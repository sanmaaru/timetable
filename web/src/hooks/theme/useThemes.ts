import {useCallback, useEffect, useState} from "react";
import {Theme} from "../../types/theme";
import {fetchSelectedTheme, fetchTheme, fetchThemes} from "../../api/fetchTheme";
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
        // 1. 함수형 업데이트 사용 (themeData를 의존성 배열에 안 넣어도 됨 -> 최신 상태 보장)
        setThemeData((prev) => {
            if (!prev) return null; // 데이터가 없으면 무시

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
    }, []);


    const update = useCallback(() => { // api 통신

    }, [themeData, themeId])

    return { isLoading, themeData, update, loadData, setColorScheme };
}


