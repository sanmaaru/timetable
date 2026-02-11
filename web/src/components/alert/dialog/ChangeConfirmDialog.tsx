import './ChangeConfirmDialog.css';
import {DialogContextType} from "./DialogProvider";
import React from "react";

interface ChangeConfirmDialogProps {
    context: DialogContextType;
    content: string;
    onConfirm: () => void;
}

const ChangeConfirmDialog = ({context, content, onConfirm}: ChangeConfirmDialogProps) => {
    const { open, close } = context;

    const handleConfirm = () => {
        onConfirm();
        close()
    }

    return (
        <div
            className='ChangeConfirmDialog'
            role='dialog'
            aria-modal='true'
        >
            <span>! 정말로 변경하시겠습니까?</span>
            <span>{content}</span>
            <div>
                <button onClick={close}>취소</button>
                <button onClick={handleConfirm}>변경</button>
            </div>
        </div>
    )
}

export default ChangeConfirmDialog;