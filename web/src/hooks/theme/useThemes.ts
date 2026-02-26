import {useCallback, useEffect, useRef, useState} from "react";
import {Theme} from "../../types/theme";
import {fetchSelectedTheme, fetchTheme, fetchThemes, putTheme} from "../../api/fetchTheme";
import {fetchThemeStatus} from "../../api/fetchStatus";
import {getJsonCookie, setJsonCookie, theme} from "../../util/storage";
import {storageKeys} from "../../constants/storageKeys";

export const useThemes = () => {
    const [isLoading, setLoading] = useState<boolean>(true);
    const [themeData, setThemeData] = useState<Theme[] | null>(null);
    const isMounted = useRef(true);

    const loadData = async () => {
        const response = await fetchThemes()
        if (response.error) {
            if(isMounted.current)
                setLoading(false);
            return
        }

        if(!isMounted.current) return;
        setThemeData(response.data)
        setLoading(false);
    }

    useEffect(() => {
        isMounted.current = true;
        loadData();

        return () => {
            isMounted.current = false;
        }
    }, [])

    return { isLoading, themeData, loadData }
}

export const useTheme = (themeId?: string | null) => {
    const [themeData, setThemeData] = useState<Theme | null>();
    const [isLoading, setIsLoading] = useState(true);
    const isMounted = useRef<boolean>(true);

    const loadData = async () => {
        const response = await fetchThemeStatus()
        const cookie = getJsonCookie<string>(storageKeys.THEME_VERSION)
        if (response.error) {
            if (isMounted.current)
                setIsLoading(false);
            return;
        }

        const version = response.data
        let data = null
        if (cookie && cookie === version)
            data = themeId ? theme.get(themeId) : theme.getSelected()

        if (!data) {
            const response = await fetchThemes()
            if (response.error) {
                if (isMounted.current)
                    setIsLoading(false);

                return;
            }

            data = response.data
            theme.set(data ?? [])
            setJsonCookie(storageKeys.THEME_VERSION, version)
            data = themeId ? theme.get(themeId) : theme.getSelected()
        }

        if (isMounted.current) {
            setThemeData(data || null)
            setIsLoading(false)
        }
    }

    useEffect(() => {
        isMounted.current = true;
        loadData();

        return () => {
            isMounted.current = false;
        }
    }, [])

    return { isLoading, themeData, loadData }
}

export const useMutableTheme = (themeId: string | null) => {
    const [isLoading, setLoading] = useState<boolean>(true);
    const [themeData, setThemeData] = useState<Theme | null>(null);
    const [isSaved, setIsSaved] = useState<boolean>(true);
    const isMounted = useRef<boolean>(true);

    const loadData = useCallback(async () => {
        let response = null
        if (!themeId)
            response = await fetchSelectedTheme()
        else
            response = await fetchTheme(themeId)

        if(response.error) {
            console.error(response.error)
            setLoading(false)
            return
        }

        if(isMounted.current) {
            setThemeData(response.data)
            setLoading(false)
        }
    }, [themeId])

    useEffect(() => {
        isMounted.current = true
        loadData();

        return () => {
            isMounted.current = false
        }
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

        const response = await putTheme(themeData.themeId, themeData)
        if (response.error)
            onFail?.(response.error)
        else
            onSuccess?.()
        setIsSaved(true)
    }, [themeData, themeId])

    return { isLoading, themeData, update, loadData, setColorScheme, isSaved, setIsSaved };
}


