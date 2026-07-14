import style from './UserElement.module.css';
import React from "react";
import {UserInfo} from "../../types/account";
import {useIdToken} from "../../hooks/useUser";

export interface UserElementProps {
    userInfo: UserInfo;
    idToken: string | null;
}

export const UserElement = ({ userInfo, idToken }: UserElementProps) => {

    return (
        <div className={style.userElement}>
            <div className={style.user}>
                <div className={style.image}/>
                <div className={style.name}>
                    <span>{userInfo.name}</span>
                    <span>{userInfo.username}</span>
                </div>
            </div>
            <span className={style.email}>{userInfo.email}</span>
            <span className={`${style.idToken} ${idToken ?? style.expired}`}>{idToken ?? 'Expired'}</span>
        </div>
    )
}
