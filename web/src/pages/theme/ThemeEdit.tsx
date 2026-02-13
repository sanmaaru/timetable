import React, {useCallback, useEffect, useRef, useState} from "react";
import './ThemeEdit.css'
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

const ThemeEdit = () => {
    const { themeId } = useParams()
    const { timetableData, isLoading: isTimetableLoading } =  useTimetable()
    const { themeData, isLoading: isThemeLoading, loadData, setColorScheme, update, isSaved } = useMutableTheme(themeId ?? '')
    const [focus, setFocus] = useState<string | null>(null);
    const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1});
    const itemsRef = useRef(new Map());
    const wrapperRef = useRef<HTMLDivElement | null>(null);

    const toast = useToast()
    const { open, close, isOpen } = useDialog()
    const navigate = useNavigate();

    const { bypass } = usePreventLeave(!isSaved, '저장하지 않으면 변경 내용이 손실됩니다. 그래도 나가시겠습니까?')

    useEffect(() => {
        if(!isTimetableLoading && !isThemeLoading && (!timetableData || !themeData)) {
            toast.addToast('알 수 없는 오류가 발생하였습니다. 관리자에게 문의해주세요!', 'error')
        }
    }, [isThemeLoading, isTimetableLoading, timetableData, themeData, toast, themeId])

    useEffect(() => {
        if (!focus || !itemsRef.current.get(focus) || !wrapperRef.current) {
            setTransform({ x: 0, y: 0, scale: 1 });
            return;
        }

        const wrapper = wrapperRef.current;
        const target = itemsRef.current.get(focus);

        const wrapperW = wrapper.offsetWidth;
        const wrapperH = wrapper.offsetHeight;

        const targetLeft= target.offsetLeft;
        const targetTop = target.offsetTop;
        const targetW = target.offsetWidth;
        const targetH = target.offsetHeight;

        const targetCenterX = targetLeft + targetW/2;
        const targetCenterY = targetTop + targetH/2;

        const scale = 2.0;

        const moveX = (wrapperW / 2) - (targetCenterX * scale);
        const moveY = (wrapperH / 2) - (targetCenterY * scale);

        setTransform({ x: moveX, y: moveY, scale: scale });
    }, [focus, itemsRef, wrapperRef]);

    const getTransformStyle = useCallback(() => {
        return {
            transform: `translate(${transform.x}px, ${transform.y}px) scale(${transform.scale})`,
            transformOrigin: "0 0",
            transition: `transform 0.7s cubic-bezier(0.25, 0.8, 0.25, 1)`,
        }
    }, [transform])

    const handleFocus = useCallback((subject: string | null) => {
        itemsRef.current.forEach((element) => {
            element?.classList.remove('focus');
        })

        if(subject) {
            const current = itemsRef.current.get(subject)
            if (current) {
                current.classList.add('focus')
            }
        }

        setFocus(subject)
    }, [itemsRef])

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
            navigate('/theme')
            return
        }

        open(<SaveDialog
            context={{ open, close, isOpen }}
            onConfirm={handleClickSave}
            onSuccess={() => { bypass(); navigate('/theme') }}
            color={'#ff0000'}
        >
            저장하지 않으면 변경 내용이 손실됩니다.
        </SaveDialog>)
    }, [isSaved])

    if (isThemeLoading || isTimetableLoading) {
        return (<div id='ThemeEdit'>
        </div>)
    }

    if (!timetableData || !themeData) {
        return (<div id='ThemeEdit'>
        </div>)
    }

    const { schedules } = timetableData;

    return (
        <DialogProvider>
            <div id='ThemeEdit'>
                <div className='title'>
                    <span className='title'>{'테마 수정'}</span>
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
                            (<EditableColorSchemaElement
                                colorScheme={value}
                                setColorScheme={setColorScheme}
                                key={idx}
                                onClick={handleFocus}
                                focus={focus}/>)
                        )}
                        <div className='footer'>
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