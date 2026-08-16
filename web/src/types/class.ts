export interface Lecture {
    lectureId: string;
    subject: string;
    teacher: string;
    division: number;
    room: string;
}

export interface Student {
    studentId: string;
    name: string;
    clazz: number;
    number: number;
    generation: number;
}