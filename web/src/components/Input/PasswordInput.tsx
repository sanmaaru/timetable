import React from 'react';
import style from './StandardInput.module.css';
import passwordStyle from './PasswordInput.module.css';
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
            return <span className={style.errorMessage}>{errorMessage}</span>
    }

    return (
        <div className={`${passwordStyle.passwordInput} ${style.standardInput} ${errorMessage? style.invalid : ''}`}>
            <input
                type={visibleTag}
                autoComplete='off'
                {...registration}
                required
                className={style.input}
            />
            <span className={style.placeholder}>{placeHolder}</span>
            <img src={
                visible ? 'assets/icon/icn_invisible.png' : '/assets/icon/icn_visible.png'
            } alt='' onClick={toggleVisible}/>
            {errorMessageBox()}
        </div>
    )
}

export default PasswordInput;
