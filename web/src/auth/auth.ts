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
    Cookies.set("access-token", access);
    Cookies.set("refresh-token", refresh);
}

export const isAuthenticated = () => (
    !!getToken()
)