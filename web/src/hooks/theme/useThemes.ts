import {useCallback, useEffect, useState} from "react";
import {Theme} from "../../types/theme";
import {fetchSelectedTheme, fetchTheme, fetchThemes, putTheme} from "../../api/fetchTheme";
import theme from "../../pages/theme/Theme";

export const useThemes = () => {
    const [isLoading, setLoading] = useState<boolean>(true);
    const [themeData, setThemeData] = useState<Theme[] | null>(null);
    const loadData = async () => {
        try {
            const data = await fetchThemes()
            setThemeData(data)
        } catch (error: any) { // TODO: error logic 추가
            console.error(error)
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadData();
    }, [])

    return { isLoading, themeData, loadData }
}

export const useTheme = (themeId?: string | null) => {
    const [themeData, setThemeData] = useState<Theme | null>();
    const [isLoading, setIsLoading] = useState(true);

    const loadData = async () => {
        try {
            let theme = null
            if (!themeId)
                theme = await fetchSelectedTheme()
            else
                theme = await fetchTheme(themeId)

            setThemeData(theme)
        } catch (e) {

        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        loadData();
    }, [])

    return { isLoading, themeData, loadData }
}

export const useMutableTheme = (themeId: string | null) => {
    const [isLoading, setLoading] = useState<boolean>(true);
    const [themeData, setThemeData] = useState<Theme | null>(null);
    const [isSaved, setIsSaved] = useState<boolean>(true);

    const loadData = useCallback(async () => {
        try {
            let theme = null
            if (!themeId)
                theme = await fetchSelectedTheme()
            else
                theme = await fetchTheme(themeId)
            setThemeData(theme)
        } catch (error: any) {
            console.error(error)
        } finally {
            setLoading(false);
        }
    }, [themeId])

    useEffect(() => {
        loadData();
    }, [])

    const setColorScheme = useCallback((subject: string, color?: string, textColor?: string) => {
        setThemeData((prev) => {
            if (!prev) return null;

            return {
                ...prev,
                colorSchemes: prev.colorSchemes.map((item) => {
                    if (item.subject === subject) {
                        return {
                            ...item,
                            color: color ?? item.color,
                            textColor: textColor ?? item.textColor
                        };
                    }
                    return item;
                })
            };
        });

        setIsSaved(false);
    }, []);


    const update = useCallback(async (onSuccess?: () => void, onFail?: (error: string) => void) => { // api 통신
        if (!themeData) {
            onFail?.('')
            return
        }

        const error = await putTheme(themeData.theme_id, themeData)
        if (error)
            onFail?.(error)
        else
            onSuccess?.()
        setIsSaved(true)
    }, [themeData, themeId])

    return { isLoading, themeData, update, loadData, setColorScheme, isSaved };
}


