import Timetable from "../components/timetable/Timetable";
import DetailBar from "../components/detailBar/DetailBar";
import './Home.css';
import useTimetable from "../hooks/useTimetable";


function Home() {
    const { timetableData, isLoading } = useTimetable();
    const themes = null;

    if (isLoading) {
        return (
            <div id={'home'}>
                <Timetable name={''} schedules={[]} theme={{}}/>
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