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

        return (isDirty && currentLocation.pathname !== nextLocation.pathname)
    }, [isDirty]);

    const blocker = useBlocker(shouldBlock);
    useEffect(() => {
        if (blocker.state == "blocked") {
            const confirmLeave = window.confirm(message);
            if(confirmLeave)
                blocker.proceed()
            else
                blocker.reset()
        }
    }, [blocker, message]);

    const bypass = useCallback(() => {
        bypassRef.current = true
    }, [])

    return { bypass }
}