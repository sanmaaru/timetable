import React from "react";
import {isAuthenticated} from "./auth";
import {Navigate, Outlet, useLocation} from "react-router-dom";

const ProtectedRoute = () => {
    const isAuth = isAuthenticated();
    const location = useLocation()

    if (!isAuth) {
        return <Navigate to="/login" state={{ from: location }} replace/>
    }

    return <Outlet/>
}

export default ProtectedRoute;