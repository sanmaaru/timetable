import React, {useCallback, useEffect, useState} from "react";
import './CreateThemeDialog.css'
import {DialogContextType} from "./DialogProvider";
import StandardInput from "../../Input/StandardInput";
import {SubmitHandler, useForm, UseFormSetError} from "react-hook-form";
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
    } = useForm({
        mode: "onBlur",
        reValidateMode: 'onChange',
    })

    const onSubmit: SubmitHandler<CreateThemeInput> = async (data: CreateThemeInput) => {
        const {data: themeData, error } = await createThemeHandler(data.title)

        console.log(error, themeData)

        if(error || !themeData) {
            addToast(getThemeErrorMessage(error ? error : 'UNKNOWN_ERROR'), 'error')
            close()
            return
        }

        navigate(`/theme/${themeData.theme_id}/edit`)
        await onSuccess?.()
        close()
    }

    return (
        <div
            className='CreateThemeDialog'
            role='dialog'
            aria-modal={true}
        >
            <span>새로운 테마 만들기</span>
            <form onSubmit={handleSubmit(onSubmit)} noValidate={true}>
                <span>테마 이름 지정</span>
                <StandardInput
                    placeHolder={'theme title'}
                    registration={ register('title', {
                        required: '테마 이름을 입력해주세요'
                    }) }
                    errorMessage={errors?.title?.message}
                />
                <div className='btn-area'>
                    <StandardButton label={'취소'} loading={false} type={'button'} onClick={close}/>
                    <StandardButton label={'생성'} loading={loading} type={'submit'}/>
                </div>
                <span></span>
            </form>
        </div>
    )
}

export default CreateThemeDialog