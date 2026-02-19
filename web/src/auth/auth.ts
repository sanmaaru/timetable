import Cookies from "js-cookie";
import {getJsonCookie, removeCookie, setJsonCookie} from "../util/storage";

export const getToken = (): string | null => {
    return getJsonCookie<string>('access-token')
}

export const getRefresh = () => {
    return getJsonCookie<string>("refresh-token");
}

export const removeTokens = () => {
    removeCookie("access-token");
    removeCookie("refresh-token");
}

export const setTokens = (access: string, refresh: string) => {
    if (!access)
        throw new Error('Access token must not be null');

    if (!refresh)
        throw new Error('Refresh token must not be null');

    setJsonCookie("access-token", access, {expires: 14});
    setJsonCookie("refresh-token", refresh, {expires: 14});
}

export const isAuthenticated = () => (
    !!getToken()
)