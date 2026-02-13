export type ToastType = 'info' | 'success' | 'error'

export interface Toast {
    id: number;
    message: string;
    type: ToastType;
}

export interface ToastContextType {
    addToast: (message: string, type: ToastType) => void;
    removeToast: (id: number) => void;
}