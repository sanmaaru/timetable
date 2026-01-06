import React from "react";
import './LoginButton.css'

interface LoginButtonProps {

    label: string;
    onClick: () => void;

}

const LoginButton = ({label, onClick}: LoginButtonProps) => (
    <button
        className='login-button'
        type='button'
        onClick={onClick}
    >
        {label}
    </button>
)

export default LoginButton;