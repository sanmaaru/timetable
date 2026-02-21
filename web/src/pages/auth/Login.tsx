import React from 'react';
import StandardInput from "../../components/Input/StandardInput";
import './Login.css'
import StandardButton from "../../components/button/StandardButton";
import TitleLogo from "../../components/TitleLogo";
import PasswordInput from "../../components/Input/PasswordInput";
import {Link, useNavigate} from "react-router-dom";
import {useLogin} from "../../hooks/useLogin";
import {isAuthenticated} from "../../auth/auth";

function Login() {
    const navigate= useNavigate();
    if (isAuthenticated())
        navigate("/", { replace: true });

    const {
        register,
        errors,
        loading,
        globalErrorMessage,
        onSubmit
    } = useLogin()

    const createGlobalErrorMessage = () => {
        if(!globalErrorMessage)
            return

        return <span className='global-error-message'>{globalErrorMessage}</span>
    }

    return (
        <div id="login">
            <TitleLogo/>
            <div className='panel'>
                <div className="container">
                    <div className='title'>
                        <span className='welcome'>반갑습니다!</span>
                        <span className='login-alert'>로그인을 위해서 아이디와 패스워드를 입력해 주세요</span>
                    </div>
                    <form className='input-area' onSubmit={onSubmit} noValidate={true}>
                        <StandardInput
                            placeHolder={'username'}
                            registration={ register('username', {
                                required: '사용자 이름을 입력해 주세요',
                            })}
                            errorMessage={errors.username?.message}
                        />
                        <PasswordInput
                            placeHolder={'password'}
                            registration={ register('password', {
                                required: '비밀번호를 입력해 주세요',
                            })}
                            errorMessage={errors.password?.message}
                        />
                        <StandardButton
                            label={loading ? '로그인 중...' : '로그인'}
                            type='submit'
                            loading={loading}
                        />
                    </form>
                    {createGlobalErrorMessage()}
                    <div className='divider'/>
                    <div className='additional'>
                        <Link to='' className='text-link'>아이디 혹은 비밀번호를 잊어버렸습니다</Link>
                        <span className='sign-up'>계정이 아직 없으신가요?</span>
                        <Link to='/signup' className={`text-link sign-up`}>회원가입</Link>
                    </div>
                </div>
            </div>
            <img className='background' src={'/assets/image/background_login.png'} alt=''/>
        </div>
    );
}

export default Login;