import React, {useEffect, useMemo, useState, useCallback} from "react";
import style from './ThemeView.module.css';
import {useParams} from "react-router-dom";
import useTimetable from "../../hooks/useTimetable";
import TimetableGrid from "../../components/timetable/TimetableGrid";
import TimetableHeader from "../../components/timetable/TimetableHeader";
import {useToast} from "../../components/alert/toast/ToastContext";
import ColorSchemaElement from "../../components/theme/ColorSchemaElement";
import {useTheme} from "../../hooks/theme/useThemes";
import useZoom from "../../hooks/useZoom";

const ThemeView = () => {
    const { themeId } = useParams()
    const { timetableData, isLoading: isTimetableLoading} =  useTimetable()
    const { themeData, isLoading: isThemeLoading } = useTheme(themeId)
    const [focus, setFocus] = useState<string | null>(null)

    const toast = useToast()

    const targetClassId = useMemo(() => {
        if(!focus || !timetableData) return null;

        const targetSchedule = timetableData.schedules.find(s => s.clazz.subject == focus)
        return targetSchedule ? targetSchedule.clazz.classId : null;
    }, [focus, timetableData])
    const { itemsRef, wrapperRef, transformStyle } = useZoom(targetClassId)

    const getScheduleClassName = useCallback((classId: string) => {
        if(targetClassId === null) return ''

        return classId == targetClassId ? '' : style.hide
    }, [targetClassId])

    useEffect(() => {
        if(!isThemeLoading && !isTimetableLoading && (!timetableData || !themeData)) {
            toast.addToast('알 수 없는 오류가 발생하였습니다. 관리자에게 문의해주세요!', 'error')
        }
    }, [isThemeLoading, isTimetableLoading, timetableData, themeData, toast, themeId])


    if (isThemeLoading || isTimetableLoading || !timetableData || !themeData) {
        return (<div className={style.themeView}>
        </div>)
    }

    const { schedules } = timetableData;


    return (<div className={style.themeView}>
        <div className={style.container}>
            <span className={style.title}>{'테마 미리보기'}</span>
            <span className={style.name}> - {themeData.title}</span>
        </div>
        <div className={style.content}>
            <div className={style.timetable} ref={wrapperRef} style={transformStyle}>
                <div className={`${style.wrapper}`}>
                    <TimetableHeader/>
                    <TimetableGrid
                        schedules={schedules}
                        colorSchemes={themeData.colorSchemes}
                        detail={false}
                        scheduleRefMap={itemsRef}
                        className={style.timetableGrid}
                        scheduleClassName={getScheduleClassName}
                    />
                </div>
            </div>
            <div className={style.detail}>
                <span className={style.title}>색 조합표</span>
                {themeData.colorSchemes.map((value, idx) =>
                    (<ColorSchemaElement colorScheme={value} key={idx} onClick={setFocus} focus={focus}/>)
                )}
            </div>
        </div>
    </div>)
}

export default ThemeView;