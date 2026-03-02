import React from 'react'
import style from './MobileDetailDialog.module.css'
import ClassDetail from "../../detailBar/ClassDetail";
import {Schedule} from "../../../types/schedule";
import IconButton from "../../button/IconButton";
import Close from '../../../resources/icon/icn_close.svg?react'
import {DialogContextType} from "./DialogProvider";

interface MobileDetailDialogProps {
    context: DialogContextType
    schedule: Schedule;
}

const MobileDetailDialog = ({schedule, context}: MobileDetailDialogProps) => {
    const handleClickClose = () => {
        context.close()
    }

    return (
        <div className={style.detailDialog}>
            <ClassDetail schedule={schedule}/>
            <IconButton onClick={handleClickClose} className={style.button}>
                <Close/>
            </IconButton>
        </div>
    )
}

export default MobileDetailDialog