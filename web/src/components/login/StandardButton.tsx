import React from "react";
import './StandardButton.css'

interface StandardButtonProps {
    label: string;
    loading: boolean;
    type: 'submit' | 'reset' | 'button' | undefined;
}

const StandardButton = ({label, type, loading}: StandardButtonProps) => (
    <button
        className={`standard-button ${loading? 'loading' : ''}`}
        type={type}
    >
        {label}
    </button>
)

export default StandardButton;