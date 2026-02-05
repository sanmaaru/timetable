import React from "react";
import {Toast} from "./types";
import './ToastItem.css';

interface ToastItemProps {
    toast: Toast;
    onRemove: (id: number) => void;
}

const ToastItem = ({ toast, onRemove }: ToastItemProps) => {
    const { id, message, type } = toast;

    return (
        <div className="toast-item">
            <span>{message}</span>
            <button onClick={() => onRemove(id)}>X</button>
        </div>
    )
}

export default ToastItem;