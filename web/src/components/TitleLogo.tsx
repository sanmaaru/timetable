import React from 'react';
import './TitleLogo.css';
import logo from '../resources/logo.svg'

const TitleLogo = () => {
    return (
        <div className="title-logo">
            <span className="app-name">Timetable</span>
            <img className="logo" src={logo} alt=''/>
            <span className="subtitle">for Gwangju Science Academy</span>
        </div>
    )
}

export default TitleLogo;