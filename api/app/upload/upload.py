from .template import *
from app.core.database import *
from pathlib import Path

session = next(conn())

resources = Path(__file__).parent / 'resources'

enrollments_path = resources / 'enrollment.xlsx'
lecture_path = resources / 'lecture.xlsx'
period_path = resources / 'period.xlsx'

enrollments, periods = parse_enrollments(str(enrollments_path))
lectures = parse_lectures(str(lecture_path))
multi_tch_periods = parse_periods(str(period_path))
periods = unify_periods(periods, multi_tch_periods, lectures)

upload_teachers(lectures, session)
upload_students(enrollments, session)
upload_lectures(lectures, session)
upload_periods(periods, session)
upload_enrollments(enrollments, session)

create_user_info(
    session, 
    name='administrator', 
    role=role.ADMINISTRATOR
)

session.commit()