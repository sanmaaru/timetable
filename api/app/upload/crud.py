import structlog
from sqlalchemy import delete, tuple_, update
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.orm import contains_eager

from app.auth.crud import *
from .exceptions import UploadError, DraftNotFoundError
from .model import register_transition, UploadDraft, OVERWRITE_TRANSITIONS, REWRITE_TRANSITIONS
from .schema import LectureInfoSchema, PeriodInfoSchema, EnrollmentInfoSchema, StudentInfoSchema, TeacherInfoSchema, \
    PeriodSchema, EnrollmentUserInfoSchema
from ..core.database import generate_ulid
from ..timetable.model import Subject, Lecture, Enrollment, Period, Semester
from ..util.common import generate_token

logger = structlog.get_logger()
async def create_upload_draft(action_name: str, payload: dict, session: AsyncSession) -> UploadDraft:
    new_draft = UploadDraft(
        action_name=action_name,
        payload=payload
    )
    session.add(new_draft)
    await session.flush()

    return new_draft

async def apply_draft(draft_id: ulid.ULID, mode: str, session: AsyncSession):
    stmt = select(UploadDraft).where(UploadDraft.draft_id == draft_id)
    draft = (await session.scalars(stmt)).one_or_none()
    if draft is None:
        raise DraftNotFoundError(message='Cannot find draft for ' + str(draft_id))

    if mode == 'overwrite':
        action = OVERWRITE_TRANSITIONS[draft.action_name]
    elif mode == 'rewrite':
        action = REWRITE_TRANSITIONS[draft.action_name]
    else:
        raise Exception('Something went wrong... Action mode must be overwrite or rewrite')

    if action is None:
        raise Exception('Something went wrong... Cannot find action')

    await action(**draft.payload, session=session)
    await session.delete(draft)


@register_transition(action_name="UPLOAD_SUBJECT", type='overwrite')
async def overwrite_subjects_transition(subjects: list[str], semester_id: ulid.ULID, session: AsyncSession):
    # Append bulk of subject into the database with ignoring duplicates
    subjects = [{
        'subject_id': generate_ulid(),
        'name': subject,
        'semester_id': semester_id
    } for subject in subjects]

    stmt = mysql_insert(Subject).values(subjects).prefix_with('IGNORE')
    await session.execute(stmt)
    await session.flush()


@register_transition(action_name="UPLOAD_SUBJECT", type='rewrite')
async def rewrite_subjects_transition(subjects: list[str], semester_id: ulid.ULID, session: AsyncSession):
    # Delete All subjects in the semester
    stmt = delete(Subject).where(Subject.semester_id == semester_id)
    await session.execute(stmt)

    # Insert bulk of subject into the database
    subjects = [{
        'subject_id': generate_ulid(),
        'name': subject,
        'semester_id': semester_id
    } for subject in subjects]

    stmt = mysql_insert(Subject).values(subjects)
    await session.execute(stmt)


async def list_subjects(semester_id: ulid.ULID, session: AsyncSession):
    # Simple function for querying subjects
    subjects = await session.scalars(select(Subject).where(Subject.semester_id == semester_id))

    return subjects


async def _prepare_lecture_payloads(
        lectures: list[LectureInfoSchema],
        semester_id: ulid.ULID,
        session: AsyncSession
):
    # Query teachers of the lectures
    teacher_names = set([])
    for lecture in lectures:
        teacher = lecture.teacher
        if teacher is None:
            raise UploadError('Teacher must not be none')

        teacher_names.add(teacher.strip())

    teachers_map = {} # { teacher name: teacher info id }
    stmt = (select(UserInfo).where(
        UserInfo.name.in_(teacher_names),
        UserInfo.role == Role.TEACHER,
        UserInfo.semester_id == semester_id)
    )
    for teacher in (await session.scalars(stmt)):
        teachers_map[teacher.name.strip()] = teacher.user_info_id

    # Query subjects of the lectures
    stmt = (select(Subject).where(
        Subject.semester_id == semester_id,
        ))
    subject_map = {s.name: s.subject_id for s in await session.scalars(stmt)} # { subject : subject id }

    # Building payloads of uploading data
    lecture_data = []
    for lecture in lectures:
        teacher_name = lecture.teacher
        if teacher_name is None:
            raise UploadError('Teacher must not be none')

        teacher_name = teacher_name.strip()

        if lecture.subject not in subject_map:
            raise UploadError('Cannot find subject: ' + lecture.subject)

        if teacher_name not in teachers_map:
            raise UploadError('Cannot find teacher: ' + teacher_name)

        lecture_data.append({
            'lecture_id': generate_ulid(),
            'subject_id': subject_map[lecture.subject],
            'teacher_info_id': teachers_map[teacher_name],
            'division': lecture.division,
            'room': lecture.room,
            'semester_id': semester_id,
        })

    return lecture_data


