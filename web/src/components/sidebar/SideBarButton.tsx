import React from "react";
import style from './SideBarButton.module.css';

interface SideBarButtonProps {
    id: string;
    icon: string;
    label?: string;
    isActive: boolean;
    onClick: () => void;

}

const SideBarButton = ({id, icon, label, isActive, onClick}: SideBarButtonProps) => {
    const active = isActive ? style.active : ''

    return (
        <button
            key={`sidebar-button-${id}`}
            type="button"
            className={`${style.sidebarButton} ${id} ${active}`}
            onClick={onClick}
        >
            <img className={`${style.sidebarButtonIcon} ${id}`} alt={label} src={icon} />
            {label}
        </button>
    );
};

export default SideBarButton;