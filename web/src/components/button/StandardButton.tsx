import React from "react";
import './StandardButton.css'

interface StandardButtonProps {
    label: string;
    loading: boolean;
    type: 'submit' | 'reset' | 'button' | undefined;
    onClick?: () => void;
}

const StandardButton = ({label, type, loading, onClick}: StandardButtonProps) => (
    <button
        className={`standard-button ${loading? 'loading' : ''}`}
        type={type}
        onClick={onClick}
    >
        {label}
    </button>
)

export default StandardButton;