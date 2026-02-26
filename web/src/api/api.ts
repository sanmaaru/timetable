import {AxiosError} from "axios";



export interface ApiResponse<T = void> {
    data: T | null;
    error: string | null;
}

export const withApi = async <T>(apiCall: () => Promise<T>): Promise<ApiResponse<T>> => {
    try {
        const data = await apiCall()
        return { data: data, error: null }
    } catch(error) {
        return { data: null, error: getErrorCode(error)}
    }
}

export const getErrorCode = (error: any) => {
    if (!(error instanceof AxiosError))
        return 'UNKNOWN_ERROR';

    const code= error.response?.data?.code

    if (code)
        return code
    else
        return 'UNKNOWN_ERROR';
}
