import Timetable from "../components/timetable/Timetable";
import DetailBar from "../components/detailBar/DetailBar";
import './Home.css';
import useTimetable from "../hooks/useTimetable";
import {useToast} from "../components/alert/toast/ToastContext";
import {useEffect} from "react";
import {useTheme} from "../hooks/theme/useThemes";


function Home() {
    const { timetableData, isLoading: isTimetableLoading } = useTimetable();
    const { themeData, isLoading: isThemeLoading } = useTheme();
    const toast = useToast()

    useEffect(() => {
        if(!isThemeLoading && !isTimetableLoading && (!timetableData || !themeData)) {
            console.log(themeData, timetableData)
            toast.addToast('알 수 없는 오류가 발생하였습니다. 관리자에게 문의해주세요!', 'error')
        }
    }, [isThemeLoading, isTimetableLoading, timetableData, themeData, toast])

    if (isThemeLoading || isTimetableLoading || (!timetableData || !themeData)) {
        return (
            <div id={'home'}>
                <Timetable name={''} schedules={[]} theme={{ title: '', theme_id: '', colorSchemes: [], selected: false }}/>
                <DetailBar quote="달을 향해 쏴라. 빗나가도 별이 될테니" source="레스 브라운" image="/assets/image/detail_image.png"/>
            </div>)
    }

    const { name, schedules } = timetableData;
    return (
        <div id="home">
            <Timetable name={name} schedules={schedules} theme={themeData}/>
            <DetailBar quote="달을 향해 쏴라. 빗나가도 별이 될테니" source="레스 브라운" image="/assets/image/detail_image.png"/>
        </div>
    )
}

export default Home;