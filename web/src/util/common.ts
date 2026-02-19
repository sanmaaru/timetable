import {Day, Period} from "../types/schedule";

const day2KrMap = {
    'Mon': '월요일',
    'Tue': '화요일',
    'Wed': '수요일',
    'Thu': '목요일',
    'Fri': '금요일',
} as Record<Day, string>;

export const scheduleToString = (day: Day, period_from: Period, period_to: Period) => {
    if (period_from == period_to)
        return `${day2KrMap[day]} ${period_from}교시`;

    return `${day2KrMap[day]} ${period_from}-${period_to}교시`;
}

export const getGrade = (generation: number)=> {
    const currentYear = new Date().getFullYear()
    return currentYear - 1982 - generation;
}