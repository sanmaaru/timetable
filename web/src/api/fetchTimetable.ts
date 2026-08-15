import {privateAxiosClient} from "./axiosClient";
import {Lecture, Student} from "../types/class";
import {Day, Period, Schedule} from "../types/schedule";
import {BaseResponseDto} from "./dto/response.dto";
import {LectureDto, TimetableDto} from "./dto/timetable.dto";
import {UserInfoDto} from "./dto/user.dto";
import {withApi} from "./api";



const parseStudents = (students: UserInfoDto[]): Student[] => {
    return students.map((entry: any): Student => {
        return {
            studentId: entry.user_info_id,
            name: entry.name,
            clazz: entry.clazz,
            number: entry.number,
            generation: entry.generation,
        }
    })
}

const parseClass = (lecture: LectureDto): Lecture => {
    return {
        lectureId: lecture.lecture_id,
        subject: lecture.subject,
        teacher: lecture.teacher,
        division: lecture.division,
        room: lecture.room,
        classmates: parseStudents(lecture.classmates)
    }
}

const parseTimetableData = (timetable: TimetableDto) => {
    const lectures: Lecture[] = [];
    const schedules: Schedule[] = [];
    timetable.timetable.forEach((entry: any) => {
        const newLecture = parseClass(entry);
        lectures.push(newLecture);

        const periodsByDay: { [key: string]: number[] } = {};

        entry.periods.forEach((period: any) => {
            if (!periodsByDay[period.day])
                periodsByDay[period.day] = [];

            periodsByDay[period.day].push(period.period);
        })

        Object.keys(periodsByDay).forEach(day => {
            const sortedPeriod = periodsByDay[day].sort((a, b) => a - b);

            let start = sortedPeriod[0];
            let prev = sortedPeriod[0];

            for (let i = 1; i < sortedPeriod.length; i++) {
                const current = sortedPeriod[i];

                if (current - prev == 1) {
                    prev = current
                    continue;
                }

                schedules.push({
                    day: day as Day,
                    period_from: start as Period,
                    period_to: prev as Period,
                    lecture: newLecture
                });
                start = current;
                prev = current;
            }

            schedules.push({
                day: day as Day,
                period_from: start as Period,
                period_to: prev as Period,
                lecture: newLecture
            })
        })
    })

    const name = timetable.name;
    return { name, lectures, schedules };
}

export const fetchTimetable = () => {
    return withApi(async () => {
        const response = await privateAxiosClient.get<BaseResponseDto<TimetableDto>>('/timetable', {});

        const { name, lectures, schedules } = parseTimetableData(response.data.data);
        return { name, lectures, schedules }
    })

}