import React from 'react';
import SideBar from "../components/sidebar/SideBar";
import './Layout.css'
import {Outlet} from "react-router-dom";

const Layout = () => {
    return (
        <div id={'layout'}>
            <SideBar/>
            <Outlet/>
        </div>
    );
}

export default Layout