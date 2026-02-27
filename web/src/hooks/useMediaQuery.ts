import useContainerSize from "./useContainerSize";
import {useEffect, useState} from "react";

const useMediaQuery = (query: string) => {
    const [matches, setMatches] = useState(false)

    useEffect(() => {
        const media = window.matchMedia(query);
        if (media.matches !== matches) {
            setMatches(true);
        }

        const listener = () => setMatches(media.matches);
        window.addEventListener("resize", listener);
        return () => window.removeEventListener("resize", listener);
    }, [query])

    return matches;
}

const MOBILE_SIZE = 768
export const useIsMobile = () => {
    return useMediaQuery(`(max-width: ${MOBILE_SIZE}px)`);
}

export default useContainerSize;