import {useCallback, useEffect, useRef} from "react";
import {useBlocker} from "react-router-dom";

export const usePreventLeave = (isDirty: boolean, message: string) => {
    const bypassRef = useRef(false)

    useEffect(() => {
        const handleBeforeUnload = (e: BeforeUnloadEvent) => {
            if (bypassRef.current) return

            if(isDirty) {
                e.preventDefault()
            }
        }

        if (isDirty)
            window.addEventListener('beforeunload', handleBeforeUnload)

        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload)
        }
    }, [isDirty])

    const shouldBlock = useCallback(({ currentLocation, nextLocation }: any) => {
        if (bypassRef.current) return false

        if (isDirty && currentLocation.pathname !== nextLocation.pathname) {
            const confirmLeave = window.confirm(message)

            return !confirmLeave
        }

        return false
    }, [isDirty, message]);

    useBlocker(shouldBlock);

    const bypass = useCallback(() => {
        bypassRef.current = true
    }, [])

    return { bypass }
}