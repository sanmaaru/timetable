import React, {useEffect, useState} from "react";
import './ToastAlert.css';
import {offset, shift, useFloating, useTransitionStyles} from "@floating-ui/react";

interface ToastAlertProps {
    text: string;
    color: string | null;
    duration: number;
}

const ToastAlert = ({text, color, duration} : ToastAlertProps) => {
    const [isOpen, setIsOpen] = useState(false);

    const offsetY = 80;
    
    const { refs, floatingStyles, context } = useFloating({
        open: isOpen,
        onOpenChange: setIsOpen,
        placement: 'bottom',
        middleware: [
            offset(offsetY),
            shift()
        ]
    })

    const { isMounted, styles } = useTransitionStyles(context, {
        initial: { opacity: 0, transform:`translateY(${offsetY}px)`, transition: 'transform 0.2s ease-out' },
        open: { opacity: 1, transform:`translateY(0px)`, transition: 'transform 0.2s ease-out' },
        close: { opacity: 0, transform:`translateY(${offsetY}px)`, transition: 'transform 0.2s ease-out' },
    })


    return (<div

    >

    </div>)
}

export default ToastAlert;