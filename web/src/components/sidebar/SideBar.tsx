import React from 'react';
import './SideBar.css';
import logo from '../../../public/assets/logo.svg'
import SideBarButton from './SideBarButton';

interface SideBarButton {
    id: string;
    icon: string;
    label: string;
}

const SideBar = () => {
    // this state saves which button is clicked
    const [activeButton, setActiveButton] = React.useState<string>('null'); // null state mean client do not select any menu --> main menu

    const handleButtonClick = (id: string) => {
        setActiveButton(id);
    };

    const buttonList: SideBarButton[] = [
        { id: "account", label: "계정", icon: "icn_account.png" },
        { id: "theme", label: "테마", icon: "icn_theme.png" },
        { id: "bug_report", label: "버그 제보", icon: "icn_bug.png" },
    ];

    return (
        <aside className="sidebar">
            <div className="logo-circle">
                <img className="logo" src={logo}  alt="시간표 홈"/>
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