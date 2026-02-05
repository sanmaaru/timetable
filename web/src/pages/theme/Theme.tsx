import React, {useEffect} from "react";
import './Theme.css'
import ThemeList from "../../components/theme/ThemeList";
import Add from '../../resources/icon/icn_add.svg?react'
import { useThemes } from "../../hooks/useThemes";
import {useToast} from "../../components/alert/toast/ToastContext";

const Theme = () => {
    const { isLoading, themeData: themes } = useThemes();

    const { addToast } = useToast();
    useEffect(() => {
        if (!isLoading && !themes) {
            addToast('테마를 불러오는 과정에서 오류가 발생하였습니다. 관리자에게 문의해주세요', 'error')
        }
    }, [isLoading, themes])

    if (isLoading || (!themes)) {
        return (<div id={'theme'}>
            <span className='title'>시간표 테마</span>
            <div className='container'>
                <div className='subtitle'>
                    <span>나의 테마</span>
                    <Add/>
                </div>
                <div className='subtitle'>
                    <span>온라인 테마</span>
                </div>
            </div>
        </div>)
    }


    return (
        <div id={'theme'}>
            <span className='title'>시간표 테마</span>
            <div className='container'>
                <div className='subtitle'>
                    <span>나의 테마</span>
                    <Add/>
                </div>
                <ThemeList themes={themes}/>
                <div className='subtitle'>
                    <span>온라인 테마</span>
                </div>
            </div>
        </div>
    )
}

export default Theme;