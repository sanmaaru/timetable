import React from 'react';
import './StandardInput.css';

interface StandardInputProps {
    placeHolder: string;
}

const StandardInput = ({placeHolder}: StandardInputProps) => {
    return (
        <div className='standard-input'>
            <input className='input' type='text' autoComplete='off' class='input' required/>
            <span className='label'>{placeHolder}</span>
        </div>
    )
}

export default StandardInput;