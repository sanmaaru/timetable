import {useEffect, useMemo, useRef, useState} from "react";

interface ZoomOptions {
    scale?: number;
}

const useZoom = <T = string> (targetKey: T | null, {scale}?: ZoomOptions = {scale: 2}) => {
    const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1 });

    const itemsRef = useRef<Map<T, HTMLElement>>(new Map());
    const wrapperRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        if(!targetKey || !wrapperRef.current) {
            setTransform({ x: 0, y: 0, scale: 1 });
            return;
        }

        const wrapper = wrapperRef.current;
        let targetRef = itemsRef.current.get(targetKey);

        if (!targetRef) {
            setTransform({ x: 0, y: 0, scale: 1 });
            return;
        }

        const wrapperW = wrapper.offsetWidth;
        const wrapperH = wrapper.offsetHeight;

        const targetLeft= targetRef.offsetLeft;
        const targetTop = targetRef.offsetTop;
        const targetW = targetRef.offsetWidth;
        const targetH = targetRef.offsetHeight;

        const targetCenterX = targetLeft + targetW/2;
        const targetCenterY = targetTop + targetH/2;

        const moveX = (wrapperW / 2) - (targetCenterX * scale);
        const moveY = (wrapperH / 2) - (targetCenterY * scale);

        setTransform({ x: moveX, y: moveY, scale: scale });
    }, [targetKey, scale]);

    const transformStyle = useMemo(() => {
        return {
            transform: `translate(${transform.x}px, ${transform.y}px) scale(${transform.scale})`,
            transformOrigin: "0 0",
            transition: `transform 0.7s cubic-bezier(0.25, 0.8, 0.25, 1)`,
        }
    }, [transform]);

    return { itemsRef, wrapperRef, transformStyle };
}

export default useZoom