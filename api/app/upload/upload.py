import structlog

from app.auth.crud import *
from .exceptions import UploadError
from .template import *
from ..timetable.model import Class, Subject, Lecture, Enrollment, Period

logger = structlog.get_logger()
async def bulk_create_students(session: AsyncSession, user_info_datas: list[UserInfoData]):
    if not user_info_datas:
        return 0

    generations = set([d.generation for d in user_info_datas])

    stmt = select(UserInfo).where(
        UserInfo.role.op('&')(Role.STUDENT) != 0,
        UserInfo.generation.in_(generations)
    )
    existing_users = (await session.execute(stmt)).scalars().all()
    existing_keys = { (user.generation, user.clazz, user.number, user.name) for user in existing_users }

    unique_users = { (user.generation, user.clazz, user.number, user.name): user for user in user_info_datas}

    new_users = []
    for key, user in unique_users.items():
        if key not in existing_keys:
            user_info = UserInfo(
                name=user.name,
                role=Role.STUDENT,
                generation=user.generation,
                clazz=user.clazz,
                number=user.number,
                credit=user.credit
            )
            new_users.append(user_info)

    if not new_users:
        return 0

    session.add_all(new_users)
    await session.flush()

    new_tokens = [
        IdentifyToken(user_info_id=user_info.user_info_id) for user_info in new_users
    ]
    session.add_all(new_tokens)

    return len(new_users)


async def bulk_create_teachers(session: AsyncSession, user_info_datas: list[UserInfoData]):
    if not user_info_datas:
        return 0

    stmt = select(UserInfo).where(
        UserInfo.role.op('&')(Role.TEACHER) != 0
    )
    existing_users = (await session.execute(stmt)).scalars().all()
    existing_keys = {user.name for user in existing_users}

    unique_users = {user.name: user for user in user_info_datas}

    new_users = []
    for key, user in unique_users.items():
        if key not in existing_keys:
            user_info = UserInfo(
                name=user.name,
                role=Role.TEACHER,
            )
            new_users.append(user_info)

    if not new_users:
        return 0

    session.add_all(new_users)
    await session.flush()

    new_tokens = [
        IdentifyToken(user_info_id=user_info.user_info_id) for user_info in new_users
    ]
    session.add_all(new_tokens)

    return len(new_users)

async def upload_students(students: list[EnrollmentInfo], session: AsyncSession):
    students = [UserInfoData(s.name, s.generation, s.clazz, s.number, s.credit) for s in students]

    len_users = await bulk_create_students(session, students)
    await session.commit()
    logger.info(f'{len_users} students uploaded')


async def upload_teachers(teachers: list[LectureInfo], session: AsyncSession):
    teacher_names = set()

    for lecture in teachers:
        names = map(str.strip, lecture.teacher.split(","))
        teacher_names.update(names)

    teachers = [UserInfoData(t.name) for t in teacher_names]
    len_teachers = await bulk_create_teachers(session, teachers)
    await session.commit()
    logger.info(f'{len_teachers} teacher uploaded')


async def upload_enrollments(students: list[EnrollmentInfo], session: AsyncSession):
    stmt = select(UserInfo).where(UserInfo.role.op('&')(Role.STUDENT) != 0)
    all_students = (await session.execute(stmt)).scalars().all()
    student_map = { (s.generation, s.clazz, s.number): s.user_info_id for s in all_students }

    stmt = select(Class).join(Class.lecture).join(Lecture.subject).options(
        joinedload(Class.lecture).joinedload(Lecture.subject)
    )
    all_classes = (await session.execute(stmt)).scalars().all()
    class_map = dict()
    for c in all_classes:
        key = (c.lecture.subject.name, c.division)
        if key not in class_map:
            class_map[key] = []

        class_map[key].append(c.class_id)

    new_objects = []
    for student in students:
        key = (student.generation, student.clazz, student.number)

        if key not in student_map:
            raise UploadError('Cannot find student', student=student)

        student_id = student_map[key]
        for subject_name, division in student.subjects:
            key = (subject_name, division)
            if key not in class_map:
                raise UploadError('Cannot find class', key=key)

            class_ids = class_map[key]
            for class_id in class_ids:
                enrollment = Enrollment(class_id=class_id, user_info_id=student_id)
                new_objects.append(enrollment)

    session.add_all(new_objects)
    await session.commit()

