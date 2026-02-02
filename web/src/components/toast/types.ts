export type ToastType = 'info' | 'success' | 'error'

export interface Toast {
    id: string;
    message: string;
    type: ToastType;
}

export interface ToastContextType {
    addToast: (message: string, type: ToastType) => void;
    removeToast: (id: string) => void;
}