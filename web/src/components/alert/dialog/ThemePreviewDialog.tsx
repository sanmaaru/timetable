import './ThemePreviewDialog.css';
import {DialogContextType} from "./DialogProvider";
import TimetableHeader from "../../timetable/TimetableHeader";
import TimetableGrid from "../../timetable/TimetableGrid";
import useTimetable from "../../../hooks/useTimetable";
import {useToast} from "../toast/ToastContext";
import React, {useEffect} from "react";
import Close from '../../../resources/icon/icn_close.svg?react';
import {useTheme} from "../../../hooks/theme/useThemes";
import IconButton from "../../button/IconButton";

export interface ThemePreviewDialogProps {
    context: DialogContextType
    themeId: string
    title: string
}

const ThemePreviewDialog = ({context: dialogContext, themeId, title} : ThemePreviewDialogProps) => {
    const { close } = dialogContext;

    const { timetableData, isLoading: isTimetableLoading } =  useTimetable()
    const { isLoading: isThemeLoading, themeData,  } = useTheme(themeId)

    const toast = useToast()

    useEffect(() => {
        if(!isThemeLoading && !isTimetableLoading && (!timetableData || !themeData)) {
            toast.addToast('알 수 없는 오류가 발생하였습니다. 관리자에게 문의해주세요!', 'error')
            close()
        }
    }, [isThemeLoading, isTimetableLoading, timetableData, themeData, toast, themeId, close])

    if (isTimetableLoading || isTimetableLoading) {
        return (<div id='theme-preview-dialog'>
        </div>)
    }

    if (!timetableData || !themeData) {
        return (<div id='theme-preview-dialog'>
        </div>)
    }

    const { schedules } = timetableData;

    return (
        <div
            className="theme-preview-dialog"
        >
            <span>{title}</span>
            <div>
                <TimetableHeader/>
                <TimetableGrid schedules={schedules} colorSchemes={themeData.colorSchemes} detail={false}/>
            </div>
            <IconButton onClick={() => close()}>
                <Close/>
            </IconButton>
        </div>
    )
}

export default ThemePreviewDialog