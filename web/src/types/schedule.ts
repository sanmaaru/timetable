import {Class} from "./class";

export const DAY_LIST = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] as const;
export type Day = typeof DAY_LIST[number];

export const PERIOD_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9] as const;
export type Period = typeof PERIOD_LIST[number];

export interface Schedule {
    day: Day;
    period_from: Period;
    period_to: Period;
    clazz: Class;
}
