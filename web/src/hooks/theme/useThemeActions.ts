import {useCallback, useState} from "react";
import {createTheme, deleteTheme, putSelectedTheme} from "../../api/fetchTheme";
import {useToast} from "../../components/alert/toast/ToastContext";
import {getThemeErrorMessage} from "../../constants/themeMessages";
import {Theme} from "../../types/theme";

const useThemeActions= (theme_id: string) => {
    const toast = useToast();

    const handleDeleteTheme = useCallback(async (onSuccess?: () => void) => {
        const errorCode = await deleteTheme(theme_id);

        if (!errorCode) {
            toast.addToast('테마가 삭제되었습니다', 'success')
            onSuccess?.()
            return true;
        }

        const message = getThemeErrorMessage(errorCode);
        toast.addToast(message, 'error')
        return false;
    }, [theme_id, toast]);

    const handlePutSelectedTheme = useCallback(async (onSuccess?: () => void) => {
        const errorCode = await putSelectedTheme(theme_id);

        if (!errorCode) {
            toast.addToast('사용 중인 테마가 변경되었습니다', 'success')
            onSuccess?.()
            return true;
        }

        const message = getThemeErrorMessage(errorCode);
        toast.addToast(message, 'error')
        return false;
    }, [theme_id, toast])

    return { handleDeleteTheme, handlePutSelectedTheme };
}

export const useCreateTheme = () => {
    const [loading, setLoading] = useState(false);

    const createThemeHandler = useCallback(async (title: string) => {
        setLoading(true);
        const { data, error } = await createTheme(title)
        setLoading(false);

        return { data, error }
    }, [])

    return {
        loading, createThemeHandler
    }
}

export default useThemeActions;