export interface UserInfoDto {
    user_info_id: string;
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

export interface IdTokenDto {
    token_id: string | null;
    owner_id: string;
}