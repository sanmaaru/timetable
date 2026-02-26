import React from "react";
import style from './StandardButton.module.css'

interface StandardButtonProps {
    label: string;
    loading: boolean;
    type: 'submit' | 'reset' | 'button' | undefined;
    onClick?: () => void;
    className?: string;
}

const StandardButton = ({label, type, loading, onClick, className}: StandardButtonProps) => (
    <button
        className={`${style.standardButton} ${loading? style.loading : ''} ${className}`}
        type={type}
        onClick={onClick}
    >
        {label}
    </button>
)

export default StandardButton;