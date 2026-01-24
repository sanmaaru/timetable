import React from "react";
import './Theme.css'
import ThemeList from "../components/theme/ThemeList";
import Add from '../resources/icon/icn_add.svg?react'

const Theme = () => {
    const themes = [
        { title: '조시우님의 테마', colorSchemas: [
                { subject: '선형대수학', color: '#5a7acd', textColor: '#ffffff' },
                { subject: '선형대수학', color: '#ff0000', textColor: '#ffffff' },
                { subject: '선형대수학', color: '#00ff00', textColor: '#ffffff' },
                { subject: '선형대수학', color: '#0000ff', textColor: '#ffffff' }
            ]
        },
        { title: '조시우님의 테마 (1)', colorSchemas: [
                { subject: '선형대수학', color: '#ff0000', textColor: '#ffffff' }
            ]
        }
    ]

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