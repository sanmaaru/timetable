import json

from template import parse_periods, unify_periods, parse_lectures, parse_division, parse_enrollments, parse_subjects, \
    parse_common_timetable, parse_student_list
from util import generate_identity_id


def _create_lecture_object(
        subject: str,
        teacher: str,
        room: str,
        division: int
):
    return {
        'subject': subject,
        'teacher': teacher,
        'room': room,
        'division': division,
    }


def _create_period_object(
        subject: str,
        division: int,
        teacher: str,
        day: int,
        period: int,
):
    return {
        'lecture': {
            'subject': subject,
            'division': division,
            'teacher': teacher
        },
        'period': {
            'day': day,
            'period': period,
        }
    }


## *_path: excel file, *_data_path: json file
def organize_optional_lecture(
        lecture_path: str,
        enrollment_path: str,
        output_path: str
):
    lectures = parse_lectures(lecture_path)
    subject_division_map = parse_division(enrollment_path)
    subject_lecture_map = {}
    for lecture in lectures:
        if lecture.subject not in subject_lecture_map:
            subject_lecture_map[lecture.subject] = []

        subject_lecture_map[lecture.subject].append(lecture)

    lecture_data = []
    for subject, division in subject_division_map.items():
        for div in range(1, division + 1):
            for lec in subject_lecture_map[subject]:
                teacher = lec.teacher.split(',')[0].strip()
                lecture_data.append(_create_lecture_object(
                    subject,
                    teacher,
                    lec.room,
                    div
                ))

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(lecture_data, f, ensure_ascii=False, indent=4)


def organize_periods(
        period_path: str,
        lecture_path: str,
        enrollment_path: str,
        output_path: str
):
    multi_tch_period = parse_periods(period_path)
    periods = parse_periods(enrollment_path)
    lectures = parse_lectures(lecture_path)

    periods = unify_periods(periods, multi_tch_period, lectures)

    period_data = []
    for period in periods:
        teacher = period.teacher.split(",")[0].strip()
        period_data.append(_create_period_object(
            period.subject,
            period.division,
            teacher,
            period.day,
            period.period
        ))

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(period_data, f, ensure_ascii=False, indent=4)


def organize_enrollments(
        enrollment_path: str,
        identity_id_path: str,
        target_generation: int,
        output_path: str
):
    with open(identity_id_path, 'r', encoding='utf-8') as f:
        identity_ids = json.load(f)

    enrollments = parse_enrollments(enrollment_path)
    enrollment_data = []
    for enrollment in enrollments:
        lectures = []
        for lecture in enrollment.lectures:
            lectures.append({
                'subject': lecture[0],
                'division': lecture[1],
            })

        name = enrollment.name
        identity_id = identity_ids[str(target_generation)][name]
        if isinstance(identity_id, list):
            print(f'Multiple student found for(Enrollment): {name}, {identity_id}')

        enrollment_data.append({
            'lectures': lectures,
            'student': {
                'identity_id': identity_id,
                'name': name,
                'credit': enrollment.credit
            }
        })

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enrollment_data, f, ensure_ascii=False, indent=4)


def organize_subjects(
        subject_path: str,
        output_path: str
):
    subjects = parse_subjects(subject_path)
    subject_data = set([s.subject for s in subjects])

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(list(subject_data), f, ensure_ascii=False, indent=4)


def organize_common_timetable(
        common_timetable_path: str,
        alias_path: str,
        lecture_output_path: str,
        period_output_path: str,
):
    with open(alias_path, 'r', encoding='utf-8') as f:
        alias = json.load(f)

    common_timetable = parse_common_timetable(common_timetable_path, alias)
    lecture_data = []
    period_data = []
    for key, timetable in common_timetable.items():
        for lecture in timetable.lectures:
            teacher = lecture.teacher.split(',')[0].strip()
            lecture_data.append(_create_lecture_object(
                lecture.subject,
                teacher,
                lecture.room,
                key[1],
            ))

        for period in timetable.periods:
            teacher = period.teacher.split(',')[0].strip()
            period_data.append(_create_period_object(
              period.subject,
              period.division,
              teacher,
              period.day,
              period.period
            ))

    with open(period_output_path, 'w', encoding='utf-8') as f:
        json.dump(period_data, f, ensure_ascii=False, indent=4)

    with open(lecture_output_path, 'w', encoding='utf-8') as f:
        json.dump(lecture_data, f, ensure_ascii=False, indent=4)


