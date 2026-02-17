import {privateAxiosClient} from "./axiosClient";
import {Class} from "../types/class";
import {Schedule} from "../types/schedule";

const parseTimetableData = (timetable: any) => {
    const classes: Class[] = [];
    const schedules: Schedule[] = [];
    timetable.forEach((entry: any) => {
        const newClass: Class = {
            subject: entry.subject,
            teacher: entry.teacher,
            division: entry.division
        }

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
                    class: newClass
                });
                start = current;
                prev = current;
            }

            schedules.push({
                day: day,
                period_from: start,
                period_to: prev,
                class: newClass
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