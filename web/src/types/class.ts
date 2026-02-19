export interface Class {
    classId: string;
    subject: string;
    teacher: string;
    division: number;
    room: string;
    classmates: Student[];
}

export interface Student {
    studentId: string;
    name: string;
    clazz: number;
    number: number;
    generation: number;
}