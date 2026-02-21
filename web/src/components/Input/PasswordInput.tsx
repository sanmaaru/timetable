import React from 'react';
import './StandardInput.css';
import './PasswordInput.css';
import {UseFormRegisterReturn} from "react-hook-form";

interface PasswordInputProps {
    placeHolder: string;
    registration: UseFormRegisterReturn
    errorMessage?: string | undefined
}

const PasswordInput = ({placeHolder, registration, errorMessage}: PasswordInputProps) => {
    const [visible, setVisible] = React.useState(false);
    const toggleVisible = () => {
        setVisible((prev) => !prev);
    }
    const visibleTag = visible ? 'text' : 'password';
    const errorMessageBox = () => {
        if (errorMessage)
            return <span className='error-message'>{errorMessage}</span>
    }

    return (
        <div className={`password-input standard-input ${errorMessage? 'invalid' : ''}`}>
            <input
                type={visibleTag}
                autoComplete='off'
                {...registration}
                required
            />
            <span className='placeholder'>{placeHolder}</span>
            <img src={
                visible ? 'assets/icon/icn_invisible.png' : '/assets/icon/icn_visible.png'
            } alt='' onClick={toggleVisible}/>
            {errorMessageBox()}
        </div>
    )
}

export default PasswordInput;
