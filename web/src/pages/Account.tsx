import React, {useCallback} from "react";
import style from './Account.module.css'
import {getGrade} from "../util/common";
import SimpleButton from "../components/button/SimpleButton";
import {useDialog} from "../components/alert/dialog/DialogProvider";
import {useNavigate} from "react-router-dom";
import {useToast} from "../components/alert/toast/ToastContext";
import useUser, {useUserAction} from "../hooks/useUser";
import AccountDeleteConfirmDialog from "../components/alert/dialog/AccountDeleteConfirmDialog";

const Account = () => {
    const { open, close, isOpen } = useDialog()
    const { addToast } = useToast()
    const { userData, loading, error } = useUser()
    const navigate = useNavigate()
    const { handleLogout } = useUserAction()

    const handleClickDelete = useCallback(async () => {
        if (!userData) {
            handleClickLogout()
            return
        }

        open(
            <AccountDeleteConfirmDialog
                context={{open, close, isOpen}}
                username={userData.username}
            />
        )
    }, [userData])

    const handleClickLogout = () => {
        handleLogout(() => navigate(`/login`))
    }

    if (!loading && (error || !userData))
        addToast('알 수 없는 오류가 발생했습니다. 관리자에게 문의해주세요', 'error')

    if (loading || !userData || error) {
        return (<div className={style.accountPage}>
            <span>계정 정보</span>
            <div className={style.profile}>
                <div>
                    <div className={style.image}/>
                    <div className={style.personnel}>
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
                <div className={style.content}>
                    <span>이메일</span>
                    <span></span>
                </div>
            </div>
            <div className={style.account}>
                <span>계정</span>
                <div>
                    <span>로그 아웃</span>
                    <SimpleButton onClick={handleClickLogout}>로그 아웃</SimpleButton>
                </div>
                <div>
                    <span>계정 삭제하기</span>
                    <SimpleButton onClick={handleClickDelete}>삭제</SimpleButton>
                </div>
            </div>
        </div>)
    }

    return (
        <div className={style.accountPage}>
            <span>계정 정보</span>
            <div className={style.profile}>
                <div>
                    <div className={style.image}/>
                    <div className={style.personnel}>
                        <span>{userData.username}</span>
                        <span>{userData.name}</span>
                        <span>{userData.role}</span>
                    </div>
                </div>
                <div className={style.content}>
                    <span>이메일</span>
                    <span>{userData.email}</span>
                </div>
                {userData.generation && userData.clazz && userData.number && <div className={style.content}>
                    <span>학번</span>
                    <span>{`${getGrade(userData.generation)}학년 ${userData.clazz}반 ${userData.number}번`}</span>
                </div>}
                {userData.credit && <div className={style.content}>
                    <span>이수 학점</span>
                    <span>{`${userData.credit} 학점`}</span>
                </div>}
            </div>
            <div className={style.account}>
                <span>계정</span>
                <div>
                    <span>로그 아웃</span>
                    <SimpleButton onClick={handleClickLogout}>로그 아웃</SimpleButton>
                </div>
                <div>
                    <span>계정 삭제하기</span>
                    <SimpleButton onClick={handleClickDelete}>삭제</SimpleButton>
                </div>
            </div>
        </div>
    )
}

export default Account;