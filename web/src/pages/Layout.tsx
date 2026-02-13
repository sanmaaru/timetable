import React from 'react';
import SideBar from "../components/sidebar/SideBar";
import './Layout.css'
import {Outlet} from "react-router-dom";
import {ToastProvider} from "../components/alert/toast/ToastContext";
import {DialogProvider} from "../components/alert/dialog/DialogProvider";

const Layout = () => {
    return (
        <div id={'layout'}>
            <ToastProvider>
                <DialogProvider>
                    <SideBar/>
                    <Outlet/>
                </DialogProvider>
            </ToastProvider>
        </div>
    );
}

export default Layout