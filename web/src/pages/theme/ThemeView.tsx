import React, {useEffect, useState} from "react";
import './ThemeView.css';
import {useParams} from "react-router-dom";
import {fetchTimetable} from "../../api/fetchTimetable";
import Timetable from "../../components/timetable/Timetable";
import {TimetableData} from "../../types/timetable";
import useTimetable from "../../hooks/useTimetable";
import DetailBar from "../../components/detailBar/DetailBar";

const ThemeView = () => {
    const { themeId } = useParams()
    const { timetableData, themeData, isLoading } =  useTimetable(themeId)

    if (isLoading) {
        return (<div id='theme-view'>
            <Timetable title={'테마 미리보기'} name={''} schedules={[]} theme={{ title: '', theme_id: '', colorSchemes: [] }}/>
        </div>)
    }

    if (!timetableData || !themeData) {
        return (<div>
            알 수 없는 오류가 발생하였습니다. 관리자에게 문의해주세요
        </div>)
    }

    const { schedules } = timetableData;

    return (<div id='theme-view'>
        <Timetable title={'테마 미리보기'} name={themeData.title} schedules={schedules} theme={themeData}/>
        <DetailBar quote="달을 향해 쏴라. 빗나가도 별이 될테니" source="레스 브라운" image="/assets/image/detail_image.png"/>
    </div>)
}

export default ThemeView;