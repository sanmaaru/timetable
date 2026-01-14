import {SubmitHandler, useForm} from "react-hook-form";
import React, {useState} from "react";
import {publicAxiosClient} from "../api/axiosClient";
import {setTokens} from "../auth/auth";
import {replace, useNavigate} from "react-router-dom";
import {AxiosError} from "axios";

export interface LoginInput {
    username: string;
    password: string;
}

const ERROR_MESSAGES = {
    GENERAL: '로그인 과정 중에 오류가 발생하였습니다. 관리자에게 제보해 주세요.',
    PASSWORD: '비밀번호가 일치하지 않습니다',
    USERNAME: '존재하지 않는 사용자 이름입니다.'
}

const INVALID_TOKEN = {
    USERNAME: 'username',
    PASSWORD: 'password',
}

const handleApiError = (invalid: string) => {
    let object, message
    switch (invalid) {
        case INVALID_TOKEN.USERNAME:
            object = 'username'
            message = ERROR_MESSAGES.USERNAME
            break;

        case INVALID_TOKEN.PASSWORD:
            object = 'password'
            message = ERROR_MESSAGES.PASSWORD
            break;

        default:
            object = null
            message = ERROR_MESSAGES.GENERAL
            break;
    }

    return { object, message }
}

export const useLogin = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [globalErrorMessage, setGlobalErrorMessage] = useState<string>('');

    const {
        register,
        handleSubmit,
        formState: { errors, isValid },
        setError
    } = useForm({
        mode: 'onBlur',
        reValidateMode: 'onChange',
    });

    const loginHandler: SubmitHandler<LoginInput> = async (data) => {
        setLoading(true);
        setGlobalErrorMessage('');

        try {
            const response = await publicAxiosClient.post("/auth/login", {
                username: data.username,
                password: data.password,
            });

            const {access_token, refresh_token} = response.data

            setTokens(access_token, refresh_token)
            navigate('/', {replace: true});
        } catch(error: any) {
            if (!error.response || error.response.status !== 401) {
                setGlobalErrorMessage(ERROR_MESSAGES.GENERAL);
                return
            }

            const invalid = error.response.data.detail.invalid;
            const { object, message } = handleApiError(invalid);
            if (object == null) {
                setGlobalErrorMessage(ERROR_MESSAGES.GENERAL);
            } else {
                setError(object, {
                    type: 'server',
                    message: message,
                })
            }
        } finally {
            setLoading(false);
        }
    }

    return {
        register,
        errors,
        loading,
        globalErrorMessage,
        onSubmit: handleSubmit(loginHandler)
    }
}