import React from "react";
import style from './DefaultDetail.module.css'

interface DefaultDetailContentProps {
    quote: string;
    source: string;
    // image: string;
}

const DefaultDetail= ({quote, source}: DefaultDetailContentProps) => {
    return (
        <div className={style.defaultDetail}>
            <span className={style.alert}>세부 내용을 볼 과목을 <br/> 선택해 주세요</span>
            {/*<img className='detail-image' src={image} alt=''/>*/}
            <div className={style.quoteContainer}>
                <span>{quote}</span>
                <span>- {source}</span>
            </div>
        </div>
    );
}

export default DefaultDetail;