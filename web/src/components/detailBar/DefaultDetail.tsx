import React from "react";
import style from './DefaultDetail.module.css'
import {Quote} from "../../util/quote";

interface DefaultDetailContentProps {
    quote: Quote | null;
}

const DefaultDetail= ({quote}: DefaultDetailContentProps) => {
    const content = quote?.quote ?? '달을 향해 쏴라 빗나가도 별이 될테니'
    const source = quote?.source ?? '레스 브라운'

    return (
        <div className={style.defaultDetail}>
            <span className={style.alert}>세부 내용을 볼 과목을 <br/> 선택해 주세요</span>
            <div className={style.quoteContainer}>
                <span>{content}</span>
                <span>- {source}</span>
            </div>
        </div>
    );
}

export default DefaultDetail;