import React from 'react';
import './StandardInput.css';
import {UseFormRegisterReturn} from "react-hook-form";

interface StandardInputProps {
    placeHolder: string;
    errorMessage?: string | undefined;
    registration: UseFormRegisterReturn;
}

const StandardInput = ({placeHolder, errorMessage, registration}: StandardInputProps) => {
    const errorMessageBox = () => {
        if (errorMessage)
            return <span className='error-message'>{errorMessage}</span>
    }

    return (
        <div className={`standard-input ${errorMessage? 'invalid' : ''}`}>
            <input
                type='text'
                autoComplete='off'
                {...registration}
                required
            />
            <span className='placeholder'>{placeHolder}</span>
            {errorMessageBox()}
        </div>
    )
}

export default StandardInput;