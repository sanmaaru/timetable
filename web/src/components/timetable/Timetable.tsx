import React from "react";
import './Timetable.css';
import {Schedule} from "../../types/schedule";
import TimetableGrid from "./TimetableGrid";
import {Theme} from "../../types/theme";
import TimetableHeader from "./TimetableHeader";

interface TimetableProps {
    name: string
    schedules: Schedule[];
    theme: Theme;

}

const Timetable = ({name, schedules, theme}: TimetableProps) => {
    return (<div className="timetable">
        <div className='timetable-title'>
            <span className='title'>시간표</span>
            <span className='name'> - {name}</span>
        </div>
        <TimetableHeader/>
        <TimetableGrid schedules={schedules} colorSchemes={theme.colorSchemes}/>
    </div>);
}

export default Timetable