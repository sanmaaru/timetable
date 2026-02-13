import React, {useMemo} from "react";
import {createContext, ReactNode, useCallback, useContext, useState} from "react";
import {Toast, ToastContextType, ToastType} from "./types";
import {FloatingPortal} from "@floating-ui/react";
import ToastItem from "./ToastItem";
import './ToastContainer.css'


const ToastContext = createContext<ToastContextType | null>(null);

interface ToastProviderProps {
    children: ReactNode;
}

const ToastProvider = ({ children }: ToastProviderProps) => {
    const [toasts, setToasts] = useState<Toast[]>([]);

    const removeToast = useCallback((id: number) => {
        setToasts((prev) => prev.filter((toast) => toast.id !== id));
    }, [])

    const addToast = useCallback((message: string, type: ToastType = 'info') => {
        const id = Date.now()
        setToasts((prev) => [{ id, message, type }, ...prev]);

        setTimeout(() => {
            removeToast(id);
        }, 3000)
    }, [removeToast])

    const contextValue = useMemo(() => ({
        addToast, removeToast
    }), [addToast, removeToast]);

    return (
        <ToastContext.Provider value={contextValue}>
            {children}

            <FloatingPortal>
                <div className='toast-container'>
                    {toasts.map((toast) => (
                        <ToastItem key={toast.id.toString()} toast={toast} onRemove={removeToast}/>
                    ))}
                </div>
            </FloatingPortal>
        </ToastContext.Provider>
    )
}

const useToast = (): ToastContextType => {
    const context = useContext(ToastContext);
    if (!context) {
        throw new Error('useToast must be used within ToastProvider');
    }
    return context
}

export { ToastProvider, useToast };