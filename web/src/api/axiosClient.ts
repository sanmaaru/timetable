import axios, {AxiosError, InternalAxiosRequestConfig} from "axios";
import {getRefresh, getToken, removeTokens, setTokens} from "../auth/auth";
import {renderToReadableStream} from "react-dom/server";

const baseUrl = '/api'

export const publicAxiosClient = axios.create({
    baseURL: baseUrl,
    headers: {
        'Content-Type': 'application/json'
    },
    withCredentials: true
})

export const privateAxiosClient = axios.create({
    baseURL: baseUrl,
    headers: {
        'Content-Type': 'application/json'
    },
    withCredentials: true
})

// insert access token when use private api request
privateAxiosClient.interceptors.request.use(
    (config) => {
        const accessToken = getToken()
        if (!!accessToken) {
            config.headers.Authorization = `Bearer ${accessToken}`
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// when jwt fail, request to refresh in order to reload jwt
privateAxiosClient.interceptors.response.use(
    (response) => response, // 정상 응답 통과
    async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry: boolean };
        if (error.response?.status !== 401 || originalRequest._retry)
            return Promise.reject(error);

        // 무한 루프 방지
        originalRequest._retry = true;

        try {
            const refreshResponse = await publicAxiosClient.post('/auth/refresh', {
                refresh_token: getRefresh(),
                access_token: getToken()
            });

            const newAccessToken = refreshResponse.data.access_token;
            const newRefreshToken = refreshResponse.data.refresh_token;

            setTokens(newAccessToken, newRefreshToken);

            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            return privateAxiosClient(originalRequest);
        } catch (error) {
            removeTokens()
            return Promise.reject(error);
        }

    }
);