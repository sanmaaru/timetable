import React from 'react';
import StandardInput from "../components/login/StandardInput";
import './Signup.css'
import StandardButton from "../components/login/StandardButton";
import TitleLogo from "../components/TitleLogo";
import PasswordInput from "../components/login/PasswordInput";
import {Link} from "react-router-dom";
import {useSignUp} from "../hooks/useSignUp";

function SignUp() {
    const { register, errors, password, loading, globalErrorMessage, onSubmit } = useSignUp()

    const createGlobalErrorMessage = () => {
        if(!globalErrorMessage)
            return

        return <span className='global-error-message'>{globalErrorMessage}</span>
    }

    return (
        <div id="signup">
            <TitleLogo/>
            <div className='panel'>
                <div className="container">
                    <div className='title'>
                        <span className='welcome'>환영합니다</span>
                        <span className='alert'>더 이상 시간표를 만드는데 시간을 허비하지 마세요</span>
                    </div>
                    <form className='input-area' onSubmit={onSubmit} noValidate={true}>
                        <div className='subarea'>
                            <StandardInput
                                placeHolder={'username'}
                                registration={register('username', {
                                    required: '사용자 이름을 입력해 주세요',
                                    minLength: {value: 3, message: '사용자 이름은 3글자 이상 20글자 이하여야 합니다'},
                                    maxLength: {value: 20, message: '사용자 이름은 3글자 이상 20글자 이하여야 합니다'}
                                })}
                                errorMessage={errors.username?.message}
                            />
                            <StandardInput
                                placeHolder={'email'}
                                registration={register('email', {
                                    required: '이메일을 입력해 주세요',
                                    pattern: {
                                        value: /\S+@\S+\.\S+/,
                                        message: '이메일을 입력해 주세요'
                                    }
                                })}
                                errorMessage={errors.email?.message}
                            />
                        </div>
                        <div className='subarea'>
                            <PasswordInput
                                placeHolder={'password'}
                                registration={register('password', {
                                    required: '비밀번호를 입력해 주세요',
                                    minLength: {value: 3, message: '비번은 8글자 이상이여야 합니다.'}
                                })}
                                errorMessage={errors.password?.message}
                            />
                            <PasswordInput
                                placeHolder={'rewrite password'}
                                registration={register('passwordConfirm', {
                                    validate: (value) => value == password || '비밀번호가 일치하지 않습니다'
                                })}
                                errorMessage={errors.passwordConfirm?.message}
                            />
                        </div>
                        <StandardInput
                            placeHolder={'identify token'}
                            registration={register('identifyToken', {
                                required: '인증 토큰을 입력해 주세요',
                                minLength: {value: 8, message: '인증 토큰을 입력해 주세요'},
                                maxLength: {value: 8, message: '인증 토큰을 입력해 주세요'}
                            })}
                            errorMessage={errors.identifyToken?.message}
                        />
                        <StandardButton
                            label={loading? '회원가입 중...' : '회원가입 '}
                            type={'submit'}
                            loading={loading}
                        />
                    </form>
                    {createGlobalErrorMessage()}
                    <div className='divider'/>
                    <div className='additional'>
                        <span>계정이 이미 존재하나요?</span>
                        <Link to='/login' className='text-link'>로그인</Link>
                    </div>
                </div>
            </div>
            <img className='background' src={'/assets/image/background_signup.png'} alt=''/>
        </div>
    );
}

export default SignUp;