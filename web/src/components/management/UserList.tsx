import style from './UserList.module.css';
import React, {useMemo} from 'react';
import {Section} from "../../pages/management/UserManagement";
import {UserInfo} from "../../types/account";
import {UserElement} from "./UserElement";
import {FilterConfig, filterUserInfos, SortConfig, sortUserInfos} from "../../util/userlist";
import {useIdTokens} from "../../hooks/useUser";

interface UserListProps {
    className?: string;
    section: Section;
    sortConfig: SortConfig;
    filterConfig: FilterConfig;
    userInfos: UserInfo[]
}

export const UserList = ({ className, section, sortConfig, filterConfig, userInfos }: UserListProps) => {
    const { idTokenMap } = useIdTokens()
    const headerElement = section === 'student' ?
        ['user', 'email', 'generation', 'class', 'number', 'id token'] :
        ['user', 'email', '', '', '', 'id token'];

    const sortedUserInfo = useMemo<UserInfo[]>(() => {
        const filtered = filterUserInfos(userInfos || [], filterConfig)
        return sortUserInfos(filtered, sortConfig)
    }, [sortConfig, filterConfig, userInfos])

    return (
        <div className={`${style.userList} ${className}`}>
            <div className={style.header}>
                {headerElement.map((element) => <span>
                    {element.toUpperCase()}
                </span>)}
            </div>
            <div className={style.border}/>
            <ul className={style.container}>
                {sortedUserInfo.map((userInfo) => {
                    return (<li key={userInfo.identityId}>
                        <UserElement userInfo={userInfo} idToken={idTokenMap[userInfo.identityId]}/>
                    </li>)
                })}
            </ul>
        </div>
    )
}