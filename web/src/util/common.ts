import {Day, Period} from "../types/schedule";
import {Role, ROLE_LIST} from "../types/account";

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

export const getRole = (role: number): Role => {
    for (let i = 0; i < ROLE_LIST.length; i++) {
        if ((1 << i) <=  role && role < (1 << (i+1)))
            return ROLE_LIST[i];
    }

    return "Student"
}