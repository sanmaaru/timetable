import {DAY_LIST} from "../../types/schedule";
import React from "react";
import style from './TimetableHeader.module.css'
import gridStyle from './TimetableGrid.module.css'

const days = DAY_LIST;

const TimetableHeader = () => {
    return (
        <div className={`${style.timetableHeader} ${gridStyle.timetableGridColumn}`}>
            <div className={gridStyle.cell}></div>
            {days.map(day => (
                <div key={day} className={gridStyle.cell}>
                    <span>{day}</span>
                </div>
            ))}
        </div>
    );
}

export default TimetableHeader;

