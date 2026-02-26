import React from 'react';
import SideBar from "../components/sidebar/SideBar";
import style from './Layout.module.css'
import {Outlet} from "react-router-dom";


const Layout = () => {
    return (
        <div className={style.layout}>
            <SideBar/>
            <Outlet/>
        </div>
    );
}

export default Layout