import React from 'react';
import StandardInput from "../components/login/StandardInput";
import './Login.css'
import StandardButton from "../components/login/StandardButton";
import TitleLogo from "../components/TitleLogo";
import PasswordInput from "../components/login/PasswordInput";

function Login() {
    return (
        <div id="login">
            <TitleLogo/>
            <div className='panel'>
                <div className="container">
                    <div className='title'>
                        <span className='welcome'>반갑습니다!</span>
                        <span className='login-alert'>로그인을 위해서 아이디와 패스워드를 입력해 주세요</span>
                    </div>
                    <div className='input-area'>
                        <StandardInput placeHolder={'username'} invalid={false}/>
                        <PasswordInput placeHolder={'password'} invalid={false}/>
                        <StandardButton label={'로그인'} onClick={() => {}}/>
                    </div>
                    <div className='divider'/>
                    <div className='additional'>
                        <a href='' className='text-link'>아이디 혹은 비밀번호를 잊어버렸습니다</a>
                        <span className='sign-up'>계정이 아직 없으신가요?</span>
                        <a href='/signup' className='text-link sign-up'>회원가입</a>
                    </div>
                </div>
            </div>
            <img className='background' src={'/assets/image/background_login.png'} alt=''/>
        </div>
    );
}

export default Login;