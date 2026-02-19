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

let isRefreshing = false
let failedQueue: any[] = []

const processQueue = (error: any, token: string | null = null) => {
    failedQueue.forEach((prom) => {
        if (error)
            prom.reject(error)
        else {
            prom.resolve(token)
            isRefreshing = false
        }
    })

    failedQueue = []
}

// when jwt fail, request to refresh in order to reload jwt
privateAxiosClient.interceptors.response.use(
    (response) => response, // 정상 응답 통과
    async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry: boolean };
        if (error.response?.status !== 401 || originalRequest._retry)
            return Promise.reject(error);

        if (isRefreshing) {
            return new Promise(function (resolve, reject) {
                failedQueue.push({resolve, reject});
            }).then((token) => {
                originalRequest.headers.Authorization = `Bearer ${token}`;
                return privateAxiosClient(originalRequest);
            }).catch((error) => {
                return Promise.reject(error);
            })
        }

        // 무한 루프 방지
        originalRequest._retry = true;
        isRefreshing = true;

        try {
            const { data } = await publicAxiosClient.post('/auth/refresh', {
                refresh_token: getRefresh(),
            });

            const newAccessToken = data.access_token;
            const newRefreshToken = data.refresh_token;

            setTokens(newAccessToken, newRefreshToken);

            processQueue(null, newRefreshToken);

            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            return privateAxiosClient(originalRequest);
        } catch (error) {
            processQueue(error, null);

            removeTokens()
            return Promise.reject(error);
        }
    }
);