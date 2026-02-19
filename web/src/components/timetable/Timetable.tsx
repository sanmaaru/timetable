import React, {useCallback, useEffect, useRef, useState} from "react";
import './Timetable.css';
import {Schedule} from "../../types/schedule";
import TimetableGrid from "./TimetableGrid";
import {Theme} from "../../types/theme";
import TimetableHeader from "./TimetableHeader";

interface TimetableProps {
    name: string
    schedules: Schedule[];
    theme: Theme;
    focus: string | null;
    setFocus: (value: string | null) => void;
}

const Timetable = ({name, schedules, theme, focus, setFocus}: TimetableProps) => {
    const itemsRef = useRef(new Map());

    const handleContainerClick = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
        const target = (e.target as HTMLElement).closest('[data-id]');

        if (!target) {
            setFocus(null)
            return;
        }

        const classId = target.getAttribute('data-id')
        if (!classId) {
            setFocus(null)
            return;
        }

        const ref = itemsRef.current.get(classId);
        if (ref)
            setFocus(classId)
    }, [itemsRef])

    useEffect(() => {
        itemsRef.current.forEach((element) => {
            element?.classList.remove('focus');
        })

        if (focus) {
            const current = itemsRef.current.get(focus)
            if (current)
                current.classList.add('focus');
        }

    }, [focus])

    return (<div className="timetable" onClick={handleContainerClick}>
        <div className='timetable-title'>
            <span className='title'>시간표</span>
            <span className='name'> - {name}</span>
        </div>
        <TimetableHeader/>
        <TimetableGrid schedules={schedules} colorSchemes={theme.colorSchemes} detail={true} scheduleRefMap={itemsRef}/>
    </div>);
}

export default Timetable