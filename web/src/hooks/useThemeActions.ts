import {useCallback} from "react";
import {deleteTheme} from "../api/fetchTheme";
import {useToast} from "../components/alert/toast/ToastContext";
import {getThemeErrorMessage} from "../constants/themeMessages";

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
    }, [theme_id]);

    return { handleDeleteTheme };
}

export default useThemeActions;