@register_transition(action_name='UPLOAD_LECTURE', type='overwrite')
async def overwrite_lectures_transition(lectures: list[LectureInfoSchema], semester_id: ulid.ULID, session: AsyncSession):
    lecture_data = await _prepare_lecture_payloads(lectures, semester_id, session)

    stmt = mysql_insert(Lecture).values(lecture_data)
    stmt = stmt.on_duplicate_key_update(
        room=stmt.inserted.room
    )

    await session.execute(stmt)


@register_transition(action_name='UPLOAD_LECTURE', type='rewrite')
async def rewrite_lectures_transition(lectures: list[LectureInfoSchema], semester_id: ulid.ULID, session: AsyncSession):
    # Delete all lectures in lecture database
    stmt = delete(Lecture).where(Lecture.semester_id == semester_id)
    await session.execute(stmt)

    lecture_data = await _prepare_lecture_payloads(lectures, semester_id, session)

    stmt = mysql_insert(Lecture).values(lecture_data)
    await session.execute(stmt)


async def list_lectures(semester_id: ulid.ULID, session: AsyncSession):
    # Simple function for querying lectures
    return await session.scalars(
        select(Lecture)
            .join(Lecture.subject)
            .join(Lecture.teacher_info)
            .options(
            contains_eager(Lecture.subject),
                contains_eager(Lecture.teacher_info),
            )
            .where(Lecture.semester_id == semester_id)
    )


async def _prepare_period_payloads(periods: list[PeriodInfoSchema], semester_id: ulid.ULID, session: AsyncSession):
    # Query lectures of the periods
    lectures = [(p.lecture.subject, p.lecture.teacher,  p.lecture.division) for p in periods]
    stmt = (select(Lecture)
        .join(Lecture.teacher_info)
        .join(Lecture.subject)
        .options(
            contains_eager(Lecture.teacher_info),
            contains_eager(Lecture.subject),
        )
        .where(
        tuple_(
                Subject.name,
                UserInfo.name,
                Lecture.division,
            ).in_(lectures),
            Lecture.semester_id == semester_id
        )
    )
    lecture_map = {
        (l.subject.name, l.teacher_info.name, l.division) : l.lecture_id for l in (await session.scalars(stmt))
    }

    # Build payloads of uploading data
    period_data = []
    for period in periods:
        lec = period.lecture
        lecture_key = (lec.subject, lec.teacher, lec.division)

        if lecture_key not in lecture_map:
            raise UploadError('Cannot find lecture: ' + str(lec))

        period_data.append({
            'period_id': generate_ulid(),
            'lecture_id': lecture_map[lecture_key],
            'period': period.period.period,
            'day': period.period.day,
            'semester_id': semester_id,
        })

    return period_data


@register_transition(action_name='UPLOAD_PERIOD', type='overwrite')
async def overwrite_periods_transition(periods: list[PeriodInfoSchema], semester_id: ulid.ULID, session: AsyncSession):
    period_data = await _prepare_period_payloads(periods, semester_id, session)

    # Upload period data with ignoring duplicates
    stmt = mysql_insert(Period).values(period_data)
    stmt = stmt.on_duplicate_key_update(
        period=stmt.inserted.period,
        day=stmt.inserted.day
    )

    await session.execute(stmt)


@register_transition(action_name='UPLOAD_PERIOD', type='rewrite')
async def rewrite_periods_transition(periods: list[PeriodInfoSchema], semester_id: ulid.ULID, session: AsyncSession):
    # Clear periods on the database
    stmt = delete(Period).where(Period.semester_id == semester_id)
    await session.execute(stmt)

    # Upload periods
    period_data = await _prepare_period_payloads(periods, semester_id, session)
    stmt = mysql_insert(Period).values(period_data)
    await session.execute(stmt)


async def list_periods(semester_id: ulid.ULID, session: AsyncSession):
    return await session.scalars(
        select(Period)
            .join(Period.lecture)
            .options(joinedload(Period.lecture))
            .where(Period.semester_id == semester_id)
    )


