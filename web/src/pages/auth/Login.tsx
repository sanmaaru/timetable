import React from 'react';
import StandardInput from "../../components/Input/StandardInput";
import style from './Login.module.css'
import StandardButton from "../../components/button/StandardButton";
import TitleLogo from "../../components/TitleLogo";
import PasswordInput from "../../components/Input/PasswordInput";
import {Link, useNavigate} from "react-router-dom";
import {useLogin} from "../../hooks/useLogin";
import {isAuthenticated} from "../../auth/auth";
import {useIsMobile} from "../../hooks/useMediaQuery";

function Login() {
    const navigate= useNavigate();
    const isMobile = useIsMobile();
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

        return <span className={style.globalErrorMessage}>{globalErrorMessage}</span>
    }

    return (
        <div className={style.loginPage}>
            <TitleLogo className={style.titleLogo} />
            <div className={style.panel}>
                <div className={style.container}>
                    <div className={style.title}>
                        <span>반갑습니다!</span>
                        <span>로그인을 위해서 아이디와 패스워드를 입력해 주세요</span>
                    </div>
                    <form className={style.inputArea} onSubmit={onSubmit} noValidate={true}>
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
                    <div className={style.divider}/>
                    <div className={style.footer}>
                        <Link to='' className={style.textLink}>아이디 혹은 비밀번호를 잊어버렸습니다</Link>
                        <span className={style.signUp}>계정이 아직 없으신가요?</span>
                        <Link to='/signup' className={`${style.textLink} ${style.signUp}`}>회원가입</Link>
                    </div>
                </div>
            </div>
            {!isMobile && <div className={`${style.backgroundBox} ${style.loginBg}`}/>}
        </div>
    );
}

export default Login;