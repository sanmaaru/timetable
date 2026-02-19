import {Period, Schedule} from "../../types/schedule";
import './ClassDetail.css';
import {getGrade, scheduleToString} from "../../util/common";
import {Student} from "../../types/class";

interface ClassDetailProps {
    schedule: Schedule
}

const ClassDetail = ({schedule}: ClassDetailProps) => {
    const drawClassmates = (classmates: Student[]) => {
        return classmates.map((classmate) => {
            var info = `${getGrade(classmate.generation)}${classmate.clazz}`
            if (classmate.number < 10)
                info += `0${classmate.number}`;
            else
                info += `${classmate.number}`;

            return (<div>
                <span>{classmate.name}</span>
                <span>{info}</span>
            </div>)
        })
    }

    return (
        <div className='ClassDetail'>
            <header>
                <span>{schedule.clazz.subject}</span>
            </header>
            <div className='detail'>
                <div>
                    <span>분반</span>
                    <span>{schedule.clazz.division}반</span>
                </div>
                <div>
                    <span>선생님</span>
                    <span>{schedule.clazz.teacher}Tr</span>
                </div>
                <div>
                    <span>강의실</span>
                    <span>{schedule.clazz.room}</span>
                </div>
                <div>
                    <span>수업 시간</span>
                    <span>{scheduleToString(schedule.day, schedule.period_from, schedule.period_to)}</span>
                </div>
            </div>
            <div className='divider'/>
            <div className='classmates'>
                <span>같이 듣는 학생</span>
                {drawClassmates(schedule.clazz.classmates)}
            </div>
        </div>
    )
}

export default ClassDetail