import './ClassDetail.css'
import {Class, ClassDetail} from "../../types/class";

interface ContentProp {
    label: string;
    content: string;
}

const Content = ({label, content}: ContentProp) => {
    return (
        <div className='detail-content'>
            <span className='detail-content-label'>{label}</span>
            <span className='detail-content-content'>{content}</span>
        </div>
    );
}

interface ListContentProps {
    content: string;
}

// TODO : add hover and click event
const ListContent = ({content}: ListContentProps) => {
    return (
        <div className='detail-content-list'>
            <div className='detail-content-bullet'></div>
            <span className='detail-content-content'>{content}</span>
        </div>
    );
}

interface ClassDetailContentProps {
    classInfo: Class;
    detail: ClassDetail;
}

const ClassDetailContent = ({classInfo, detail}: ClassDetailContentProps) => {
    const icon = '../../assets/icon/icn_brush.png';

    return (
        <div className='detail-wrapper'>
            <div className='detail-subject-icon-wrapper'>
                <img className='detail-brush' alt='' src={icon}/>
                <span className='detail-subject'>{classInfo.subject}</span>
            </div>
            <Content label={classInfo.division.toString()} content=''/>

            <div className='detail-divider'/>
            <Content label='Tch' content={`${classInfo.teacher} Tr`}/>
            <Content label='Room' content={detail.room}/>

            <div className='detail-divider'/>
            <Content label='Students' content=''/>
            {detail.students.map(item => (
                <ListContent content={item.name}/>
            ))}
        </div>
    );
}

export default ClassDetailContent;