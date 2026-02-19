import Cookies from "js-cookie";
import {TimetableData} from "../types/timetable";
import {Theme} from "../types/theme";

export interface CookieOptions {
    expires?: number | Date;
    path?: string;
    domain?: string;
    secure?: boolean;
}

export const setJsonCookie = (key: string, value: any, options?: CookieOptions) => {
    Cookies.set(key, JSON.stringify(value), {
        path: '/',
        ...options,
    });
};

export const getJsonCookie = <T>(key: string): T | null => {
    const value = Cookies.get(key);

    if (!value) return null;

    try {
        return JSON.parse(value) as T;
    } catch (e) {
        console.error(e);
        return null;
    }
}

export const removeCookie = (key: string) => {
    Cookies.remove(key);
}

const maxLength = 25;
export const recentUsedColor= {
    query: (): string[] => {
        return getJsonCookie('color-recently-used') || []
    },

    append: (color: string) => {
        const colors: string[] = getJsonCookie('color-recently-used') || []
        const filtered = colors.filter(v => v != color)
        const value = [color, ...filtered].slice(0, maxLength);

        console.log(value)

        setJsonCookie('color-recently-used', value)
    },

    init: () => {
        if(!getJsonCookie('color-recently-used'))
            setJsonCookie('color-recently-used', ['#000000', '#ffffff']);
    }
}

export const timetable = {
    get: (): TimetableData | null => {
        if (typeof window === 'undefined') return null;

        const value = localStorage.getItem('timetable-data');
        return value ? JSON.parse(value) : null;
    },

    set: (data: TimetableData) => {
        if (typeof window === 'undefined') return;

        localStorage.setItem('timetable-data', JSON.stringify(data));
    },

    getClass: (classId: string) => {
        const classes = timetable.get()?.classes
        if (!classes) return null;

        for (const clazz of classes) {
            if (clazz.classId === classId)
                return clazz;
        }

        return null;
    }
}

export const theme = {
}