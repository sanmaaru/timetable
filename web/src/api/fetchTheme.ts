import {privateAxiosClient} from "./axiosClient";
import {ColorScheme, Theme} from "../types/theme";
import {BaseResponseDto} from "./dto/response.dto";
import {ColorSchemeDto, ThemeDto} from "./dto/theme.dto";
import {withApi} from './api'

const parseThemeData = (theme: ThemeDto) => {
    const colorSchemes: ColorScheme[] = [];
    theme.color_schemes.forEach((item: ColorSchemeDto) => {
        colorSchemes.push({
            subject: item.subject,
            color: '#' + item.color,
            textColor: '#' + item.text_color
        })
    })

    return {
        title: theme.title,
        themeId: theme.theme_id,
        colorSchemes: colorSchemes,
        selected: theme.selected,
    }
}

export const fetchThemes = () => {
    return withApi(async () => {
        const response = await privateAxiosClient.get<BaseResponseDto<ThemeDto[]>>('/theme/', {});

        const rawData = response.data.data;
        const themes: Theme[] = [];
        rawData.forEach((item: ThemeDto) => {
            themes.push(parseThemeData(item));
        })

        return themes;
    });
}

export const fetchTheme = (themeId: string) => {
    return withApi(async () => {
        const response = await privateAxiosClient.get<BaseResponseDto<ThemeDto>>(`/theme/${themeId}`, {});
        const rawData = response.data.data;
        return parseThemeData(rawData);
    })
}

export const fetchSelectedTheme = () => {
    return withApi(async () => {
        const response = await privateAxiosClient.get<BaseResponseDto<ThemeDto>>('/theme/selected', {});

        const rawData = response.data.data;
        return parseThemeData(rawData)
    });
}

export const deleteTheme = (themeId: string) => {
    return withApi(async () => {
        await privateAxiosClient.delete(`/theme/${themeId}`);
        return null;
    })
}

export const putSelectedTheme = (themeId: string) => {
    return withApi(async () => {
        await privateAxiosClient.put(`/theme/selected`, {
            theme_id: themeId,
        });
        return null;
    })
}

export const createTheme = (title: string) => {
    return withApi(async () => {
        const response = await privateAxiosClient.post(`/theme/`, {
            title: title
        })

        const rawData = response.data.data;
        return parseThemeData(rawData)
    })
}

export const putTheme = (themeId: string, theme: Theme) => {
    return withApi(async () => {
        await privateAxiosClient.put(`/theme/${themeId}`, {
            title: theme.title,
            color_schemes: theme.colorSchemes.map((item: ColorScheme) => ({
                subject: item.subject,
                color: item.color.replace('#', ''),
                text_color: item.textColor.replace('#', '') ,
            })),
        })
        return null
    })
}
