import {UserInfo} from "../types/account";
import {privateAxiosClient} from "./axiosClient";
import {getRole} from "../util/common";
import {BaseResponseDto} from "./dto/response.dto";
import {UserDto} from "./dto/user.dto";
import {withApi} from "./api";

const parseUser = (data: UserDto): UserInfo => {
    return {
        userId: data.user_id,
        username: data.username,
        email: data.email,
        name: data.user_info.name,
        clazz: data.user_info.clazz,
        number: data.user_info.number,
        credit: data.user_info.credit,
        generation: data.user_info.generation,
        role: getRole(data.user_info.role),
    }
}

export const fetchCurrentUser= async () => {
    return withApi(async () => {
        const response = await privateAxiosClient.get<BaseResponseDto<UserDto>>('/account/', {})

        return parseUser(response.data.data)
    })
}

export const fetchUser= async (userId: string) => {
    return withApi(async () => {
        const response = await privateAxiosClient.get<BaseResponseDto<UserDto>>(`/account/${userId}`, {})

        return parseUser(response.data.data)
    })
}

export const deleteUser= () => {
    return withApi(async () => {
        await privateAxiosClient.delete('/account/', {})
        return null
    })
}