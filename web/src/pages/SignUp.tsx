import React from 'react';
import StandardInput from "../components/login/StandardInput";
import './Signup.css'
import StandardButton from "../components/login/StandardButton";
import TitleLogo from "../components/TitleLogo";
import PasswordInput from "../components/login/PasswordInput";

function Login() {
    return (
        <div id="signup">
            <TitleLogo/>
            <div className='panel'>
                <div className="container">
                    <div className='title'>
                        <span className='welcome'>환영합니다</span>
                        <span className='alert'>더 이상 시간표를 만드는데 시간을 허비하지 메세요</span>
                    </div>
                    <div className='input-area'>
                        <div className='subarea'>
                            <StandardInput placeHolder={'username'} invalid={false}/>
                            <StandardInput placeHolder={'email'} invalid={false}/>
                        </div>
                        <div className='subarea'>
                            <PasswordInput placeHolder={'password'} invalid={false}/>
                            <PasswordInput placeHolder={'rewrite password'} invalid={false}/>
                        </div>
                        <StandardInput placeHolder={'identify token'} invalid={false}/>
                        <StandardButton label={'회원가입'} onClick={() => {}}/>
                    </div>
                    <div className='divider'/>
                    <div className='additional'>
                        <span>계정이 이미 존재하나요?</span>
                        <a href='/login' className='text-link'>로그인</a>
                    </div>
                </div>
            </div>
            <img className='background' src={'/assets/image/background_signup.png'} alt=''/>
        </div>
    );
}

export default Login;