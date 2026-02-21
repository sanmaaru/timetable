export const ROLE_LIST = ['Student', 'Teacher', 'Manager', 'Administrator'] as const
export type Role = typeof ROLE_LIST[number];

export interface UserInfo {
    userId: string;
    email: string;
    username: string;
    name: string;
    generation: number;
    clazz: number;
    number: number;
    credit: number;
    role: Role;
}