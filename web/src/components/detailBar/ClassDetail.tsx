import {Schedule} from "../../types/schedule";
import style from './ClassDetail.module.css';
import {getGrade} from "../../util/common";
import {Student} from "../../types/class";

interface ClassDetailProps {
    schedule: Schedule
}

const ClassDetail = ({schedule}: ClassDetailProps) => {
    const drawClassmates = (classmates: Student[]) => {
        return classmates.map((classmate) => {
            let info = `${getGrade(classmate.generation)}${classmate.clazz}`
            if (classmate.number < 10)
                info += `0${classmate.number}`;
            else
                info += `${classmate.number}`;

            return (<div className={style.classmateElement}>
                <span>{classmate.name}</span>
                <span>{info}</span>
            </div>)
        })
    }

    return (
        <div className={style.classDetail}>
            <header className={style.header}>
                <span>{schedule.clazz.subject}</span>
            </header>
            <div className={style.detail}>
                <div className={style.content}>
                    <span>분반</span>
                    <span>{schedule.clazz.division}반</span>
                </div>
                <div className={style.content}>
                    <span>선생님</span>
                    <span>{schedule.clazz.teacher}Tr</span>
                </div>
                <div className={style.content}>
                    <span>강의실</span>
                    <span>{schedule.clazz.room}</span>
                </div>
            </div>
            <div className={style.divider}/>
            <div className={style.classmates}>
                <span>같이 듣는 학생</span>
                {drawClassmates(schedule.clazz.classmates)}
            </div>
        </div>
    )
}

export default ClassDetail