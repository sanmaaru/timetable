import {useCallback, useEffect, useState} from "react";
import {TimetableData} from "../types/timetable";
import {fetchClassmates, fetchTimetable} from "../api/fetchTimetable";
import {fetchTimetableStatus} from "../api/fetchStatus";
import {getJsonCookie, setJsonCookie, timetable} from "../util/storage";
import {storageKeys} from "../constants/storageKeys";
import {UserInfo} from "../types/account";
import {Student} from "../types/class";

const useTimetable = () => {
    const [timetableData, setTimetableData] = useState<TimetableData | null>();
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        let isMounted = true;

        const loadData = async () => {
            let response= await fetchTimetableStatus()
            const cookie = getJsonCookie<string>(storageKeys.TIMETABLE_VERSION)

            if(response.error) {
                if (isMounted)
                    setIsLoading(false);
                return
            }

            const version = response.data
            let data = null
            if (cookie && cookie === version)
                data = timetable.get()

            if(!data) {
                const response = await fetchTimetable();
                if (response.error) {
                    if(isMounted)
                        setIsLoading(false);
                    return
                }

                data = response.data
                timetable.set(data)
                setJsonCookie(storageKeys.TIMETABLE_VERSION, version);
            }

            if(isMounted) {
                setTimetableData(data || null)
                setIsLoading(false);
            }
        };

        loadData();

        return () => {
            isMounted = false
        }
    }, []);

    const getSchedule = useCallback((lectureId: string) => {
        if (!timetableData?.schedules) return null
        for (const schedule of timetableData?.schedules) {
            if(schedule.lecture.lectureId == lectureId)
                return schedule
        }

        return null
    }, [timetableData]);
    
    return { timetableData, isLoading, getSchedule };
}

export const useClassmates = (lectureId: string) => {
    const [classmatesData, setClassmatesData] = useState<Student[]>([]);
    const [isLoading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        let isMounted = true;

        const loadData = async () => {
            const response = await fetchClassmates(lectureId)
            if (response.error) {
                if (isMounted)
                    setLoading(false)
                return
            }

            if (!isMounted) return;
            setLoading(false);
            setClassmatesData(response.data ?? [])
        };

        loadData()

        return () => {
            isMounted = false;
        }
    }, [lectureId]);

    return { classmatesData, isLoading }
}

export default useTimetable