def organize_common_timetable_enrollment(
        lecture_data_path: str,
        student_data_path: str,
        target_generation: int,
        credit: int,
        output_path: str,
):
    with open(lecture_data_path, 'r', encoding='utf-8') as f:
        lecture_data = json.load(f)

    with open(student_data_path, 'r', encoding='utf-8') as f:
        student_data = json.load(f)

    division_lecture_map = {}
    division_student_map = {}
    for lecture in lecture_data:
        division = lecture['division']
        if division not in division_lecture_map:
            division_lecture_map[division] = []

        division_lecture_map[division].append({
            'subject': lecture['subject'],
            'division': lecture['division'],
        })

    for data in student_data:
        if data['generation'] != target_generation:
            continue

        division = data['clazz']
        if division not in division_student_map:
            division_student_map[division] = []

        name = data['name']
        identity_id = data['identity_id']
        if isinstance(identity_id, list):
            print(f'Multiple student found for(Enrollment): {name}, {identity_id}')

        division_student_map[division].append({
            'identity_id': identity_id,
            'name': name,
            'credit': credit,
        })

    enrollments = []
    for division, lectures in division_lecture_map.items():
        for student in division_student_map[division]:
            enrollments.append({
                'lectures': lectures,
                'student': student
            })

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enrollments, f, ensure_ascii=False, indent=4)


def organize_teachers(
        lecture_data_paths: list[str],
        identity_id_path: str,
        output_path: str
):
    ## TODO :: Manual process required for duplicate teacher names
    teacher_names = set([])
    for lecture_path in lecture_data_paths:
        with open(lecture_path, 'r', encoding='utf-8') as f:
            lectures = json.load(f)
            for lecture in lectures:
                for teacher_name in lecture['teacher'].split(','):
                    teacher_names.add(teacher_name.strip())

    with open(identity_id_path, 'r', encoding='utf-8') as f:
        identity_ids = json.load(f)['0']

    output_data = []
    for teacher in teacher_names:
        output_data.append({
            'name': teacher,
            'identity_id': identity_ids[teacher]
        })


    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)


def organize_students(
        student_path: str,
        identity_id_path: str,
        output_path: str,
):
    students = parse_student_list(student_path)
    with open(identity_id_path, 'r', encoding='utf-8') as f:
        identity_ids = json.load(f)

    student_data = []
    for student in students:
        name = student.name
        generation = student.generation
        clazz = student.clazz
        number = student.number
        identity_id = identity_ids[str(generation)][name]
        if isinstance(identity_id, list):
            print(f'multiple identity id found(Student): {name}: {identity_id}')

        student_data.append({
            'name': name,
            'generation': generation,
            'clazz': clazz,
            'number': number,
            'identity_id': identity_id
        })

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(student_data, f, ensure_ascii=False, indent=4)


def create_identity_id_map(
        student_path: str,
        lecture_data_paths: list[str],
        output_path: str
):
    # Create students' identity id map
    students = parse_student_list(student_path)
    gen_name_count = {}
    for student in students:
        name = student.name
        gen = student.generation
        if gen not in gen_name_count:
            gen_name_count[gen] = {}

        if name not in gen_name_count[gen]:
            gen_name_count[gen][name] = 0
        else:
            gen_name_count[gen][name] += 1

    output_data = {}
    for gen, name_counts in gen_name_count.items():
        if gen not in output_data:
            output_data[gen] = {}

        for name, count in name_counts.items():
            if count == 0:
                output_data[gen][name] = generate_identity_id(0, gen, name)
                continue

            output_data[gen][name] = [generate_identity_id(num, gen, name) for num in range(count+1)]
            print('multiple students found: ' + name)

    # Generate teachers' identity id map
    ## TODO :: Manual process required for duplicate teacher names
    teacher_names = set([])
    for lecture_path in lecture_data_paths:
        with open(lecture_path, 'r', encoding='utf-8') as f:
            lectures = json.load(f)
            for lecture in lectures:
                for teacher_name in lecture['teacher'].split(','):
                    teacher_names.add(teacher_name.strip())

    output_data[0] = {}
    for teacher in teacher_names:
        output_data[0][teacher] = generate_identity_id(0, 0, teacher)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)