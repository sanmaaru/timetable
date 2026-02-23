import React, {useCallback, useEffect, useMemo, useRef, useState} from "react";
import './ThemeView.css';
import {useParams} from "react-router-dom";
import useTimetable from "../../hooks/useTimetable";
import TimetableGrid from "../../components/timetable/TimetableGrid";
import TimetableHeader from "../../components/timetable/TimetableHeader";
import {useToast} from "../../components/alert/toast/ToastContext";
import ColorSchemaElement from "../../components/theme/ColorSchemaElement";
import {useTheme} from "../../hooks/theme/useThemes";
import {timetable} from "../../util/storage";

const ThemeView = () => {
    const { themeId } = useParams()
    const { timetableData, isLoading: isTimetableLoading} =  useTimetable()
    const { themeData, isLoading: isThemeLoading } = useTheme(themeId)
    const [focus, setFocus] = useState<string | null>(null);
    const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1});
    const itemsRef = useRef(new Map());
    const wrapperRef = useRef<HTMLDivElement | null>(null);

    const toast = useToast()

    useEffect(() => {
        if(!isThemeLoading && !isTimetableLoading && (!timetableData || !themeData)) {
            toast.addToast('알 수 없는 오류가 발생하였습니다. 관리자에게 문의해주세요!', 'error')
        }
    }, [isThemeLoading, isTimetableLoading, timetableData, themeData, toast, themeId])

    useEffect(() => {
        if (!focus || !wrapperRef.current) {
            setTransform({ x: 0, y: 0, scale: 1 });
            return;
        }

        const wrapper = wrapperRef.current;
        let targetRef = null;

        for (const [classId, ref] of itemsRef.current) {
            const targetClass = timetable.getClass(classId);
            if (targetClass && targetClass.subject === focus) {
                targetRef = ref;
                break;
            }
        }

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

        const scale = 2.0;

        const moveX = (wrapperW / 2) - (targetCenterX * scale);
        const moveY = (wrapperH / 2) - (targetCenterY * scale);

        setTransform({ x: moveX, y: moveY, scale: scale });
    }, [focus]);

    const handleFocus = useCallback((subject: string | null) => {
        itemsRef.current.forEach((ref) => {
            ref?.classList.remove('focus');
        });

        if(subject) {
            for (const [classId, ref] of itemsRef.current) {
                const targetClass = timetable.getClass(classId);
                if (targetClass && targetClass.subject === subject) {
                    ref?.classList.add('focus');
                }
            }
        }

        setFocus(subject);
    }, []);

    const getTransformStyle = useCallback(() => {
        return {
            transform: `translate(${transform.x}px, ${transform.y}px) scale(${transform.scale})`,
            transformOrigin: "0 0",
            transition: `transform 0.7s cubic-bezier(0.25, 0.8, 0.25, 1)`,
        }
    }, [transform])


    if (isThemeLoading || isTimetableLoading || !timetableData || !themeData) {
        return (<div id='theme-view'>
        </div>)
    }

    const { schedules } = timetableData;


    return (<div id='theme-view'>
        <div className='title container'>
            <span className='title'>{'테마 미리보기'}</span>
            <span className='name'> - {themeData.title}</span>
        </div>
        <div className='content'>
            <div className='timetable' ref={wrapperRef} style={getTransformStyle()}>
                <div className={`wrapper ${focus ? 'focus' : ''}`}>
                    <TimetableHeader/>
                    <TimetableGrid
                        schedules={schedules}
                        colorSchemes={themeData.colorSchemes}
                        detail={false}
                        scheduleRefMap={itemsRef}
                    />
                </div>
            </div>
            <div className='detail'>
                <span className='title'>색 조합표</span>
                {themeData.colorSchemes.map((value, idx) =>
                    (<ColorSchemaElement colorScheme={value} key={idx} onClick={handleFocus} focus={focus}/>)
                )}
            </div>
        </div>
    </div>)
}

export default ThemeView;