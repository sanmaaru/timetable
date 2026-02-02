import {useEffect, useState} from "react";
import {TimetableData} from "../types/timetable";
import {fetchTimetable} from "../api/fetchTimetable";
import {fetchSelectedTheme, fetchTheme} from "../api/fetchTheme";
import {Theme} from "../types/theme";

const useTimetable = (themeId: string | null = null) => {
    const [timetableData, setTimetableData] = useState<TimetableData | null>();
    const [themeData, setThemeData] = useState<Theme | null>();
    const [isLoading, setIsLoading] = useState(true);

    // TODO: Store timetable data in cookie
    useEffect(() => {
        const loadData = async () => {
            try {
                const data = await fetchTimetable();
                setTimetableData(data)

                let theme = null
                if (!themeId)
                    theme = await fetchSelectedTheme()
                else
                    theme = await fetchTheme(themeId)

                setThemeData(theme)
            } catch (error: any) {
                console.error(error);
            } finally {
                setIsLoading(false);
            }
        };

        loadData();
    }, []);
    
    return { timetableData, themeData, isLoading };
}

export default useTimetable