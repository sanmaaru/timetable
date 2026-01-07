import React from 'react';
import './PasswordInput.css';

interface PasswordInputProps {
    placeHolder: string;
    invalid: boolean;
}

const PasswordInput = ({placeHolder, invalid}: PasswordInputProps) => {
    const [visible, setVisible] = React.useState(false);
    const toggleVisible = () => {
        setVisible((prev) => !prev);
    }
    const visibleTag = visible ? 'text' : 'password';
    const invalidTag = invalid ? 'invalid' : '';
    return (
        <div className={`password-input ${invalidTag}`}>
            <input className='input' type={visibleTag} autoComplete='off' class='input' required/>
            <span className='label'>{placeHolder}</span>
            <img className={`visible`} src={
                visible ? 'assets/icon/icn_invisible.png' : '/assets/icon/icn_visible.png'
            } alt='' onClick={toggleVisible}/>
        </div>
    )
}

export default PasswordInput;
