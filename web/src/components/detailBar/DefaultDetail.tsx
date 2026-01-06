import React from "react";
import './DefaultDetail.css'

interface DefaultDetailContentProps {
    quote: string;
    source: string;
    image: string;
}

const DefaultDetailContent= ({quote, source, image}: DefaultDetailContentProps) => {
    return (
        <div className='detail-wrapper'>
            <span className='detail-alert'>세부 내용을 볼 과목을 <br/> 선택해 주세요</span>
            <img className='detail-image' src={image} alt=''/>
            <div className='quote-container'>
                <span className='detail-quote'>{quote}</span>
                <span className='detail-source'>- {source}</span>
            </div>
        </div>
    );
}

export default DefaultDetailContent;