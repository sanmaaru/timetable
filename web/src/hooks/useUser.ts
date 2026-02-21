import {useCallback, useEffect, useState} from "react";
import {UserInfo} from "../types/account";
import {deleteUser, fetchCurrentUser, fetchUser} from "../api/fetchUser";
import {useToast} from "../components/alert/toast/ToastContext";
import {removeTokens} from "../auth/auth";
import {useNavigate} from "react-router-dom";

const useUser = (userId?: string | null) => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [userData, setUserData] = useState<UserInfo | null>(null);

    const loadData = useCallback(async () => {
        let data, err
        setLoading(true);
        if (!userId) {
            const response = await fetchCurrentUser()
            data = response.data
            err = response.error
        } else {
            const response = await fetchUser(userId)
            data = response.data
            err = response.error
        }

        setUserData(data);
        setError(err)
        setLoading(false);
    }, [userId, setLoading, setError]);

    useEffect(() => {
        loadData()
    }, [])

    return { loadData, loading, error, userData };
}

export const useUserAction = () => {
    const { addToast } = useToast();
    const navigate = useNavigate();

    const handleDeleteUser = useCallback(async (onSuccess?: () => void) => {
        const error = await deleteUser();
        if (error) {
            addToast('계정을 삭제하는 도중 에러가 발생하였습니다. 관리자에게 문의해주세요', 'error')
            return
        }

        removeTokens()
        onSuccess?.()
    }, [addToast, navigate])

    const handleLogout = useCallback((onSuccess?: () => void) => {
        removeTokens()
        onSuccess?.()
    }, [])

    return { handleDeleteUser, handleLogout }
}

export default useUser;