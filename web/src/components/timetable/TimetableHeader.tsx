import {DAY_LIST} from "../../types/schedule";
import React from "react";
import './TimetableHeader.css'

const days = DAY_LIST;

const TimetableHeader = () => {
    return (
        <div className="timetable-header timetable-grid-column">
            <div className="timetable-grid-cell"></div>
            {days.map(day => (
                <div key={day} className="timetable-grid-cell">
                    <span>{day}</span>
                </div>
            ))}
        </div>
    );
}

export default TimetableHeader;

