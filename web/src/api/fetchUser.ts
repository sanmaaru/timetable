import {UserInfo} from "../types/account";
import {AxiosError} from "axios";
import {privateAxiosClient} from "./axiosClient";
import {getRole} from "../util/common";

const parseUser = (data: any): UserInfo => {
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
    try {
        const response = await privateAxiosClient.get('/account/', {})

        return { data: parseUser(response.data.data), error: null }
    } catch (error) {
        if (!(error instanceof AxiosError))
            return { data: null, error: 'UNKNOWN_ERROR' };

        const code= error.response?.data?.code

        if (code)
            return { data: null, error: code }
        else
            return { data: null, error: 'UNKNOWN_ERROR' }
    }
}

export const fetchUser= async (userId: string) => {
    try {
        const response = await privateAxiosClient.get(`/account/${userId}`, {})

        return { data: parseUser(response.data.data), error: null }
    } catch (error) {
        if (!(error instanceof AxiosError))
            return { data: null, error: 'UNKNOWN_ERROR' };

        const code= error.response?.data?.code

        if (code)
            return { data: null, error: code }
        else
            return { data: null, error: 'UNKNOWN_ERROR' }
    }
}

export const deleteUser= async () => {
    try {
        const response = await privateAxiosClient.delete('/account/', {})

        return null
    } catch (error) {
        if (!(error instanceof AxiosError))
            return 'UNKNOWN_ERROR';

        const code = error.response?.data?.code

        if (code)
            return code
        else
            return 'UNKNOWN_ERROR'
    }
}