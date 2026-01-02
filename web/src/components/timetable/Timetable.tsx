import React from "react";
import './Timetable.css';
import {DAY_LIST, Schedule} from "../../types/schedule";
import TimetableGrid from "./TimetableGrid";

const days = DAY_LIST;

const TimetableHeader = () => {
    return (
      <div className="timetable-header timetable-grid-column">
          <div className="timetable-grid-cell"></div>
          {days.map(day => (
              <div key={day} className="timetable-grid-cell">
                  <span className="header-cell-day">{day}</span>
              </div>
          ))}
      </div>
    );
}

interface TimetableProps {

    name: string
    schedules: Schedule[];

}

const Timetable = ({name, schedules}: TimetableProps) => {
    return (<div className="timetable">
        <div className='timetable-title'>
            <span className='title'>시간표</span>
            <span className='name'> - {name}</span>
        </div>
        <TimetableHeader/>
        <TimetableGrid schedules={schedules}/>
    </div>);
}

export default Timetable