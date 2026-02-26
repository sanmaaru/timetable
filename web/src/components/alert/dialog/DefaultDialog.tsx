import {DialogContextType} from "./DialogProvider";
import React from "react";
import style from './DefaultDialog.module.css'

interface DefaultDialogProps {
    context: DialogContextType
    title: string
    color?: string
    children: string;
    onConfirm: () => void;
    confirm: string
}

const DefaultDialog = ({context, title, color, children, onConfirm, confirm}: DefaultDialogProps) => {
    const { close } = context;
    const handleConfirm =  () => {
        onConfirm()
        close()
    }

    const formattedChildren = children.replace(/\\n/g, '\n')

    return (
        <div
            className={style.defaultDialog}
            role="dialog"
            aria-modal='true'
        >
            <span className={`${style.span} ${style.title}`} style={{ color: color }}>{title}</span>
            <span className={`${style.span} ${style.content}`}>{formattedChildren}</span>
            <div className={style.btnArea}>
                <button className={`${style.button}`} onClick={close}>취소</button>
                <button className={`${style.button}`} style={{color: color}} onClick={handleConfirm}>{confirm}</button>
            </div>
        </div>
    )
}

export default DefaultDialog;