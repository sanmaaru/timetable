import React, {forwardRef, useImperativeHandle, useState} from "react";
import './DeleteConfirmDialog.css'
import {
    FloatingFocusManager,
    FloatingOverlay,
    FloatingPortal,
    useDismiss,
    useFloating,
    useInteractions,
    useRole
} from "@floating-ui/react";

export interface DeleteConfirmDialogRef {
    show: (params: { onConfirm: () => void }) => void;
    close: () => void;
}

export interface DeleteConfirmDialogProps {
    content: string
}

const DeleteConfirmDialog = forwardRef(({ content }: DeleteConfirmDialogProps, ref) => {
    const [isOpen, setIsOpen] = useState(false);
    const [onConfirm, setOnConfirm] = useState<(() => void) | null>(null);

    useImperativeHandle(ref, () => ({
        show: (params: { onConfirm: () => void }) => {
            setOnConfirm(() => params.onConfirm);
            setIsOpen(true);
        },
        close: () => {
            setIsOpen(false)
        }
    }));

    const { refs, context } = useFloating({
        open: isOpen,
        onOpenChange: setIsOpen
    })

    const dismiss = useDismiss(context, { outsidePress: true });
    const role = useRole(context);
    const { getFloatingProps } = useInteractions([dismiss, role])

    const handleConfirm = () => {
        if(onConfirm) onConfirm();
        setIsOpen(false);
    }

    if(!isOpen)
        return null;

    return (
        <FloatingPortal>
            <FloatingOverlay
                lockScroll
                style={{
                    backgroundColor: `rgba(0, 0, 0, 0.6)`,
                    display: "grid",
                    placeItems: "center",
                    zIndex: 1000
                }}
            >
                <FloatingFocusManager context={context}>
                    <div
                        ref={refs.setFloating}
                        {...getFloatingProps()}
                        className="delete-confirm-dialog"
                    >
                        <span> ! 정말로 삭제하시겠습니까?</span>
                        <span>{content}</span>
                        <div>
                            <button onClick={() => setIsOpen(false)}>취소</button>
                            <button onClick={handleConfirm}>삭제</button>
                        </div>
                    </div>
                </FloatingFocusManager>
            </FloatingOverlay>
        </FloatingPortal>
    )
})

export default DeleteConfirmDialog;