async def upload_lectures(lectures: list[LectureInfo], session: AsyncSession):
    unique_subjects = { l.subject for l in lectures }

    # query subjects
    stmt = select(Subject).where(Subject.name.in_(unique_subjects))
    subjects = (await session.execute(stmt)).scalars().all()
    subject_map = { s.name: s.subject_id for s in subjects }

    # create subject if not exists
    new_subjects = []
    for name in unique_subjects:
        if name not in subject_map.keys():
            subject = Subject(name=name)
            new_subjects.append(subject)
            subject_map[name] = subject.subject_id

    session.add_all(new_subjects)
    await session.flush()

    teacher_names = set()
    for l in lectures:
        teacher_names.update(map(str.strip, l.teacher.split(",")))

    # === query teachers ===
    stmt = select(UserInfo).where(
        UserInfo.name.in_(teacher_names),
        UserInfo.role.op('&')(Role.TEACHER) != 0)
    teachers = (await session.execute(stmt)).scalars().all()
    teacher_map = { t.name : t.user_info_id for t in teachers }

    stmt = (select(Lecture)
            .join(Lecture.subject)
            .where(Lecture.subject_id.in_(subject_map.values()))
            .options(joinedload(Lecture.subject), joinedload(Lecture.teacher_info)))
    existing_lectures = (await session.execute(stmt)).scalars().all()
    existing_lecture_keys = set([(l.subject.name, l.teacher.name, l.room) for l in existing_lectures])

    # === add new lectures ===
    new_objects = []
    for l in lectures:
        teacher_name = l.teacher.split(",")[0].strip()
        if teacher_name not in teacher_map.keys():
            raise UploadError('cannot find teacher', lecture=l)

        key = (l.subject, teacher_name, l.room)
        if key in existing_lecture_keys:
            continue

        subject = subject_map[l.subject]
        teacher = teacher_map[teacher_name]
        lecture = Lecture(subject_id=subject, teacher_info_id=teacher, room=l.room)
        new_objects.append(lecture)

    session.add_all(new_objects)
    await session.commit()


async def upload_periods(periods: list[PeriodInfo], session: AsyncSession):
    # === query subjects ===
    subjects = set([p.subject for p in periods])
    stmt = select(Subject).where(Subject.name.in_(subjects))
    subjects = (await session.execute(stmt)).scalars().all()
    subject_map = { s.name: s.subject_id for s in subjects }

    # === query teachers ===
    teacher_names = set()
    for p in periods:
        teacher_names.update(map(str.strip, p.teacher.split(",")))
    stmt = select(UserInfo).where(UserInfo.name.in_(teacher_names),
                                  UserInfo.role.op('&')(Role.TEACHER) != 0)
    teachers = (await session.execute(stmt)).scalars().all()
    teacher_map = { t.name: t.user_info_id for t in teachers }

    stmt = (select(Lecture)
            .join(Lecture.subject)
            .join(Lecture.teacher_info)
            .where(Lecture.subject.in_(subjects),
                   Lecture.teacher_info_id.in_(teacher_map.values()))
            .options(joinedload(Lecture.subject),
                     joinedload(Lecture.teacher_info)))
    lectures = (await session.execute(stmt)).scalars().all()
    lecture_map = { (l.subject.name, l.teacher.name): l.lecture_id for l in lectures }

    # === create classe ===
    stmt = select(Class).where(Class.lecture_id.in_(lecture_map.values()))
    classes = (await session.execute(stmt)).scalars().all()

    class_map = { (c.lecture_id, c.division): c for c in classes }


    new_classes = []
    new_periods = []
    for p in periods:
        teacher_name = p.teacher.split(',')[0].strip()
        lecture_id = lecture_map.get((p.subject, teacher_name))

        if not lecture_id:
            raise UploadError(f'too many lectures', period=p)

        class_key = (lecture_id, p.division)
        clazz = class_map.get(class_key)
        if clazz is None:
            clazz = Class(lecture_id=lecture_id, division=p.division)
            new_classes.append(clazz)
            class_map[class_key] = clazz

        period = Period(clazz=clazz, period=p.period, day=p.day)
        new_periods.append(period)


    session.add_all(new_classes)
    session.add_all(new_periods)
    await session.commit()
