import React, {useEffect, useMemo, useState} from 'react';
import SideBar, {SideBarButton} from "../components/sidebar/SideBar";
import style from './Layout.module.css'
import mobileStyle from './MobileLayout.module.css'
import {Outlet} from "react-router-dom";
import {useIsMobile} from "../hooks/useMediaQuery";
import MobileSidebar from "../components/sidebar/MobileSidebar";
import useUser from "../hooks/useUser";


const Layout = () => {
    const isMobile = useIsMobile()
    const { userData, loading } = useUser()

    const buttonList = useMemo<SideBarButton[]>(() => {
        const baseButtons: SideBarButton[] = [
            { id: "account", label: "계정", icon: "icn_account.png" },
            { id: "theme", label: "테마", icon: "icn_theme.png" },
        ];
        if(!loading && userData) {
            if (userData.role == 'Administrator') {
                return [
                    ...baseButtons,
                    {id: "users", label: "사용자 관리", icon: ""},
                    {id: "upload", label: "업로드", icon: ""}
                ]
            }
        }

        return baseButtons;
    }, [userData, loading]);



    if (!isMobile) return (
        <div className={style.layout}>
            <SideBar sideBarButtons={buttonList}/>
            <Outlet/>
        </div>
    )

    return ( // TODO: Mobile도 동일하게 sidebar button을 밖으로 빼는 방안 검토
        <div className={mobileStyle.mobileLayout}>
            <Outlet/>
            <MobileSidebar/>
        </div>
    )
}

export default Layout