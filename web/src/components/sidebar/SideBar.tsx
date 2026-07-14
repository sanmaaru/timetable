import React from 'react';
import style from './SideBar.module.css';
import SideBarButton from './SideBarButton';
import {useLocation, useNavigate} from "react-router-dom";
import Logo from '../../resources/logo.svg?react'
import {getActiveId, LocationKey, locations} from "../../constants/location";

export interface SideBarButton {
    id: LocationKey;
    icon: string;
    label: string;
}

interface SideBarProps {
    sideBarButtons: SideBarButton[];
}

const SideBar = ({ sideBarButtons }: SideBarProps) => {
    // this state saves which button is clicked
    const location = useLocation();
    const navigate = useNavigate();

    const handleButtonClick = (id: LocationKey | null) => {
        if (id === null) {
            navigate('/');
            return;
        }

        navigate(locations[id]);
    };

    return (
        <aside className={style.sidebar}>
            <div className={style.logo} onClick={() => handleButtonClick(null)} title={'시간표 홈'}>
                <Logo/>
            </div>
            <nav className={style.btnArea}>
                {sideBarButtons.map((button) => (
                    <SideBarButton
                        id={button.id}
                        icon={'/assets/icon/' + button.icon}
                        label={button.label}
                        isActive={getActiveId(location.pathname) === button.id}
                        onClick={() => handleButtonClick(button.id)}
                    />
                ))}
            </nav>
        </aside>
    );
};

export default SideBar;