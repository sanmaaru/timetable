import React from "react";
import style from './ColorSchemeElement.module.css';
import {ColorScheme} from "../../types/theme";

interface ColorSchemeElementProps {
    colorScheme: ColorScheme;
    onClick: (subject: string | null) => void;
    focus: string | null;
}

const ColorSchemeElement = ({colorScheme, onClick, focus}: ColorSchemeElementProps) => {
    const { subject, color } = colorScheme;

    const handleClick = () => {
        if (focus === subject)
            onClick(null);
        else
            onClick(subject);
    }

    return (
        <div
            className={`${style.colorSchemeElement} ${focus === subject ? style.focus : ''}`}
            onClick={() => {handleClick()}}
        >
            <span>{subject}</span>
            <span>{color}</span>
            <div style={{ backgroundColor: color }}>

            </div>
        </div>
    )
}

export default ColorSchemeElement;