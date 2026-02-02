import React from "react";
import './Timetable.css';
import {DAY_LIST, Schedule} from "../../types/schedule";
import TimetableGrid from "./TimetableGrid";
import {Theme} from "../../types/theme";

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

interface TimetableProps {
    title: string;
    name: string
    schedules: Schedule[];
    theme: Theme;

}

const Timetable = ({title, name, schedules, theme}: TimetableProps) => {
    return (<div className="timetable">
        <div className='timetable-title'>
            <span className='title'>{title}</span>
            <span className='name'> - {name}</span>
        </div>
        <TimetableHeader/>
        <TimetableGrid schedules={schedules} colorSchemes={theme.colorSchemes}/>
    </div>);
}

export default Timetable