import React from 'react';
import './SimpleButton.css';

interface SimpleButtonProps {
    children: string;
    onClick?: () => void;
}

const SimpleButton = ({children, onClick}: SimpleButtonProps) => {
    return (
        <button className="SimpleButton" onClick={onClick}>
            {children}
        </button>
    )
}

export default SimpleButton;