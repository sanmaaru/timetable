import Cookies from "js-cookie";
import {TimetableData} from "../types/timetable";
import {storageKeys} from "../constants/storageKeys";
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
        return null;
    }
}

export const removeCookie = (key: string) => {
    Cookies.remove(key);
}

const maxLength = 25;
export const recentUsedColor= {
    query: (): string[] => {
        return getJsonCookie(storageKeys.COLOR_RECENTLY_USED) || []
    },

    append: (color: string) => {
        const colors: string[] = getJsonCookie(storageKeys.COLOR_RECENTLY_USED) || [];
        const filtered = colors.filter(v => v != color)
        const value = [color, ...filtered].slice(0, maxLength);

        setJsonCookie(storageKeys.COLOR_RECENTLY_USED, value)
    },

    init: () => {
        if(!getJsonCookie(storageKeys.COLOR_RECENTLY_USED))
            setJsonCookie(storageKeys.COLOR_RECENTLY_USED, ['#000000', '#ffffff']);
    }
}

export const timetable = {
    get: (): TimetableData | null => {
        if (typeof window === 'undefined') return null;

        try {
            const value = localStorage.getItem(storageKeys.TIMETABLE_DATA);
            return value ? JSON.parse(value) : null;
        } catch(e) {
            return null;
        }
    },

    set: (data: TimetableData | null) => {
        if (typeof window === 'undefined') return;

        try {
            localStorage.setItem(storageKeys.TIMETABLE_DATA, JSON.stringify(data));
        } catch(e) {
            return null;
        }
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
    getSelected: (): Theme | null => {
        if (typeof window === 'undefined') return null;

        try {
            const value = localStorage.getItem(storageKeys.SELECTED_THEME_DATA);
            return value ? JSON.parse(value) : null;
        } catch (e) {
            return null;
        }
    },

    get: (themeId: string) => {
        if (typeof window === 'undefined') return null;

        try {
            const values = localStorage.getItem(storageKeys.THEME_DATA);
            const parsed = (values ? JSON.parse(values) : {}) as Record<string, Theme>;

            return parsed[themeId];
        } catch (e) {
            return null;
        }
    },

    set: (themes: Theme[]) => {
        const record = {} as Record<string, Theme>;
        let selectedTheme = null;
        for (const theme of themes) {
            if (theme.selected)
                selectedTheme = theme;

            record[theme.themeId] = theme;
        }

        localStorage.setItem(storageKeys.THEME_DATA, JSON.stringify(record));
        if (selectedTheme)
            localStorage.setItem(storageKeys.SELECTED_THEME_DATA, JSON.stringify(selectedTheme));
    }
}