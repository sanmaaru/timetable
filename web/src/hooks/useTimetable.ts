import {useCallback, useEffect, useState} from "react";
import {TimetableData} from "../types/timetable";
import {fetchTimetable} from "../api/fetchTimetable";
import {fetchTimetableStatus} from "../api/fetchStatus";
import {getJsonCookie, setJsonCookie, timetable} from "../util/storage";

const useTimetable = () => {
    const [timetableData, setTimetableData] = useState<TimetableData | null>();
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            try {
                const version = await fetchTimetableStatus();
                const cookie = getJsonCookie<string>(`timetable-version`)
                if (cookie && cookie == version) {
                    console.log(cookie);
                    setTimetableData(timetable.get())
                    return
                }

                const data = await fetchTimetable();
                timetable.set(data)
                setJsonCookie('timetable-version', version);
                setTimetableData(data)
            } catch (error: any) {
                setTimetableData(null)
            } finally {
                setIsLoading(false);
            }
        };

        loadData();
    }, []);

    const getSchedule = useCallback((classId: string) => {
        if (!timetableData?.schedules) return null
        for (const schedule of timetableData?.schedules) {
            if(schedule.clazz.classId == classId)
                return schedule
        }

        return null
    }, [timetableData]);
    
    return { timetableData, isLoading, getSchedule };
}

export default useTimetable