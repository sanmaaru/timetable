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
        const response = await privateAxiosClient.delete(`/theme/${themeId}`);
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
