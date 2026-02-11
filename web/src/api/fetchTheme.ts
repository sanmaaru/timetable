import {privateAxiosClient} from "./axiosClient";
import {ColorScheme, Theme} from "../types/theme";
import {AxiosError} from "axios";

const parseThemeData = (theme: any) => {
    const colorSchemes: ColorScheme[] = [];
    theme.color_schemes.forEach((item: any) => {
        colorSchemes.push({
            subject: item.subject,
            color: '#' + item.color,
            textColor: '#' + item.text_color
        })
    })

    return {
        title: theme.title,
        theme_id: theme.theme_id,
        colorSchemes: colorSchemes,
        selected: theme.selected,
    }
}

export const fetchThemes = async () => {
    const response = await privateAxiosClient.get('/theme/', {});

    const rawData = response.data.data;
    const themes: Theme[] = [];
    rawData.forEach((item: any) => {
        themes.push(parseThemeData(item));
    })

    return themes;
}

export const fetchTheme = async (themeId: string) => {
    const response = await privateAxiosClient.get(`/theme/${themeId}`, {});

    const rawData = response.data.data;
    return parseThemeData(rawData);
}

export const fetchSelectedTheme = async () => {
    const response = await privateAxiosClient.get('/theme/selected', {});

    const rawData = response.data.data;
    return parseThemeData(rawData)
}

export const deleteTheme = async (themeId: string) => {
    try {
        await privateAxiosClient.delete(`/theme/${themeId}`);
        return null;
    } catch (error) {
        if (!(error instanceof AxiosError))
            return 'UNKNOWN_ERROR';

        const code= error.response?.data?.code

        if (code)
            return code
        else
            return 'UNKNOWN_ERROR';
    }
}

export const putSelectedTheme = async (themeId: string) => {
    try {
        await privateAxiosClient.put(`/theme/selected`, {
            theme_id: themeId,
        });
        return null;
    } catch (error) {
        if (!(error instanceof AxiosError))
            return 'UNKNOWN_ERROR';

        const code = error.response?.data?.code
        if (code)
            return code
        else
            return 'UNKNOWN_ERROR';
    }
}

export const createTheme = async (title: string) => {
    try {
        const response = await privateAxiosClient.post(`/theme/`, {
            title: title
        })

        const rawData = response.data.data;
        console.log(rawData);
        return {
            data: parseThemeData(rawData),
            error: null
        };
    } catch (error) {
        if (!(error instanceof AxiosError))
            return {
                data: null,
                error: 'UNKNOWN_ERROR'
            };

        const code = error.response?.data?.code
        return { data: null, error: code ? code : 'UNKNOWN_ERROR' };
    }
}
