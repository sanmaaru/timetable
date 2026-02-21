import React from "react";
import './AccountDeleteConfirmDialog.css';
import {DialogContextType} from "./DialogProvider";
import {useForm} from "react-hook-form";
import {useUserAction} from "../../../hooks/useUser";
import {useToast} from "../toast/ToastContext";
import {useNavigate} from "react-router-dom";
import StandardButton from "../../button/StandardButton";
import StandardInput from "../../Input/StandardInput";

interface AccountDeleteInput {
    username: string
}

interface AccountDeleteConfirmDialogProps {
    context: DialogContextType
    username: string
    onSuccess?: () => void;
}

const AccountDeleteConfirmDialog = ({ context, username }: AccountDeleteConfirmDialogProps) => {
    const { handleDeleteUser } = useUserAction()
    const { addToast } = useToast()
    const navigate = useNavigate()
    const { close } = context;
    const {
        register,
        handleSubmit,
        formState: { errors },
        setError
    } = useForm<AccountDeleteInput>({
        mode: "onBlur",
        reValidateMode: 'onChange'
    })

    const onSubmit = async (data: AccountDeleteInput) => {
        if (data.username !== username) {
            setError('username', {
                type: 'value',
                message: '확인 문자가 일치하지 않습니다'
            })
            return
        }

        await handleDeleteUser(() => {
            navigate('/login')
            addToast('계정이 성공적으로 삭제되었습니다', 'success')
        })
        close()
    }

    return (
        <div className={'AccountDeleteConfirmDialog'} role='dialog' aria-modal='true'>
            <span>! 정말로 계정을 삭제하시겠습니까?</span>
            <span>{'계정 삭제 시 모든 사용자 데이터가 사라지며, 영원이 복구할 수 없습니다. \n그래도 삭제하시겠습니까?'}</span>
            <form onSubmit={handleSubmit(onSubmit)} noValidate={true}>
                <span>{`삭제를 원하신다면 '${username}'을(를) 입력해 주세요`}</span>
                <StandardInput
                    placeHolder={'username'}
                    registration={register(
                        'username', {
                            required: '확인 문자를 입력해 주세요',
                        }
                    )}
                    errorMessage={errors.username?.message}
                />
                <div className='btn-area'>
                    <StandardButton label={'취소'} loading={false} type={'button'} onClick={close}/>
                    <StandardButton label={'삭제'} loading={false} type={'submit'}/>
                </div>
            </form>
        </div>
    )
}

export default AccountDeleteConfirmDialog;