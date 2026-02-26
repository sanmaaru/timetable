import {UserInfoDto} from "./user.dto";

export interface PeriodDto {
    period: number;
    day: string;
}

export interface ClassDto {
    class_id: string;
    division: number;
    periods: PeriodDto[];
    classmates: UserInfoDto[];
    subject: string;
    teacher: string;
    room: string;
}

export interface TimetableDto {
    name: string
    username: string
    timetable: ClassDto[]
}