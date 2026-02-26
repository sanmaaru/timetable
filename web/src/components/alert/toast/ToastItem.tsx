import React from "react";
import {Toast} from "./types";
import style from './ToastItem.module.css';
import IconButton from "../../button/IconButton";
import Close from '../../../resources/icon/icn_close.svg?react'
import {toastTextColor} from "../../../constants/colors";

interface ToastItemProps {
    toast: Toast;
    onRemove: (id: number) => void;
}

const ToastItem = ({ toast, onRemove }: ToastItemProps) => {
    const { id, message, type } = toast;

    const textColor = toastTextColor[type];

    return (
        <div className={style.toastItem}>
            <span className={style.content} style={{ color: textColor }}>{message}</span>
            <IconButton className={style.button} onClick={() => onRemove(id)}>
                <Close/>
            </IconButton>
        </div>
    )
}

export default ToastItem;