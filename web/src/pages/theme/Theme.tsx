import React from "react";
import './Theme.css'
import ThemeList from "../../components/theme/ThemeList";
import Add from '../../resources/icon/icn_add.svg?react'
import { useThemes } from "../../hooks/useThemes";

const Theme = () => {
    const { loading, themeData: themes } = useThemes();

    if (loading) {
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

    if (!themes) {
        return (<div>
            알 수 없는 오류가 발생했습니다. 관리자에게 문의해주세요
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