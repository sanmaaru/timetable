import React, {useEffect, useState} from "react";
import './ThemeView.css';
import {useParams} from "react-router-dom";
import {fetchTimetable} from "../../api/fetchTimetable";
import Timetable from "../../components/timetable/Timetable";
import {TimetableData} from "../../types/timetable";
import useTimetable from "../../hooks/useTimetable";

const ThemeView = () => {
    const themeId = useParams()
    const { timetableData, isLoading } =  useTimetable()

    return (<div id='theme-view'>
    </div>)
}

export default ThemeView;