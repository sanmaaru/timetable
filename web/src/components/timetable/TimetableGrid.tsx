import React, {MutableRefObject} from 'react';
import './TimetableGrid.css'
import {DAY_LIST, PERIOD_LIST, Schedule} from "../../types/schedule";
import {ColorScheme} from "../../types/theme";

const periods = PERIOD_LIST
const days = DAY_LIST

interface TimetableGridProps {
    schedules: Schedule[];
    colorSchemes: ColorScheme[];
    detail: boolean;
    scheduleRefMap?: MutableRefObject<Map<string, HTMLDivElement>>
}

const drawSchedule = (
    schedules: Schedule[],
    colorSchemes: ColorScheme[],
    detail: boolean,
    scheduleRefMap?: MutableRefObject<Map<string, HTMLDivElement>>,
) => {
    const subjectColorMap = colorSchemes.reduce((acc, { subject, color, textColor}) => {
        acc[subject] = { color, textColor };
        return acc
    }, {} as Record<string, { color: string, textColor: string }>);

    return schedules.map(schedule => {
        const columnIdx = days.indexOf(schedule.day) + 2
        const color = subjectColorMap[schedule.clazz.subject] ?? { color: '#ff0000', textColor: '#eeeeee' }
        const classId = schedule.clazz.classId
        const setRef = (el: any) => {
            if (scheduleRefMap && el) {
                scheduleRefMap.current.set(classId, el);
            }
        }

        return [<div
            ref = {setRef}
            key={`timetable-class-${classId}`}
            data-id={classId}
            className="timetable-class"
            style={{
                backgroundColor: color.color,
                gridRowStart: schedule.period_from,
                gridRowEnd: schedule.period_to + 1,
                gridColumn: columnIdx,
                boxShadow: `1px 1px 2px ${color.color}`,
                color: color.textColor,
            }}
        >
            <div
                key={`timetable-class-info-${columnIdx}-${schedule.period_from}`}
                className="timetable-info"
            >
                <span className='subject'>{schedule.clazz.subject}</span>
                {detail && [
                    <span className='division'>{schedule.clazz.division}반</span>,
                    <span className='teacher'>{schedule.clazz.teacher}T</span>,
                ]}
            </div>
        </div>]
    });
};

const TimetableGrid = ({schedules, colorSchemes, detail = false, scheduleRefMap}: TimetableGridProps) => {
    return (
        <div className="timetable-grid-column timetable-grid-row timetable-grid">
            {drawSchedule(schedules, colorSchemes, detail, scheduleRefMap)}
            {periods.map(period => ( // create cell of period
                <div
                    key={`timetable-grid-${period}`}
                    className="timetable-grid-cell"
                    style={{
                        gridRow: period,
                        gridColumn: 1,
                    }}
                >
                    <span>{period}</span>
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