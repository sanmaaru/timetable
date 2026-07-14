import React from "react";
import style from './DetailBar.module.css';
import DefaultDetailContent from "./DefaultDetail";
import ClassDetailContent from './ClassDetail';
import {Schedule} from "../../types/schedule";
import {Quote} from "../../util/quote";

interface DetailBarProps {
    schedule?: Schedule | null
    quote: Quote | null;
}

const DetailBar = ({schedule, quote}: DetailBarProps) => {
    const detailContent = (() => {
        if(schedule == null) {
            return <DefaultDetailContent quote={quote}/>
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