async def _prepare_enrollment_payloads(enrollments: list[EnrollmentInfoSchema], semester_id: ulid.ULID, session: AsyncSession):
    # Query lectures of lecture reference with considering split teaching
    lectures = [(l.subject, l.division) for e in enrollments for l in e.lectures]
    stmt = (select(Lecture)
        .join(Lecture.subject)
        .options(joinedload(Lecture.subject))
        .where(
            tuple_(
                Subject.name,
                Lecture.division,
            ).in_(lectures),
            Lecture.semester_id == semester_id
        )
    )
    lecture_map = {}
    for l in (await session.scalars(stmt)):
        lecture_key = (l.subject.name, l.division)
        if lecture_key not in lecture_map:
            lecture_map[lecture_key] = set([])

        lecture_map[lecture_key].add(l.lecture_id)

    # Query students in the enrollment list
    students = [(e.student.name, e.student.identity_id) for e in enrollments]
    stmt = (select(UserInfo)
        .where(
            tuple_(
                UserInfo.name,
                UserInfo.identity_id
            ).in_(students),
            UserInfo.role == Role.STUDENT,
            UserInfo.semester_id == semester_id
        )
    )
    student_map = { (s.name, s.enrollment_id): s.user_info_id for s in (await session.scalars(stmt)) }


    # Prepare data of enrollments credit data of
    enrollment_data = []
    student_data = []
    for e in enrollments:
        student_key = (e.student.name, e.student.identity_id)
        if student_key not in student_map:
            raise UploadError('Cannot find student: ' + str(student_key))

        student_data.append({
           'user_info_id': student_map[student_key],
           'credit': e.student.credit,
        })

        for l in e.lectures:
            lecture_key = (l.subject, l.division)
            if lecture_key not in lecture_map:
                raise UploadError('Cannot find lecture: ' + str(lecture_key))

            enrollment_data += [{
                'lecture_id': lec_id,
                'user_info_id': student_map[student_key],
                'semester_id': semester_id,
            } for lec_id in lecture_map[lecture_key]]

    return enrollment_data, student_data


@register_transition(action_name='UPLOAD_ENROLLMENT', type='overwrite')
async def overwrite_enrollment_transition(enrollments: list[EnrollmentInfoSchema], semester_id: ulid.ULID, session: AsyncSession):
    enrollment_data, student_data = await _prepare_enrollment_payloads(enrollments, semester_id, session)

    # Upload enrollment info on the database with overwriting duplicates
    stmt = mysql_insert(Enrollment).values(enrollment_data).prefix_with('IGNORE')
    await session.execute(stmt)

    # Update student credit info
    stmt = update(UserInfo)
    await session.execute(stmt, student_data)


@register_transition(action_name='UPLOAD_ENROLLMENT', type='rewrite')
async def rewrite_enrollment_transition(enrollments: list[EnrollmentInfoSchema], semester_id: ulid.ULID, session: AsyncSession):
    # Clear database
    stmt = delete(Enrollment).where(Enrollment.semester_id == semester_id)
    await session.execute(stmt)

    enrollment_data, student_data = await _prepare_enrollment_payloads(enrollments, semester_id, session)
    # Upload enrollment
    stmt = mysql_insert(Enrollment).values(enrollment_data)
    await session.execute(stmt)

    # Update student credit info
    stmt = update(UserInfo)
    await session.execute(stmt, student_data)


async def list_enrollments(semester_id: ulid.ULID, session: AsyncSession):
    return await session.scalars(
        select(Enrollment)
            .join(Enrollment.lecture)
            .join(Enrollment.user_info)
            .options(
                contains_eager(Enrollment.user_info),
                contains_eager(Enrollment.lecture),
            )
            .where(Enrollment.semester_id == semester_id)
    )


def _prepare_student_payloads(students: list[StudentInfoSchema], semester_id: ulid.ULID):
    student_data = [{
        'name': s.name,
        'role': Role.STUDENT,
        'clazz': s.clazz,
        'number': s.number,
        'generation': s.generation,
        'identity_id': s.identity_id,
        'semester_id': semester_id,
        'user_info_id': generate_ulid()
    } for s in students]

    return student_data


async def _prepare_identify_token_payloads(
        identity_ids: list[str],
        session: AsyncSession,
):
    # Prepare Identify Token data for new user
    stmt = select(IdentifyToken).where(IdentifyToken.identity_id.in_(identity_ids))
    existing_identify_tokens = set([tkn.identity_id for tkn in await session.scalars(stmt)])

    # Does not create identify token for already registered user exists
    identify_token_data = []
    for identity_id in identity_ids:
        if identity_id in existing_identify_tokens:
            continue

        identify_token_data.append({
            'token_id': generate_token(),
            'identity_id': identity_id,
        })

    return identify_token_data


