import React from 'react';
import style from './StandardInput.module.css';
import {UseFormRegisterReturn} from "react-hook-form";

interface StandardInputProps {
    placeHolder: string;
    errorMessage?: string | undefined;
    registration: UseFormRegisterReturn;
}

const StandardInput = ({placeHolder, errorMessage, registration}: StandardInputProps) => {
    const errorMessageBox = () => {
        if (errorMessage)
            return <span className={style.errorMessage}>{errorMessage}</span>
    }

    return (
        <div className={`${style.standardInput} ${errorMessage? style.invalid : ''}`}>
            <input
                type='text'
                autoComplete='off'
                {...registration}
                required
                className={style.input}
            />
            <span className={style.placeholder}>{placeHolder}</span>
            {errorMessageBox()}
        </div>
    )
}

export default StandardInput;