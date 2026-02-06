import React from "react";
import './DeleteConfirmDialog.css'
import {DialogContextType} from "./DialogProvider";

export interface DeleteConfirmDialogProps {
    context: DialogContextType
    content: string;
    onConfirm: () => void;
}

const DeleteConfirmDialog = ( { context: dialogContext, content, onConfirm }: DeleteConfirmDialogProps) => {
    const { close } = dialogContext;
    const handleConfirm =  () => {
        onConfirm()
        close()
    }

    return (
        <div
            className="delete-confirm-dialog"
            role="dialog"
            aria-modal="true"
        >
            <span>! 정말로 삭제하시겠습니까?</span>
            <span>{content}</span>
            <div>
                <button onClick={close}>취소</button>
                <button onClick={handleConfirm}>삭제</button>
            </div>
        </div>
    )
}

export default DeleteConfirmDialog;