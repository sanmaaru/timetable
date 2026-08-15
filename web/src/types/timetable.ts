import {Schedule} from "./schedule";
import {Lecture} from "./class";

export interface TimetableData {
    name: string;
    schedules: Schedule[];
    lectures: Lecture[];
}