@register_transition(action_name='UPLOAD_STUDENTS', type='overwrite')
async def overwrite_students_transition(students: list[StudentInfoSchema], semester_id: ulid.ULID, session: AsyncSession):
    student_data = _prepare_student_payloads(students, semester_id)
    identity_ids = [s.identity_id for s in students]
    id_tkn_data = await _prepare_identify_token_payloads(identity_ids, session)

    # Upload student info with ignoring duplicates
    stmt = mysql_insert(UserInfo).values(student_data)
    stmt = stmt.on_duplicate_key_update(
        name=stmt.inserted.name,
        role=stmt.inserted.role,
        clazz=stmt.inserted.clazz,
        number=stmt.inserted.number,
        generation=stmt.inserted.generation
    )

    await session.execute(stmt)

    # Update identify token
    stmt = mysql_insert(IdentifyToken).values(id_tkn_data)

    await session.execute(stmt)


@register_transition(action_name='UPLOAD_STUDENTS', type='rewrite')
async def rewrite_students_transition(students: list[StudentInfoSchema], semester_id: ulid.ULID, session: AsyncSession):
    # Clear identity token related to removing user info
    stmt = select(UserInfo).where(UserInfo.role == Role.STUDENT, UserInfo.semester_id == semester_id)
    identity_ids = [u.identity_id for u in (await session.scalars(stmt))]

    stmt = delete(IdentifyToken).where(
        IdentifyToken.identity_id.in_(identity_ids),
        IdentifyToken.expired == False,
    )
    await session.execute(stmt)

    # Clear Uploaded Student data
    stmt = delete(UserInfo).where(UserInfo.semester_id == semester_id, UserInfo.role == Role.STUDENT)
    await session.execute(stmt)

    # Upload Student data and identify token
    student_data = _prepare_student_payloads(students, semester_id)
    stmt = mysql_insert(UserInfo).values(student_data)
    await session.execute(stmt)

    identity_ids = [s.identity_id for s in students]
    id_tkn_data = await _prepare_identify_token_payloads(identity_ids, session)
    stmt = mysql_insert(IdentifyToken).values(id_tkn_data)
    await session.execute(stmt)


async def list_students(semester_id: ulid.ULID, session: AsyncSession):
    return await session.scalars(
        select(UserInfo).where(UserInfo.role == Role.STUDENT, UserInfo.semester_id == semester_id)
    )


def _prepare_teacher_payloads(teachers: list[TeacherInfoSchema], semester_id: ulid.ULID):
    # Prepare teacher info data
    teacher_data = [{
        'name': t.name,
        'role': Role.TEACHER,
        'identity_id': t.identity_id,
        'semester_id': semester_id,
        'user_info_id': generate_ulid()
    } for t in teachers]

    return teacher_data


@register_transition(action_name='UPLOAD_TEACHERS', type='overwrite')
async def overwrite_teachers_transition(teachers: list[TeacherInfoSchema], semester_id: ulid.ULID, session: AsyncSession):
    teacher_data = _prepare_teacher_payloads(teachers, semester_id)
    identity_ids = [t.identity_id for t in teachers]
    id_tkn_data = await _prepare_identify_token_payloads(identity_ids, session)

    stmt = mysql_insert(UserInfo).values(teacher_data)
    stmt = stmt.on_duplicate_key_update(
        name=stmt.inserted.name,
        role=stmt.inserted.role,
    )
    await session.execute(stmt)

    stmt = mysql_insert(IdentifyToken).values(id_tkn_data)
    await session.execute(stmt)


@register_transition(action_name='UPLOAD_TEACHERS', type='rewrite')
async def rewrite_teachers_transition(teachers: list[TeacherInfoSchema], semester_id: ulid.ULID, session: AsyncSession):
    # Delete identify tokens related to removing users
    stmt = select(UserInfo).where(UserInfo.role == Role.TEACHER, UserInfo.semester_id == semester_id)
    identity_ids = [u.identity_id for u in (await session.scalars(stmt))]

    stmt = delete(IdentifyToken).where(
        IdentifyToken.identity_id.in_(identity_ids),
        IdentifyToken.expired == False,
    )
    await session.execute(stmt)

    # Clear uploaded teacher data
    stmt = delete(UserInfo).where(UserInfo.semester_id == semester_id, UserInfo.role == Role.TEACHER)
    await session.execute(stmt)

    # Upload Student data and identify token
    teacher_data = _prepare_teacher_payloads(teachers, semester_id)
    stmt = mysql_insert(UserInfo).values(teacher_data)
    await session.execute(stmt)

    identity_ids = [t.identity_id for t in teachers]
    id_tkn_data = await _prepare_identify_token_payloads(identity_ids, session)
    stmt = mysql_insert(IdentifyToken).values(id_tkn_data)
    await session.execute(stmt)


