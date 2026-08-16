import style from './StudentUserElement.module.css';
import userElementStyle from './UserElement.module.css';
import React from "react";
import {UserElementProps} from "./UserElement";


export const StudentUserElement = ({ userInfo, idToken }: UserElementProps) => {

    return (
        <div className={style.userElement}>
            <div className={userElementStyle.user}>
                <div className={userElementStyle.image}/>
                <div className={userElementStyle.name}>
                    <span>{userInfo.name}</span>
                    <span>{userInfo.username}</span>
                </div>
            </div>
            <span className={userElementStyle.info}>{userInfo.email}</span>
            <span className={style.info}>{userInfo.generation}</span>
            <span className={style.info}>{userInfo.clazz}</span>
            <span className={style.info}>{userInfo.number}</span>
            <span className={`${userElementStyle.info} ${idToken.expired ? style.expired : ''}`}>
                {idToken.expired ? 'Expired' : idToken.token_id}
            </span>
        </div>
    )
}
