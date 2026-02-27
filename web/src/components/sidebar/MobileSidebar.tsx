import React from "react";
import style from './MobileSidebar.module.css'
import {useLocation, useNavigate} from "react-router-dom";
import {getActiveId, LocationKey, locations} from "../../constants/location";
import SideBarButton from "./SideBarButton";

interface SideBarButton {
    id: LocationKey;
    icon: string;
}

const MobileSidebar = () => {
    const location = useLocation();
    const navigate = useNavigate();


    const handleButtonClick = (id: LocationKey | null) => {
        if (id === null) {
            navigate('/');
            return;
        }

        navigate(locations[id]);
    };

    const buttonList: SideBarButton[] = [
        { id: "account", icon: "icn_account.png" },
        { id: "home", icon: "logo.svg" },
        { id: "theme", icon: "icn_theme.png" },
    ]

    return (
        <nav className={style.sidebar}>
            {buttonList.map((button) => (
                <SideBarButton
                    id={button.id}
                    icon={"/assets/icon/" + button.icon}
                    label={'테스트'}
                    isActive={getActiveId(location.pathname) == button.id}
                    onClick={() => handleButtonClick(button.id)}
                />
            ))}
        </nav>
    )
}

export default MobileSidebar;