async def list_teachers(semester_id: ulid.ULID, session: AsyncSession):
    return await session.scalars(
        select(UserInfo).where(UserInfo.semester_id == semester_id, UserInfo.role == Role.TEACHER)
    )


async def upload_default_semester(session: AsyncSession):
    # Check there exists default semester already
    stmt = select(Semester).where(Semester.code == configs.DEFAULT_SEMESTER_CODE)
    if await session.scalars(stmt):
        return

    # Upload default semester
    default_semester = Semester(code=configs.DEFAULT_SEMESTER_CODE, is_current=True)
    session.add(default_semester)
    await session.flush()


async def upload_admin_user_info(semester: Semester, session: AsyncSession) -> UserInfo:
    stmt = (select(UserInfo)
    .where(
        UserInfo.name == configs.ADMINISTRATOR_NAME,
        UserInfo.role == Role.ADMINISTRATOR,
        UserInfo.semester_id == semester.semester_id,
    ))

    user_info = (await session.execute(stmt)).scalars().one_or_none()
    if user_info is not None:
        # If an administrator account exists, it returns immediately to prevent the server from crashing at startup.
        return user_info

    user_info = UserInfo(
        name=configs.ADMINISTRATOR_NAME,
        role=Role.ADMINISTRATOR,
        identity_id=configs.ADMINISTRATOR_IDENTITY_ID,
        semester_id=semester.semester_id
    )

    session.add(user_info)
    await session.flush()

    return user_info


async def upload_admin_user(semester: Semester, session: AsyncSession):
    user_info = await upload_admin_user_info(semester, session)

    id_token = IdentifyToken(token_id=configs.ADMINISTRATOR_TOKEN, identity_id=user_info.identity_id)
    session.add(id_token)

    await session.commit()
    return user_info


async def upload_sample_timetable(semester: Semester, user: UserInfo, session: AsyncSession):
    SAMPLE_SUBJECTS = ['과목A', '과목B']
    await overwrite_subjects_transition(SAMPLE_SUBJECTS, semester.semester_id, session)

    SAMPLE_TEACHERS = [
        TeacherInfoSchema(name='선생님A', identity_id='000-aaaaaaaaaaaa'),
        TeacherInfoSchema(name='선생님B', identity_id='000-aaaaaaaabbbb'),
        TeacherInfoSchema(name='선생님C', identity_id='000-aaaaaaaacccc')
    ]
    await overwrite_teachers_transition(SAMPLE_TEACHERS, semester.semester_id, session)

    SAMPLE_LECTURES = [
        LectureInfoSchema(subject=SAMPLE_SUBJECTS[0], teacher=SAMPLE_TEACHERS[0].name, room='강의실A', division=1),
        LectureInfoSchema(subject=SAMPLE_SUBJECTS[0], teacher=SAMPLE_TEACHERS[1].name, room='강의실B', division=1),
        LectureInfoSchema(subject=SAMPLE_SUBJECTS[1], teacher=SAMPLE_TEACHERS[2].name, room='강의실C', division=3),
    ]
    await overwrite_lectures_transition(SAMPLE_LECTURES, semester.semester_id, session)

    SAMPLE_PERIODS = [
        PeriodInfoSchema(lecture=SAMPLE_LECTURES[0], period=PeriodSchema(day=0, period=1)),
        PeriodInfoSchema(lecture=SAMPLE_LECTURES[0], period=PeriodSchema(day=0, period=2)),
        PeriodInfoSchema(lecture=SAMPLE_LECTURES[1], period=PeriodSchema(day=2, period=3)),
        PeriodInfoSchema(lecture=SAMPLE_LECTURES[2], period=PeriodSchema(day=4, period=5)),
        PeriodInfoSchema(lecture=SAMPLE_LECTURES[2], period=PeriodSchema(day=4, period=6)),
    ]
    await overwrite_periods_transition(SAMPLE_PERIODS, semester.semester_id, session)

    SAMPLE_ENROLLMENTS = [
        EnrollmentInfoSchema(
            lectures=SAMPLE_LECTURES,
            student=EnrollmentUserInfoSchema(identity_id=user.identity_id, name=user.name, credit=5)
        ),
    ]
    await overwrite_enrollment_transition(SAMPLE_ENROLLMENTS, semester.semester_id, session)

    await session.flush()