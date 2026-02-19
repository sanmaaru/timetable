import {SubmitHandler, useForm} from "react-hook-form";
import {useState} from "react";
import {publicAxiosClient} from "../api/axiosClient";
import {setTokens} from "../auth/auth";
import {useNavigate} from "react-router-dom";
import {handleLoginError, LOGIN_ERROR_MESSAGES} from "../constants/authMessages";

export interface LoginInput {
    username: string;
    password: string;
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

            console.log(response);

            const {access_token, refresh_token} = response.data.data

            setTokens(access_token, refresh_token)
            navigate('/', {replace: true});
        } catch(error: any) {
            if (!error.response || error.response.status !== 401) {
                setGlobalErrorMessage(LOGIN_ERROR_MESSAGES.GENERAL);
                return
            }

            const invalid = error.response.data.invalid;
            const { object, message } = handleLoginError(invalid);
            if (object == null) {
                setGlobalErrorMessage(LOGIN_ERROR_MESSAGES.GENERAL);
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