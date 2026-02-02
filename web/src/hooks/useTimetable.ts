import {useEffect, useState} from "react";
import {TimetableData} from "../types/timetable";
import {fetchTimetable} from "../api/fetchTimetable";

const useTimetable = () => {
    const [timetableData, setTimetableData] = useState<TimetableData | null>();
    const [isLoading, setIsLoading] = useState(true);

    // TODO: Store timetable data in cookie
    useEffect(() => {
        const loadData = async () => {
            try {
                const data = await fetchTimetable();
                setTimetableData(data)
            } catch (error: any) {
                console.error(error);
            } finally {
                setIsLoading(false);
            }
        };

        loadData();
    }, []);
    
    return { timetableData, isLoading };
}

export default useTimetable