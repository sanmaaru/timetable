import structlog
from sqlalchemy import tuple_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from ulid.ulid import ULID

from app.core.types import Role
from app.crud.auth import crud_user_info, crud_identify_token
from app.crud.timetable import crud_subject, crud_lecture
from app.exceptions.upload import UploadError
from app.model.auth import UserInfo, IdentifyToken
from app.model.timetable import Subject, Lecture
from app.schema.upload import LectureInfoSchema, PeriodInfoSchema, EnrollmentInfoSchema, StudentInfoSchema, \
    TeacherInfoSchema


logger = structlog.get_logger()
class UploadPayloadService:

    @staticmethod
    def prepare_subject_payloads(subjects: list[str]):
        return [{
            'name': subject,
        } for subject in subjects]


    @staticmethod
    async def prepare_lecture_payloads(
        lectures: list[LectureInfoSchema],
        semester_id: ULID,
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
        teacher_data = await crud_user_info.list_by_semester(
            semester_id, session,
            condition = [
                UserInfo.name.in_(teacher_names),
                UserInfo.role == Role.TEACHER,
            ]
        )
        for teacher in teacher_data:
            teachers_map[teacher.name.strip()] = teacher.user_info_id

        # Query subjects of the lectures
        subject_map = {
            s.name: s.subject_id
            for s in await crud_subject.list_by_semester(semester_id, session)
        } # { subject : subject id }

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
                'subject_id': subject_map[lecture.subject],
                'teacher_info_id': teachers_map[teacher_name],
                'division': lecture.division,
                'room': lecture.room,
            })

        return lecture_data

    @staticmethod
    async def prepare_period_payloads(periods: list[PeriodInfoSchema], semester_id: ULID, session: AsyncSession):
        # Query lectures of the periods
        lectures = [(p.lecture.subject, p.lecture.teacher,  p.lecture.division) for p in periods]
        lecture_data = await crud_lecture.list_with_relation(
            semester_id, session, condition=[
                tuple_(
                    Subject.name,
                    UserInfo.name,
                    Lecture.division,
                ).in_(lectures),
            ]
        )
        lecture_map = {
            (l.subject.name, l.teacher_info.name, l.division) : l.lecture_id for l in lecture_data
        }

        # Build payloads of uploading data
        period_data = []
        for period in periods:
            lec = period.lecture
            lecture_key = (lec.subject, lec.teacher, lec.division)

            if lecture_key not in lecture_map:
                raise UploadError('Cannot find lecture: ' + str(lec))

            period_data.append({
                'lecture_id': lecture_map[lecture_key],
                'period': period.period.period,
                'day': period.period.day,
            })

        return period_data


    @staticmethod
    async def prepare_enrollment_payloads(enrollments: list[EnrollmentInfoSchema], semester_id: ULID, session: AsyncSession):
        # Query lectures of lecture reference with considering split teaching
        lectures = [(l.subject, l.division) for e in enrollments for l in e.lectures]
        lecture_data = await crud_lecture.list_with_relation(
            semester_id, session, condition=[
                tuple_(
                    Subject.name,
                    Lecture.division,
                ).in_(lectures),
        ])

        lecture_map = {}
        for l in lecture_data:
            lecture_key = (l.subject.name, l.division)
            if lecture_key not in lecture_map:
                lecture_map[lecture_key] = set([])

            lecture_map[lecture_key].add(l.lecture_id)

        # Query students in the enrollment list
        students = [(e.student.name, e.student.identity_id) for e in enrollments]
        student_data = await crud_user_info.list_by_semester(
            semester_id, session, condition=[
                tuple_(
                    UserInfo.name,
                    UserInfo.identity_id
                ).in_(students),
                or_(
                    UserInfo.role == Role.STUDENT,
                    UserInfo.role == Role.ADMINISTRATOR
                )
            ]
        )
        student_map = {
            (s.name, s.identity_id): s.user_info_id
            for s in student_data
        }

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


    @staticmethod
    def prepare_student_payloads(students: list[StudentInfoSchema], semester_id: ULID):
        student_data = [{
            'name': s.name,
            'role': Role.STUDENT,
            'clazz': s.clazz,
            'number': s.number,
            'generation': s.generation,
            'identity_id': s.identity_id,
        } for s in students]

        return student_data


    @staticmethod
    async def prepare_identify_token_payloads(
            identity_ids: list[str],
            session: AsyncSession,
    ):
        # Prepare Identify Token data for new user
        id_token_data = await crud_identify_token.list(session, condition=[IdentifyToken.identity_id.in_(identity_ids)])
        existing_identify_tokens = set([tkn.identity_id for tkn in id_token_data])

        # Does not create identify token for already registered user exists
        identify_token_data = []
        for identity_id in identity_ids:
            if identity_id in existing_identify_tokens:
                continue

            identify_token_data.append({
                'identity_id': identity_id,
            })

        return identify_token_data


    @staticmethod
    def prepare_teacher_payloads(teachers: list[TeacherInfoSchema], semester_id: ULID):
        # Prepare teacher info data
        teacher_data = [{
            'name': t.name,
            'role': Role.TEACHER,
            'identity_id': t.identity_id,
        } for t in teachers]

        return teacher_data
