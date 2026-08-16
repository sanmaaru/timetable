import style from './UserElement.module.css';
import React from "react";
import {IdToken, UserInfo} from "../../types/account";

export interface UserElementProps {
    userInfo: UserInfo;
    idToken: IdToken;
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
            <span className={style.info}>{userInfo.email}</span>
            <span className={`${style.info} ${idToken.expired ? style.expired : ''}`}>
                {idToken.expired ? 'Expired' : idToken.token_id}
            </span>
        </div>
    )
}
