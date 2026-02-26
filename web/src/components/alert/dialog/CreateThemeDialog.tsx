import React from "react";
import style from './CreateThemeDialog.module.css'
import {DialogContextType} from "./DialogProvider";
import StandardInput from "../../Input/StandardInput";
import {SubmitHandler, useForm} from "react-hook-form";
import StandardButton from "../../button/StandardButton";
import {useCreateTheme} from "../../../hooks/theme/useThemeActions";
import {useToast} from "../toast/ToastContext";
import {useNavigate} from "react-router-dom";
import {getThemeErrorMessage} from "../../../constants/themeMessages";

interface CreateThemeInput {
    title: string;
}

interface CreateThemeDialogProps {
    context: DialogContextType;
    onSuccess?: () => void;
}

const CreateThemeDialog = ({context, onSuccess}: CreateThemeDialogProps) => {
    const { close } = context;
    const { loading, createThemeHandler } = useCreateTheme()
    const { addToast } = useToast()
    const navigate = useNavigate()

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<CreateThemeInput>({
        mode: "onBlur",
        reValidateMode: 'onChange',
    })

    const onSubmit: SubmitHandler<CreateThemeInput> = async (data: CreateThemeInput) => {
        const {data: themeData, error } = await createThemeHandler(data.title)

        if(error || !themeData) {
            addToast(getThemeErrorMessage(error ? error : 'UNKNOWN_ERROR'), 'error')
            close()
            return
        }

        navigate(`/theme/${themeData.themeId}/edit`)
        await onSuccess?.()
        close()
    }

    return (
        <div
            className={style.createThemeDialog}
            role='dialog'
            aria-modal={true}
        >
            <span className={style.title}>새로운 테마 만들기</span>
            <form className={style.form} onSubmit={handleSubmit(onSubmit)} noValidate={true}>
                <span className={style.content}>테마 이름 지정</span>
                <StandardInput
                    placeHolder={'theme title'}
                    registration={ register('title', {
                        required: '테마 이름을 입력해주세요'
                    }) }
                    errorMessage={errors?.title?.message}
                />
                <div className={style.btnArea}>
                    <StandardButton className={style.cancelButton} label={'취소'} loading={false} type={'button'} onClick={close}/>
                    <StandardButton label={'생성'} loading={loading} type={'submit'}/>
                </div>
            </form>
        </div>
    )
}

export default CreateThemeDialog