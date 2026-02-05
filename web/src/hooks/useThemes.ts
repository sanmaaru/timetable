import {useEffect, useState} from "react";
import {Theme} from "../types/theme";
import {fetchThemes} from "../api/fetchTheme";

export const useThemes = () => {
    const [isLoading, setLoading] = useState<boolean>(true);
    const [themeData, setThemeData] = useState<Theme[] | null>(null);

    useEffect(() => {
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

        loadData();
    }, [])

    return { isLoading, themeData }
}


