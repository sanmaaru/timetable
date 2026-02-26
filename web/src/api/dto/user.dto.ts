export interface UserInfoDto {
    name: string;
    generation: number | null;
    clazz: number | null;
    number: number | null;
    credit: number | null;
    role: number
}

export interface UserDto {
    user_id: string;
    email: string;
    username: string;
    user_info: UserInfoDto;
}