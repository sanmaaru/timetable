import {privateAxiosClient} from "./axiosClient";
import {Class, Student} from "../types/class";
import {Day, Period, Schedule} from "../types/schedule";
import {BaseResponseDto} from "./dto/response.dto";
import {ClassDto, TimetableDto} from "./dto/timetable.dto";
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

const parseClass = (clazz: ClassDto): Class => {
    return {
        classId: clazz.class_id,
        subject: clazz.subject,
        teacher: clazz.teacher,
        division: clazz.division,
        room: clazz.room,
        classmates: parseStudents(clazz.classmates)
    }
}

const parseTimetableData = (timetable: TimetableDto) => {
    const classes: Class[] = [];
    const schedules: Schedule[] = [];
    timetable.timetable.forEach((entry: any) => {
        const newClass = parseClass(entry);
        classes.push(newClass);

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
                    clazz: newClass
                });
                start = current;
                prev = current;
            }

            schedules.push({
                day: day as Day,
                period_from: start as Period,
                period_to: prev as Period,
                clazz: newClass
            })
        })
    })

    const name = timetable.name;
    return { name, classes, schedules};
}

export const fetchTimetable = () => {
    return withApi(async () => {
        const response = await privateAxiosClient.get<BaseResponseDto<TimetableDto>>('/timetable', {});

        const { name, classes, schedules} = parseTimetableData(response.data.data);
        return { name, classes, schedules }
    })

}