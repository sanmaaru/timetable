import {DialogContextType} from "./DialogProvider";
import React from "react";
import './DefaultDialog.css'

interface DefaultDialogProps {
    context: DialogContextType
    color?: string
    children: string;
    onConfirm: () => void;
    onSuccess: () => void;
}

const SaveDialog = ({context, color, children, onSuccess, onConfirm}: DefaultDialogProps) => {
    const { close } = context;

    const handleQuit = () => {
        onSuccess();
        close()
    }

    const handleConfirm =  () => {
        onConfirm()
        close()
        onSuccess()
    }

    const formattedChildren = children.replace(/\\n/g, '\n')

    return (
        <div
            className="DefaultDialog SaveDialog"
            role="dialog"
            aria-modal='true'
        >
            <span style={{ color: color }}>! 저장하시겠습니까?</span>
            <span>{formattedChildren}</span>
            <div>
                <button onClick={handleQuit}>저장하지 않기</button>
                <button onClick={handleConfirm}>저장하기</button>
            </div>
        </div>
    )
}

export default SaveDialog;
