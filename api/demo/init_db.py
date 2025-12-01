from database import init_db, conn
from upload import *
from pathlib import Path

init_db()

resources = Path.cwd() / 'resources'

enrollment = resources / 'enrollment.xlsx'
lecture = resources / 'lecture.xlsx'
period = resources / 'period.xlsx'

session = next(conn())

enrollments, periods = parse_enrollments(str(enrollment))
lectures = parse_lectures(str(lecture))
multi_tch_periods = parse_periods(str(period))
periods = unify_periods(periods, multi_tch_periods, lectures)

upload_teachers(lectures, session)
upload_students(enrollments, session)

upload_lectures(lectures, session)
upload_periods(periods, session)
upload_enrollments(enrollments, session)

session.close()