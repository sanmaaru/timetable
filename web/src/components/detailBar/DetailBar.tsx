import React from "react";
import './DetailBar.css';
import DefaultDetailContent from "./DefaultDetail";
import ClassDetailContent from './ClassDetail';
import {Schedule} from "../../types/schedule";

interface DetailBarProps {
    schedule?: Schedule | null
    quote: string;
    source: string;
    image: string;
}

const DetailBar = ({schedule, quote, source, image}: DetailBarProps) => {
    const detailContent = (() => {
        if(schedule == null) {
            return <DefaultDetailContent quote={quote} source={source} image={image}/>
        } else {
            return <ClassDetailContent schedule={schedule}/>
        }
    })()

    return (
        <div className="detail-bar">
            <div className="title-wrapper">
                <span className="title">Details</span>
            </div>
            <div className="container">
                {detailContent}
            </div>
        </div>
    )
}

export default DetailBar;