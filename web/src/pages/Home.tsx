import Timetable from "../components/timetable/Timetable";
import DetailBar from "../components/detailBar/DetailBar";
import style from './Home.module.css';
import useTimetable from "../hooks/useTimetable";
import {useToast} from "../components/alert/toast/ToastContext";
import {useCallback, useEffect, useState} from "react";
import {useTheme} from "../hooks/theme/useThemes";
import {useIsMobile} from "../hooks/useMediaQuery";
import {useDialog} from "../components/alert/dialog/DialogProvider";
import MobileDetailDialog from "../components/alert/dialog/MobileDetailDialog";


function Home() {
    const [focus, setFocus] = useState<string | null>(null)
    const { timetableData, isLoading: isTimetableLoading, getSchedule } = useTimetable();
    const { themeData, isLoading: isThemeLoading } = useTheme();
    const toast = useToast()
    const isMobile = useIsMobile()
    const dialog = useDialog();

    useEffect(() => {
        if(!isThemeLoading && !isTimetableLoading && (!timetableData || !themeData)) {
            console.log(themeData, timetableData)
            toast.addToast('알 수 없는 오류가 발생하였습니다. 관리자에게 문의해주세요!', 'error')
        }
    }, [isThemeLoading, isTimetableLoading, timetableData, themeData, toast])

    const drawDetail = useCallback(() => {
        if(isMobile) return;

        let schedule
        if (!focus) schedule = null
        else
            schedule = getSchedule(focus)

        return <DetailBar
            quote="달을 향해 쏴라. 빗나가도 별이 될테니"
            source="레스 브라운"
            schedule={schedule}
        />

    }, [focus, isMobile])

    useEffect(() => {
        if (!isMobile) return

        if(!focus) {
            dialog.close();
            return
        }

        const schedule = getSchedule(focus)
        if (!schedule)
            return

        dialog.open(
            <MobileDetailDialog
                context={dialog}
                schedule={schedule}
                setFocus={setFocus}
            />
        )
    }, [isMobile, focus]);

    if (isThemeLoading || isTimetableLoading || (!timetableData || !themeData)) {
        return (
            <div className={style.home}>
                <Timetable name={''} schedules={[]} theme={{ title: '', themeId: '', colorSchemes: [], selected: false }} focus={focus} setFocus={setFocus} />
                {!isMobile && <DetailBar quote="달을 향해 쏴라. 빗나가도 별이 될테니" source="레스 브라운"/>}
            </div>)
    }

    const { name, schedules } = timetableData;
    return (
        <div className={style.home}>
            <Timetable name={name} schedules={schedules} theme={themeData} focus={focus} setFocus={setFocus}/>
            {drawDetail()}
        </div>
    )
}

export default Home;