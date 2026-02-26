import {privateAxiosClient} from "./axiosClient";
import {BaseResponseDto} from "./dto/response.dto";
import {VersionDto} from "./dto/dto";
import {withApi} from './api'

export const fetchThemeStatus = () => {
    return withApi(async () => {
        const response = await privateAxiosClient.get<BaseResponseDto<VersionDto>>('/theme/status', {})
        return response.data.data.version
    })
}


export const fetchTimetableStatus = () => {
    return withApi(async () => {
        const response = await privateAxiosClient.get<BaseResponseDto<VersionDto>>('/timetable/status', {})
        return response.data.data.version
    })
}