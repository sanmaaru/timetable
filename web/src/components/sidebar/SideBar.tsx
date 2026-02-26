import React from 'react';
import style from './SideBar.module.css';
import SideBarButton from './SideBarButton';
import {useLocation, useNavigate} from "react-router-dom";
import Logo from '../../resources/logo.svg?react'

const locations = {
    account: '/account',
    theme: '/theme',
} as const;
type LocationKey = keyof typeof locations;

interface SideBarButton {
    id: LocationKey;
    icon: string;
    label: string;
}

const SideBar = () => {
    // this state saves which button is clicked
    const location = useLocation();
    const navigate = useNavigate();

    const getActiveId = () => {
        for (const [key, path] of Object.entries(locations)) {
            if (location.pathname.startsWith(path))
                return key as LocationKey;
        }
        return 'null';
    }

    const handleButtonClick = (id: LocationKey | null) => {
        if (id === null) {
            navigate('/');
            return;
        }

        navigate(locations[id]);
    };

    const buttonList: SideBarButton[] = [
        { id: "account", label: "계정", icon: "icn_account.png" },
        { id: "theme", label: "테마", icon: "icn_theme.png" },
    ];

    return (
        <aside className={style.sidebar}>
            <div className={style.logo} onClick={() => handleButtonClick(null)} title={'시간표 홈'}>
                <Logo/>
            </div>
            <nav>
                {buttonList.map((button) => (
                    <SideBarButton
                        id={button.id}
                        icon={'/assets/icon/' + button.icon}
                        label={button.label}
                        isActive={getActiveId() === button.id}
                        onClick={() => handleButtonClick(button.id)}
                    />
                ))}
            </nav>
        </aside>
    );
};

export default SideBar;