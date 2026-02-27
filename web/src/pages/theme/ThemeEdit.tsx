import React, {useCallback, useEffect, useMemo, useState} from "react";
import style from './ThemeEdit.module.css'
import viewerStyle from './ThemeView.module.css'
import {useNavigate, useParams} from "react-router-dom";
import useTimetable from "../../hooks/useTimetable";
import {useToast} from "../../components/alert/toast/ToastContext";
import TimetableHeader from "../../components/timetable/TimetableHeader";
import TimetableGrid from "../../components/timetable/TimetableGrid";
import EditableColorSchemaElement from "../../components/theme/EditableColorSchemaElement";
import StandardButton from "../../components/button/StandardButton";
import {useMutableTheme} from "../../hooks/theme/useThemes";
import {getThemeErrorMessage} from "../../constants/themeMessages";
import {DialogProvider, useDialog} from "../../components/alert/dialog/DialogProvider";
import SaveDialog from "../../components/alert/dialog/SaveDialog";
import {usePreventLeave} from "../../hooks/usePreventLeave";
import useZoom from "../../hooks/useZoom";

const ThemeEdit = () => {
    const { themeId } = useParams()
    const { timetableData, isLoading: isTimetableLoading } =  useTimetable()
    const { themeData, isLoading: isThemeLoading, loadData, setColorScheme, update, isSaved, setIsSaved } = useMutableTheme(themeId ?? '')
    const [focus, setFocus] = useState<string | null>(null);

    const toast = useToast()
    const { open, close, isOpen } = useDialog()
    const navigate = useNavigate();



    const targetClassId = useMemo(() => {
        if(!focus || !timetableData) return null;

        const targetSchedule = timetableData.schedules.find(s => s.clazz.subject == focus)
        return targetSchedule ? targetSchedule.clazz.classId : null;
    }, [focus, timetableData])
    const { itemsRef, wrapperRef, transformStyle } = useZoom(targetClassId, {})

    const getScheduleClassName = useCallback((classId: string) => {
        if(targetClassId === null) return ''

        return classId == targetClassId ? '' : viewerStyle.hide
    }, [targetClassId])





    const { bypass } = usePreventLeave(!isSaved, '저장하지 않으면 변경 내용이 손실됩니다. 그래도 나가시겠습니까?')

    useEffect(() => {
        if(!isTimetableLoading && !isThemeLoading && (!timetableData || !themeData)) {
            toast.addToast('알 수 없는 오류가 발생하였습니다. 관리자에게 문의해주세요!', 'error')
        }
    }, [isThemeLoading, isTimetableLoading, timetableData, themeData, toast, themeId])

    const handleClickSave = async () => {
        await update(() => {
            toast.addToast('성공적으로 테마가 저장되었습니다', 'success')
        }, (error) => {
            toast.addToast(getThemeErrorMessage(error), 'error')
        })
        await loadData()
    }

    const handleClickQuit = useCallback(async () => {
        if (isSaved) {
            navigate(-1)
            return
        }

        open(<SaveDialog
            context={{ open, close, isOpen }}
            onConfirm={handleClickSave}
            onSuccess={() => { bypass(); navigate(-1); }}
            color={'#ff0000'}
        >
            저장하지 않으면 변경 내용이 손실됩니다.
        </SaveDialog>)
    }, [isSaved, setIsSaved])

    if (isThemeLoading || isTimetableLoading) {
        return (<div className={style.themeEdit}>
        </div>)
    }

    if (!timetableData || !themeData) {
        return (<div className={style.themeEdit}>
        </div>)
    }

    const { schedules } = timetableData;

    return (
        <DialogProvider>
            <div className={style.themeEdit}>
                <div className={viewerStyle.container}>
                    <span className={viewerStyle.title}>{'테마 수정'}</span>
                    <span className={viewerStyle.name}> - {themeData.title}</span>
                </div>
                <div className={viewerStyle.content}>
                    <div className={viewerStyle.timetable} ref={wrapperRef} style={transformStyle}>
                        <div className={viewerStyle.wrapper}>
                            <TimetableHeader/>
                            <TimetableGrid
                                schedules={schedules}
                                colorSchemes={themeData.colorSchemes}
                                detail={false}
                                scheduleRefMap={itemsRef}
                                className={viewerStyle.timetableGrid}
                                scheduleClassName={getScheduleClassName}
                            />
                        </div>
                    </div>
                    <div className={viewerStyle.detail}>
                        <span className={viewerStyle.title}>색 조합표</span>
                        {themeData.colorSchemes.map((value, idx) =>
                            (<EditableColorSchemaElement
                                colorScheme={value}
                                setColorScheme={setColorScheme}
                                key={idx}
                                onClick={setFocus}
                                focus={focus}/>)
                        )}
                        <div className={style.footer}>
                            <StandardButton label={'나가기'} loading={false} type={'button'} onClick={handleClickQuit}/>
                            <StandardButton label={'저장'} loading={false} type={'button'} onClick={handleClickSave}/>
                        </div>
                    </div>
                </div>
            </div>
        </DialogProvider>

    )
}

export default ThemeEdit