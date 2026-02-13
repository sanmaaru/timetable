import {DialogContextType} from "./DialogProvider";
import React from "react";
import './DefaultDialog.css'

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
            className="DefaultDialog"
            role="dialog"
            aria-modal='true'
        >
            <span style={{ color: color }}>{title}</span>
            <span>{formattedChildren}</span>
            <div>
                <button onClick={close}>취소</button>
                <button style={{color: color}} onClick={handleConfirm}>{confirm}</button>
            </div>
        </div>
    )
}

export default DefaultDialog;