import React from "react";
import './ThemeView.css';
import {useParams} from "react-router-dom";
import useTimetable from "../../hooks/useTimetable";
import TimetableGrid from "../../components/timetable/TimetableGrid";
import TimetableHeader from "../../components/timetable/TimetableHeader";

const ThemeView = () => {
    const { themeId } = useParams()
    const { timetableData, themeData, isLoading } =  useTimetable(themeId)

    if (isLoading) {
        return (<div id='theme-view'>
        </div>)
    }

    if (!timetableData || !themeData) {
        return (<div>
            알 수 없는 오류가 발생하였습니다. 관리자에게 문의해주세요
        </div>)
    }

    const { schedules } = timetableData;

    return (<div id='theme-view'>
        <div className='title container'>
            <span className='title'>{'테마 미리보기'}</span>
            <span className='name'> - {themeData.title}</span>
        </div>
        <div>
            <TimetableHeader/>
            <TimetableGrid schedules={schedules} colorSchemes={themeData.colorSchemes}/>
        </div>
        <div>

        </div>
    </div>)
}

export default ThemeView;