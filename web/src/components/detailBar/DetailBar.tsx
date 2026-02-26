import React from "react";
import style from './DetailBar.module.css';
import DefaultDetailContent from "./DefaultDetail";
import ClassDetailContent from './ClassDetail';
import {Schedule} from "../../types/schedule";

interface DetailBarProps {
    schedule?: Schedule | null
    quote: string;
    source: string;
    // image: string;
}

const DetailBar = ({schedule, quote, source}: DetailBarProps) => {
    const detailContent = (() => {
        if(schedule == null) {
            return <DefaultDetailContent quote={quote} source={source}/>
        } else {
            return <ClassDetailContent schedule={schedule}/>
        }
    })()

    return (
        <div className={style.detailBar}>
            <div className={style.titleWrapper}>
                <span>Details</span>
            </div>
            <div className={style.container}>
                {detailContent}
            </div>
        </div>
    )
}

export default DetailBar;