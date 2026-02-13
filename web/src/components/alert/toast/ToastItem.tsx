import React from "react";
import {Toast} from "./types";
import './ToastItem.css';
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
        <div className="toast-item">
            <span style={{ color: textColor }}>{message}</span>
            <IconButton onClick={() => onRemove(id)}>
                <Close/>
            </IconButton>
        </div>
    )
}

export default ToastItem;