import React from "react";
import './StandardButton.css'

interface StandardButtonProps {

    label: string;
    onClick: () => void;

}

const StandardButton = ({label, onClick}: StandardButtonProps) => (
    <button
        className='standard-button'
        type='button'
        onClick={onClick}
    >
        {label}
    </button>
)

export default StandardButton;