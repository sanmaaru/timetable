import React from 'react';
import './TimetableGrid.css'
import {DAY_LIST, PERIOD_LIST, Schedule} from "../../types/schedule";

const periods = PERIOD_LIST
const days = DAY_LIST

interface TimetableGridProps {

    schedules: Schedule[];

}

const drawSchedule = (schedules: Schedule[]) => (
    schedules.map(schedule => {
        const columnIdx = days.indexOf(schedule.day) + 2

        return [<div
            key={`timetable-class-${schedule.class.subject}-${schedule.class.teacher}`}
            className="timetable-class"
            style={{
                backgroundColor: schedule.class.color,
                gridRowStart: schedule.period_from,
                gridRowEnd: schedule.period_to + 1,
                gridColumn: columnIdx,
                boxShadow: `1px 1px 2px ${schedule.class.color}`,
                color: schedule.class.textColor,
            }}
        >
            <span className='subject'>{schedule.class.subject}</span>
            <span className='teacher'>{schedule.class.teacher}T</span>
            <span className='division'>{schedule.class.division}분반</span>
        </div>]
    })
);

const TimetableGrid = ({schedules}: TimetableGridProps) => {
    return (
        <div className="timetable-grid-column timetable-grid-row timetable-grid">
            {drawSchedule(schedules)}
            {periods.map(period => ( // create cell of period
                <div
                    key={`timetable-grid-${period}`}
                    className="timetable-grid-cell"
                    style={{
                        gridRow: period,
                        gridColumn: 1,
                    }}
                >
                    <span className={`timetable-grid-period`}>{period}</span>
                </div>
            ))}

            {periods.map(period => { // create cell of day
                return days.map((day, dayIdx) => {
                    const columnIdx = dayIdx + 2

                    return <div
                        key={`timetable-grid-${day}-${period}`}
                        className="timetable-grid-cell"
                        style={{
                            gridRow: period,
                            gridColumn: columnIdx,
                        }}
                    ></div>
                })
            })}
        </div>
    )
}

export default TimetableGrid;