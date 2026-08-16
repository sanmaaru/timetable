from pathlib import Path

from data_collector import organize_common_timetable, organize_optional_lecture, organize_periods, organize_subjects
from template import ClassCell

resource_dir = Path(__file__).parent / 'resources'
output_dir = Path(__file__).parent / 'output'

enrollment_path = resource_dir / 'enrollment.xlsx'
lecture_path = resource_dir / 'lecture.xlsx'
period_path = resource_dir / 'period.xlsx'
subject_path = resource_dir / 'subject.xlsx'
timetable_1_path = resource_dir / 'common_timetable_1.xlsx'
alias_1_path = resource_dir / 'alias_1.json'
timetable_2_path = resource_dir / 'common_timetable_2.xlsx'
alias_2_path = resource_dir / 'alias_2.json'
timetable_3_path = resource_dir / 'common_timetable_3.xlsx'
alias_3_path = resource_dir / 'alias_3.json'
student_path = resource_dir / 'student.xlsx'

# organize_periods(
#     str(period_path),
#     str(lecture_path),
#     str(enrollment_path),
#     str(output_dir / 'period.json')
# )

# cell = ClassCell()
# print(cell.match(content='체육Ⅳ 4반 (최민수, 1시간)'))

organize_common_timetable(
    str(timetable_2_path),
    str(alias_2_path),
    str(output_dir / 'lecture_2.json'),
    str(output_dir / 'period_2.json')
)