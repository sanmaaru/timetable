from pathlib import Path

from data_collector import organize_enrollments, organize_periods, organize_optional_lecture, organize_subjects, \
    organize_common_timetable, organize_teachers, organize_students, create_identity_id_map, \
    organize_common_timetable_enrollment

resource_dir = Path(__file__).parent / 'resources'
output_dir = Path(__file__).parent / 'output'

enrollment_path = resource_dir / 'enrollment.xlsx'
lecture_path = resource_dir / 'lecture.xlsx'
period_path = resource_dir / 'period.xlsx'
subject_path = resource_dir / 'subject.xlsx'
# timetable_1_path = resource_dir / 'common_timetable_1.xlsx'
# alias_1_path = resource_dir / 'alias_1.json'
timetable_2_path = resource_dir / 'common_timetable_2.xlsx'
alias_2_path = resource_dir / 'alias_2.json'
# timetable_3_path = resource_dir / 'common_timetable_3.xlsx'
# alias_3_path = resource_dir / 'alias_3.json'
student_path = resource_dir / 'student.xlsx'

organize_subjects(
    str(subject_path),
    str(output_dir / 'subject.json')
)

organize_optional_lecture(
    str(lecture_path),
    str(enrollment_path),
    str(output_dir / 'subject.json'),
    str(output_dir / 'lecture.json')
)

organize_periods(
    str(enrollment_path),
    str(output_dir / 'lecture.json'),
    str(output_dir / 'period.json')
)

# organize_common_timetable(
#     str(timetable_1_path),
#     str(alias_1_path),
#     str(output_dir / 'lecture_1.json'),
#     str(output_dir / 'period_1.json')
# )

organize_common_timetable(
    str(timetable_2_path),
    str(alias_2_path),
    str(output_dir / 'lecture_2.json'),
    str(output_dir / 'period_2.json')
)

create_identity_id_map(
    str(student_path),
    [
        str(output_dir / 'lecture.json'),
        str(output_dir / 'lecture_2.json'),
    ],
    str(output_dir / 'identity_id.json'),
)

# organize_common_timetable(
#     str(timetable_3_path),
#     str(alias_3_path),
#     str(output_dir / 'lecture_3.json'),
#     str(output_dir / 'period_3.json')
# )


organize_teachers(
    [
        str(output_dir / 'lecture.json'),
        str(output_dir / 'lecture_2.json'),
    ],
    str(output_dir / 'identity_id.json'),
    str(output_dir / 'teacher.json')
)


# organize_students(
#     str(student_path),
#     str(output_dir / 'identity_id.json'),
#     str(output_dir / 'student.json'),
# )
#
organize_enrollments(
    str(enrollment_path),
    str(output_dir / 'identity_id.json'),
    [41, 42],
    str(output_dir / 'enrollment.json')
)

organize_common_timetable_enrollment(
    str(output_dir / 'lecture_2.json'),
    str(output_dir / 'student.json'),
    43,
    32,
    str(output_dir / 'enrollment_2.json')
)

# organize_common_timetable_enrollment(
#     str(output_dir / 'lecture_3.json'),
#     str(output_dir / 'student.json'),
#     42,
#     30,
#     str(output_dir / 'enrollment_3.json')
# )

