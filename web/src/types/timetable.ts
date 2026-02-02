import {Schedule} from "./schedule";
import {Class} from "./class";

export interface TimetableData {
    name: string;
    schedules: Schedule[];
    classes: Class[];
}
