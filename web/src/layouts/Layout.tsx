import React from 'react';
import SideBar from "../components/sidebar/SideBar";
import style from './Layout.module.css'
import mobileStyle from './MobileLayout.module.css'
import {Outlet} from "react-router-dom";
import {useIsMobile} from "../hooks/useMediaQuery";
import MobileSidebar from "../components/sidebar/MobileSidebar";


const Layout = () => {
    const isMobile = useIsMobile()

    if (!isMobile) return (
        <div className={style.layout}>
            <SideBar/>
            <Outlet/>
        </div>
    )

    return (
        <div className={mobileStyle.mobileLayout}>
            <Outlet/>
            <MobileSidebar/>
        </div>
    )
}

export default Layout