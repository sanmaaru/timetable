import React from "react";
import './SideBarButton.css';

interface SideBarButtonProps {
    id: string;
    icon: string;
    label: string;
    isActive: boolean;
    onClick: () => void;

}

const SideBarButton = ({id, icon, label, isActive, onClick}: SideBarButtonProps) => {
    const active = isActive ? 'active' : ''

    return (
        <button
            type="button"
            className={`sidebar-button ${id} ${active}`}
            onClick={onClick} // TODO: we need to add common action on the button
        >
            <img className={`sidebar-button-icon ${id} ${active}`} alt={label} src={icon} />
            {label}
        </button>
    );
};

export default SideBarButton;