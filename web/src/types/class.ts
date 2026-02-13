export interface Class {
    subject: string;
    teacher: string;
    division: number;
}

export interface Student {
    studentId: string;
    name: string;
}

export interface ClassDetail {

    room: string;
    students: Student[];

}
