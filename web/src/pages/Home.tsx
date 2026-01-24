import {Class} from "../types/class";
import {Schedule} from "../types/schedule";
import SideBar from "../components/sidebar/SideBar";
import Timetable from "../components/timetable/Timetable";
import DetailBar from "../components/detailBar/DetailBar";
import './Home.css';
import {fetchTimetable} from "../api/fetchTimetable";
import {useEffect, useState} from "react";
import timetable from "../components/timetable/Timetable";

interface TimetableData {
    name: string;
    schedules: Schedule[];
    classes: Class[];
}

function Home() {
    const [timetableData, setTimetableData] = useState<TimetableData | null>();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            try {
                const data = await fetchTimetable();
                setTimetableData(data)
            } catch (error: any) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        };

        loadData()
    }, [])

    if (loading) {
        return (
            <div id={'home'}>
                <Timetable name={''} schedules={[]}/>
                <DetailBar quote="달을 향해 쏴라. 빗나가도 별이 될테니" source="레스 브라운" image="/assets/image/detail_image.png"/>
            </div>)
    }

    if (!timetableData) {
        return <div className='error-message'>알 수 없는 오류가 발생하였습니다. 관리자에게 문의해 주세요</div>
    }

    const { name, schedules, classes } = timetableData;
    return (
        <div id="home">
            <Timetable name={name} schedules={schedules}/>
            <DetailBar quote="달을 향해 쏴라. 빗나가도 별이 될테니" source="레스 브라운" image="/assets/image/detail_image.png"/>
        </div>
    )
}

export default Home;