import React from 'react';
import style from './TitleLogo.module.css';
import Logo from '../resources/logo.svg?react'

interface TitleLogoProps {
    className?: string;
}

const TitleLogo = ({className}: TitleLogoProps) => {
    return (
        <div className={`${className} ${style.logo}`}>
            <span>Timetable</span>
            <Logo/>
            <span>for Gwangju Science Academy</span>
        </div>
    )
}

export default TitleLogo;