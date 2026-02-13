import {createContext, ReactNode, useCallback, useContext, useMemo, useState} from "react";
import {FloatingOverlay, FloatingPortal} from "@floating-ui/react";

export interface DialogContextType {
    open: (content: ReactNode) => void;
    close: () => void;
    isOpen: boolean;
}

const DialogContext = createContext<DialogContextType | null>(null)

interface DialogProviderProps {
    children: ReactNode;
}

const DialogProvider = ({ children }: DialogProviderProps) => {
    const [isOpen, setIsOpen] = useState<boolean>(false);
    const [dialogContent, setDialogContent] = useState<ReactNode | null>(null);

    const open = useCallback((content: ReactNode) => {
        setDialogContent(content);
        setIsOpen(true);
    }, []);

    const close = useCallback(() => {
        setDialogContent(null);
        setIsOpen(false);
    }, [])

    const contextValue = useMemo(() => ({
        open, close, isOpen
    }), [open, close, isOpen]);

    return (
        <DialogContext.Provider value={contextValue}>
            {children}
            {isOpen && (<FloatingPortal>
                <FloatingOverlay
                    lockScroll
                    onMouseDown={(e) => {
                        if (e.target === e.currentTarget)
                            close()
                    }}
                    style={{
                        backgroundColor: `rgba(0, 0, 0, 0.6)`,
                        display: "grid",
                        placeItems: "center",
                        zIndex: 1000
                    }}
                >
                    {dialogContent}
                </FloatingOverlay>
            </FloatingPortal>)}
        </DialogContext.Provider>
    )
}

const useDialog = (): DialogContextType => {
    const context = useContext(DialogContext)
    if (!context) {
        throw Error('useDialog must be used within DialogProvider')
    }

    return context
}

export { DialogProvider, useDialog };