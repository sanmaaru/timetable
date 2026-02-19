import {privateAxiosClient} from "./axiosClient";
import {Class, Student} from "../types/class";
import {Schedule} from "../types/schedule";

const parseStudents = (students: any): Student[] => {
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

const parseClass = (clazz: any): Class => {
    return {
        classId: clazz.class_id,
        subject: clazz.subject,
        teacher: clazz.teacher,
        division: clazz.division,
        room: clazz.room,
        classmates: parseStudents(clazz.classmates)
    }
}

const parseTimetableData = (timetable: any) => {
    const classes: Class[] = [];
    const schedules: Schedule[] = [];
    timetable.forEach((entry: any) => {
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
                    day: day,
                    period_from: start,
                    period_to: prev,
                    clazz: newClass
                });
                start = current;
                prev = current;
            }

            schedules.push({
                day: day,
                period_from: start,
                period_to: prev,
                clazz: newClass
            })
        })
    })

    return {classes, schedules};
}

export const fetchTimetable = async () => {
    const response = await privateAxiosClient.get('/timetable', {});

    const {name, timetable} = response.data.data
    const {classes, schedules} = parseTimetableData(timetable);

    return { name, classes, schedules }
}

export const fetchClass = async (classId: string) => {
    const response = await privateAxiosClient.get(`/class/${classId}`, {});

    const classInfo = response.data.data

}