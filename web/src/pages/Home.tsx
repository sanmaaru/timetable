import {Class} from "../types/class";
import {Schedule} from "../types/schedule";
import SideBar from "../components/sidebar/SideBar";
import Timetable from "../components/timetable/Timetable";
import DetailBar from "../components/detailBar/DetailBar";
import './Home.css';

function Home() {
    const name = '조시우';
    const classes: Class[] = [
        {color: "#F5F2F2", textColor: "#111111", subject: "일반물리학", teacher: "김광식", division: 2},
        {color: "#2B2A2A", textColor: "#EEEEEE", subject: "선형대수학", teacher: "최병길", division: 2},
        {color: "#2B2A2A", textColor: "#EEEEEE", subject: "선형대수학", teacher: "전강민", division: 2},
        {color: "#5A7ACD", textColor: "#EEEEEE", subject: "인공지능과 프로그래밍", teacher: "이동윤", division: 2}
    ];
    const schedules: Schedule[] = [
        {day: "Mon", period_from: 1, period_to: 1, class: classes[0]},
        {day: "Tue", period_from: 3, period_to: 4, class: classes[1]},
        {day: "Thu", period_from: 3, period_to: 4, class: classes[2]},
        {day: "Wed", period_from: 7, period_to: 7, class: classes[3]},
    ];

    return (
        <div id="home">
            <SideBar/>
            <Timetable name={name} schedules={schedules}/>
            <DetailBar quote="달을 향해 쏴라. 빗나가도 별이 될테니" source="레스 브라운" image="/assets/image/detail_image.png"/>
        </div>
    )
}

export default Home;