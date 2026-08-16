import {useCallback, useEffect, useRef, useState} from "react";
import {IdToken, UserInfo} from "../types/account";
import {deleteUser, fetchCurrentUser, fetchIdToken, fetchIdTokens, fetchUser, fetchUserInfos} from "../api/fetchUser";
import {useToast} from "../components/alert/toast/ToastContext";
import {removeTokens} from "../auth/auth";
import {useNavigate} from "react-router-dom";

const useUser = (userId?: string | null) => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [userData, setUserData] = useState<UserInfo | null>(null);
    const isMounted = useRef<boolean>(true);

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

        if (isMounted.current) {
            setUserData(data);
            setError(err)
            setLoading(false);
        }
    }, [userId, setLoading, setError]);

    useEffect(() => {
        isMounted.current = true;
        loadData()

        return () => {
            isMounted.current = false;
        }
    }, [])

    return { loadData, loading, error, userData };
}

export const useUserAction = () => {
    const { addToast } = useToast();
    const navigate = useNavigate();

    const handleDeleteUser = useCallback(async (onSuccess?: () => void) => {
        const data = await deleteUser();
        if (data.error) {
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

export const useIdToken = (userInfoId: string) => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [idToken, setIdToken] = useState<IdToken | null>(null);
    const isMounted = useRef<boolean>(true);

    const loadData = useCallback(async () => {
        let data, err
        setLoading(true);
        const response = await fetchIdToken(userInfoId)
        data = response.data
        err = response.error

        if (isMounted.current) {
            setIdToken(data)
            setError(err)
            setLoading(false);
        }
    }, [userInfoId, setLoading, setError]);

    useEffect(() => {
        isMounted.current = true;
        loadData()

        return () => {
            isMounted.current = false;
        }
    }, [userInfoId])

    return { loading, error, idToken };
}


export const useIdTokens = () => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [idTokenMap, setIdTokenMap] = useState<Record<string, IdToken>>({});
    const isMounted = useRef<boolean>(true);

    const loadData = useCallback(async () => {
        let data, err
        setLoading(true);
        const response = await fetchIdTokens()
        data = response.data
        err = response.error

        if (isMounted.current) {
            setIdTokenMap(data ?? {})
            setError(err)
            setLoading(false);
        }
    }, [setLoading, setError]);

    useEffect(() => {
        isMounted.current = true;
        loadData()

        return () => {
            isMounted.current = false;
        }
    }, [])

    return { loading, error, idTokenMap };
}

export const useUserInfos = (role: string) => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [userInfos, setUserInfos]  = useState<UserInfo[]>([]);
    const isMounted = useRef<boolean>(true);

    const loadData = useCallback(async () => {
        let data, err
        setLoading(true);
        const response = await fetchUserInfos(role)
        data = response.data
        err = response.error

        if (isMounted.current) {
            setUserInfos(data ?? []);
            setError(err)
            setLoading(false);
        }
    }, [role, setLoading, setError]);

    useEffect(() => {
        isMounted.current = true;
        loadData()

        return () => {
            isMounted.current = false;
        }
    }, [role])

    return { loading, error, userInfos };
}

export default useUser;