import React from "react";
import './DetailBar.css';
import {Class, ClassDetail} from "../../types/class";
import DefaultDetailContent from "./DefaultDetail";
import ClassDetailContent from './ClassDetail';

interface DetailBarProps {
    classInfo?: Class
    detail?: ClassDetail;
    quote: string;
    source: string;
    image: string;
}

const DetailBar = ({classInfo, detail, quote, source, image}: DetailBarProps) => {
    const detailContent = (() => {
        if(classInfo == null || detail == null) {
            return <DefaultDetailContent quote={quote} source={source} image={image}/>
        } else {
            return <ClassDetailContent classInfo={classInfo} detail={detail}/>
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