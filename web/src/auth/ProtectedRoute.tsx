import React, {useEffect} from "react";
import {isAuthenticated} from "./auth";
import {Navigate, Outlet, useLocation} from "react-router-dom";
import {Role, ROLE_LIST} from "../types/account";
import useUser from "../hooks/useUser";
import {useToast} from "../components/alert/toast/ToastContext";

interface ProtectedRouteProps {
    allowedRoles?: Role[]
}

const ProtectedRoute = ({ allowedRoles = [...ROLE_LIST] }: ProtectedRouteProps) => {
    const isAuth = isAuthenticated();
    const location = useLocation()
    const { addToast } = useToast();

    if (!isAuth) {
        return <Navigate to="/login" state={{ from: location }} replace/>
    }

    const { userData, loading } = useUser()
    useEffect(() => {
        if(!loading && userData) {
            const hasAccess = allowedRoles.includes(userData.role)
            if (!hasAccess) {
                addToast('허가 되지 않은 사용자입니다', 'error')
            }
        }
    }, [loading, userData, allowedRoles, addToast]);

    if (loading) {
        return <div></div>
    }

    if (!userData || !allowedRoles.includes(userData.role)) {
        return <Navigate to="/" replace/>
    }

    return <Outlet/>
}

export default ProtectedRoute;