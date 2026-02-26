import React from 'react';
import style from './SimpleButton.module.css';

interface SimpleButtonProps {
    children: string;
    onClick?: () => void;
    className?: string;
}

const SimpleButton = ({children, onClick, className}: SimpleButtonProps) => {
    return (
        <button className={`${className} ${style.simpleButton}`} onClick={onClick}>
            {children}
        </button>
    )
}

export default SimpleButton;