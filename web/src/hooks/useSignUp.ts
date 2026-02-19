import {SubmitHandler, useForm} from "react-hook-form";
import {useNavigate} from "react-router-dom";
import {useState} from "react";
import {publicAxiosClient} from "../api/axiosClient";
import {handleSignUpError, SIGN_UP_ERROR_MESSAGES} from "../constants/authMessages";
import {useToast} from "../components/alert/toast/ToastContext";

export interface SignUpInput {
    username: string;
    email: string;
    password: string;
    identifyToken: string;
}

const INVALID_TOKEN = {
    USERNAME: 'username',
}

export const useSignUp = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [globalErrorMessage, setGlobalErrorMessage] = useState<string>('');
    const { addToast } = useToast()

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

            addToast('회원가입이 성공적으로 이루어졌습니다.', 'success')
            navigate('/login', {replace: true});
        } catch (error: any) {
            if (!error.response || error.response?.status !in [ 401, 409 ]) {
                setGlobalErrorMessage(SIGN_UP_ERROR_MESSAGES.GENERAL);
                return
            }

            const invalid = error.response.data.invalid;
            const { object, message } = handleSignUpError(invalid);
            if (object == null)
                setGlobalErrorMessage(SIGN_UP_ERROR_MESSAGES.GENERAL);
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
