import Cookies from "js-cookie";

export const getToken = (): string | undefined => {
    return Cookies.get("access-token");
}

export const getRefresh = () => {
    return Cookies.get("refresh-token");
}

export const removeTokens = () => {
    Cookies.remove("access-token", { path: '/' });
    Cookies.remove("refresh-token", { path: '/' });
}

export const setTokens = (access: string, refresh: string) => {
    if (!access)
        throw new Error('Access token must not be null');

    if (!refresh)
        throw new Error('Refresh token must not be null');


    Cookies.set("access-token", access, { path: '/', expires: 14 });
    Cookies.set("refresh-token", refresh, { path: '/', expires: 14 });
}

export const isAuthenticated = () => (
    !!getToken()
)