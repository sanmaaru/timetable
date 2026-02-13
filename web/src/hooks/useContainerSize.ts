import {useEffect, useRef, useState} from "react";

const useContainerSize = () => {
    const ref = useRef(null);
    const [size, setSize] = useState({ width: 0, height: 0 });

    useEffect(() => {
        if (!ref.current) return;

        const observer = new ResizeObserver((entries) => {
            for (let entry of entries) {
                const { width, height } = entry.contentRect
                setSize({ width: width, height: height });
            }
        })

        observer.observe(ref.current);

        return () => observer.disconnect()
    }, [])

    return { ref, width: size.width, height: size.height }
}

export default useContainerSize