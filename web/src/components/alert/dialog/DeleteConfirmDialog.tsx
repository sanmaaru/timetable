import React from "react";
import './DeleteConfirmDialog.css'
import {FloatingFocusManager, useDismiss, useFloating, useInteractions, useRole} from "@floating-ui/react";
import {DialogContextType} from "./DialogProvider";

export interface DeleteConfirmDialogProps {
    context: DialogContextType
    content: string;
    onConfirm: () => void;
}

const DeleteConfirmDialog = ( { context: dialogContext, content, onConfirm }: DeleteConfirmDialogProps) => {
    const { close, isOpen } = dialogContext;
    const { refs, context } = useFloating({
        open: isOpen,
        onOpenChange: (value) => {
            if (!value)
                close()
        }
    })

    const handleConfirm =  () => {
        onConfirm()
        close()
    }

    const dismiss = useDismiss(context, { outsidePress: true });
    const role = useRole(context);
    const { getFloatingProps } = useInteractions([dismiss, role])

    return (
        <FloatingFocusManager context={context}>
            <div
                ref={refs.setFloating}
                {...getFloatingProps()}
                className="delete-confirm-dialog"
            >
                <span> ! 정말로 삭제하시겠습니까?</span>
                <span>{content}</span>
                <div>
                    <button onClick={close}>취소</button>
                    <button onClick={handleConfirm}>삭제</button>
                </div>
            </div>
        </FloatingFocusManager>
    )
}

export default DeleteConfirmDialog;