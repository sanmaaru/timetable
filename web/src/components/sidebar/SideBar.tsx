import React from 'react';
import './SideBar.css';
import SideBarButton from './SideBarButton';
import logo from '../../resources/logo.svg';
import {useNavigate} from "react-router-dom";


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
    const [activeButton, setActiveButton] = React.useState<string>('null'); // null state mean client do not select any menu --> main menu
    const navigate = useNavigate();

    const handleButtonClick = (id: LocationKey | null) => {
        if (id === null) {
            setActiveButton('null');
            navigate('/');
            return;
        }

        setActiveButton(id);
        navigate(locations[id]);
    };

    const buttonList: SideBarButton[] = [
        { id: "account", label: "계정", icon: "icn_account.png" },
        { id: "theme", label: "테마", icon: "icn_theme.png" },
    ];

    return (
        <aside className="sidebar">
            <div className="logo-circle" onClick={() => handleButtonClick(null)}>
                <img className="logo" src={logo}  alt="시간표 홈" />
            </div>
            <nav className="sidbar-menu">
                {buttonList.map((button) => (
                    <SideBarButton
                        id={button.id}
                        icon={'/assets/icon/' + button.icon}
                        label={button.label}
                        isActive={activeButton === button.id}
                        onClick={() => handleButtonClick(button.id)}
                    />
                ))}
            </nav>
        </aside>
    );
};

export default SideBar;