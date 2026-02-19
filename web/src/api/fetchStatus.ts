import {privateAxiosClient} from "./axiosClient";

export const fetchThemeStatus = async () => {
    const response = await privateAxiosClient.get('/timetable/status', {})

    return response.data.version
}


export const fetchTimetableStatus = async () => {
    const response = await privateAxiosClient.get('/timetable/status', {})

    return response.data.version
}