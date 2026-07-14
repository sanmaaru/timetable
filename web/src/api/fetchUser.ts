import {UserInfo} from "../types/account";
import {privateAxiosClient} from "./axiosClient";
import {getRole} from "../util/common";
import {BaseResponseDto} from "./dto/response.dto";
import {IdTokenDto, UserDto, UserInfoDto} from "./dto/user.dto";
import {withApi} from "./api";

const parseUser = (data: UserDto): UserInfo => {
    return {
        userId: data.user_id,
        userInfoId: data.user_info.user_info_id,
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
        const response = await privateAxiosClient.get<BaseResponseDto<UserDto>>(
            `/account/${userId}`
        )

        return parseUser(response.data.data)
    })
}

export const deleteUser= () => {
    return withApi(async () => {
        await privateAxiosClient.delete('/account/', {})
        return null
    })
}

export const fetchIdToken = (userInfoId: string) => {
    return withApi(async () => {
        const response = await privateAxiosClient.get<BaseResponseDto<IdTokenDto>>(
            `/auth/identifier/${userInfoId}`
        )

        return response.data.data.token_id
    })
}

export const fetchIdTokens = () => {
    return withApi(async () => {
        const response = await privateAxiosClient.get<BaseResponseDto<IdTokenDto[]>>(
            `/auth/identifier`
        )
        const tokenArray = response.data.data;

        const tokenMap: Record<string, string | null> = {};
        if(tokenArray) {
            for (const token of tokenArray) {
                tokenMap[token.owner_id] = token.token_id
            }
        }
        return tokenMap
    })
}

export const fetchUserInfos = (role: string) => {
    return withApi(async () => {
        const response = await privateAxiosClient.get<BaseResponseDto<UserDto[]>> (
            `/account/userInfo`,
            {
                params: { role },
            }
        )
        
        return response.data.data.map(dto => parseUser(dto))
    })
}