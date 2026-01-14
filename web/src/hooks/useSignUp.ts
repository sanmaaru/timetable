import {SubmitHandler, useForm} from "react-hook-form";
import {useNavigate} from "react-router-dom";
import {useState} from "react";
import {publicAxiosClient} from "../api/axiosClient";

export interface SignUpInput {
    username: string;
    email: string;
    password: string;
    identifyToken: string;
}

const ERROR_MESSAGES = {
    GENERAL: '로그인 과정 중에 오류가 발생하였습니다. 관리자에게 제보해 주세요.',
    USERNAME: '이미 존재하는 사용자 이름 입니다.',
    IDENTIFY_TOKEN: '이미 만료된 인증 토큰 입니다.'
}

const INVALID_TOKEN = {
    USERNAME: 'username',
    IDENTIFY_TOKEN: 'identify_token',
}

const handleApiError = (invalid: string) => {
    let object, message
    switch (invalid) {
        case INVALID_TOKEN.USERNAME:
            object = 'username'
            message = ERROR_MESSAGES.USERNAME
            break;

        case INVALID_TOKEN.IDENTIFY_TOKEN:
            object = 'identifyToken'
            message = ERROR_MESSAGES.IDENTIFY_TOKEN
            break;

        default:
            object = null
            message = ERROR_MESSAGES.GENERAL
            break;
    }
    return { object, message }
}

export const useSignUp = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [globalErrorMessage, setGlobalErrorMessage] = useState<string>('');

    const {
        register,
        handleSubmit,
        watch,
        setError,
        formState: { errors, isValid }
    } = useForm({
        mode: 'onBlur',
        reValidateMode: 'onChange',
    });

    const password = watch('password')

    const signUpHandler: SubmitHandler<SignUpInput> = async (data) => {
        setLoading(true);
        setGlobalErrorMessage('');

        try {
            const response = await publicAxiosClient.post("/auth/signup", {
                username: data.username,
                email: data.email,
                password: data.password,
                identify_token: data.identifyToken.trim(),
            });

            navigate('/login', {replace: true});
        } catch (error: any) {
            if (!error.response || error.response?.status !in [ 401, 409 ]) {
                setGlobalErrorMessage(ERROR_MESSAGES.GENERAL);
                return
            }

            const invalid = error.response.data.detail.invalid;
            const { object, message } = handleApiError(invalid);
            if (object == null)
                setGlobalErrorMessage(ERROR_MESSAGES.GENERAL);
            else
                setError(object, {
                    type: 'server',
                    message: message
                })

        } finally {
            setLoading(false);
        }
    }

    return {
        register,
        errors,
        password,
        loading,
        globalErrorMessage,
        onSubmit: handleSubmit(signUpHandler),
    }
}
