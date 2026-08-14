import structlog
from sqlalchemy import delete

from app.core.types import Role
from app.crud.auth import *
from app.crud.timetable import crud_subject, \
    crud_lecture, crud_period, crud_enrollment
from app.exceptions.upload import DraftNotFoundError
from app.model.timetable import Semester
from app.model.upload import register_transition, UploadDraft, OVERWRITE_TRANSITIONS, REWRITE_TRANSITIONS
from app.schema.upload import LectureInfoSchema, PeriodInfoSchema, EnrollmentInfoSchema, StudentInfoSchema, \
    TeacherInfoSchema, \
    PeriodSchema, EnrollmentUserInfoSchema
from app.servcie.upload import UploadPayloadService

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
    subjects = UploadPayloadService.prepare_subject_payloads(subjects)

    await crud_subject.insert_by_semester(subjects, semester_id, session, ignore_duplicates=True)


@register_transition(action_name="UPLOAD_SUBJECT", type='rewrite')
async def rewrite_subjects_transition(subjects: list[str], semester_id: ulid.ULID, session: AsyncSession):
    # Delete All subjects in the semester
    await crud_subject.delete_by_semester(semester_id, session)

    # Insert bulk of subject into the database
    subjects = UploadPayloadService.prepare_subject_payloads(subjects)

    await crud_subject.insert_by_semester(subjects, semester_id, session)



@register_transition(action_name='UPLOAD_LECTURE', type='overwrite')
async def overwrite_lectures_transition(lectures: list[LectureInfoSchema], semester_id: ulid.ULID, session: AsyncSession):
    lecture_data = await UploadPayloadService.prepare_lecture_payloads(lectures, semester_id, session)

    await crud_lecture.insert_by_semester(
        semester_id, lecture_data, session, update_duplicate_keys=['room']
    )


@register_transition(action_name='UPLOAD_LECTURE', type='rewrite')
async def rewrite_lectures_transition(lectures: list[LectureInfoSchema], semester_id: ulid.ULID, session: AsyncSession):
    # Delete all lectures in lecture database
    await crud_lecture.delete_by_semester(semester_id, session)

    lecture_data = await UploadPayloadService.prepare_lecture_payloads(lectures, semester_id, session)

    await crud_lecture.insert_by_semester(
        semester_id, lecture_data, session
    )


@register_transition(action_name='UPLOAD_PERIOD', type='overwrite')
async def overwrite_periods_transition(periods: list[PeriodInfoSchema], semester_id: ulid.ULID, session: AsyncSession):
    period_data = await UploadPayloadService.prepare_period_payloads(periods, semester_id, session)

    # Upload period data with ignoring duplicates
    await crud_period.insert_by_semester(
        semester_id, period_data, session, update_duplicate_keys=['period', 'day']
    )


@register_transition(action_name='UPLOAD_PERIOD', type='rewrite')
async def rewrite_periods_transition(periods: list[PeriodInfoSchema], semester_id: ulid.ULID, session: AsyncSession):
    # Clear periods on the database
    await crud_period.delete_by_semester(semester_id, session)

    # Upload periods
    period_data = await UploadPayloadService.prepare_period_payloads(periods, semester_id, session)
    await crud_period.insert_by_semester(semester_id, period_data, session)


@register_transition(action_name='UPLOAD_ENROLLMENT', type='overwrite')
async def overwrite_enrollment_transition(enrollments: list[EnrollmentInfoSchema], semester_id: ulid.ULID, session: AsyncSession):
    enrollment_data, student_data = await UploadPayloadService.prepare_enrollment_payloads(enrollments, semester_id, session)

    # Upload enrollment info on the database with overwriting duplicates
    await crud_enrollment.insert_by_semester(semester_id, enrollment_data, session, ignore_duplicates=True)

    # Update student credit info
    await crud_user_info.bulk_update(student_data, session)


@register_transition(action_name='UPLOAD_ENROLLMENT', type='rewrite')
async def rewrite_enrollment_transition(enrollments: list[EnrollmentInfoSchema], semester_id: ulid.ULID, session: AsyncSession):
    # Clear database
    await crud_enrollment.delete_by_semester(semester_id, session)

    enrollment_data, student_data = await UploadPayloadService.prepare_enrollment_payloads(enrollments, semester_id, session)
    # Upload enrollment
    await crud_enrollment.insert_by_semester(semester_id, enrollment_data, session, ignore_duplicates=True)

    # Update student credit info
    await crud_user_info.bulk_update(student_data, session)


@register_transition(action_name='UPLOAD_STUDENTS', type='overwrite')
async def overwrite_students_transition(students: list[StudentInfoSchema], semester_id: ulid.ULID, session: AsyncSession):
    student_data = UploadPayloadService.prepare_student_payloads(students, semester_id)
    identity_ids = [s.identity_id for s in students]
    id_tkn_data = await UploadPayloadService.prepare_identify_token_payloads(identity_ids, session)

    # Upload student info with ignoring duplicates
    await crud_user_info.insert_by_semester(
        semester_id, student_data, session, on_duplicate_key=['name', 'role', 'clazz', 'number', 'generation']
    )

    # Update identify token
    await crud_identify_token.insert(id_tkn_data, session)


@register_transition(action_name='UPLOAD_STUDENTS', type='rewrite')
async def rewrite_students_transition(students: list[StudentInfoSchema], semester_id: ulid.ULID, session: AsyncSession):
    # Clear identity token related to removing user info
    student_data = await crud_user_info.list_by_semester(
        semester_id, session, condition=[UserInfo.role == Role.STUDENT]
    )
    identity_ids = [u.identity_id for u in student_data]

    await crud_identify_token.delete(
        session, condition=[
            IdentifyToken.identity_id.in_(identity_ids),
            IdentifyToken.expired == False
        ]
    )

    # Clear Uploaded Student data
    await crud_user_info.delete_by_semester(semester_id, session, condition=[UserInfo.role == Role.STUDENT])

    # Upload Student data and identify token
    student_data = UploadPayloadService.prepare_student_payloads(students, semester_id)
    await crud_user_info.insert_by_semester(semester_id, student_data, session)

    identity_ids = [s.identity_id for s in students]
    id_tkn_data = await UploadPayloadService.prepare_identify_token_payloads(identity_ids, session)
    await crud_identify_token.insert(id_tkn_data, session)


@register_transition(action_name='UPLOAD_TEACHERS', type='overwrite')
async def overwrite_teachers_transition(teachers: list[TeacherInfoSchema], semester_id: ulid.ULID, session: AsyncSession):
    teacher_data = UploadPayloadService.prepare_teacher_payloads(teachers, semester_id)
    identity_ids = [t.identity_id for t in teachers]
    id_tkn_data = await UploadPayloadService.prepare_identify_token_payloads(identity_ids, session)

    await crud_user_info.insert_by_semester(
        semester_id, teacher_data, session, on_duplicate_key=['name', 'role']
    )

    await crud_identify_token.insert(id_tkn_data, session)


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