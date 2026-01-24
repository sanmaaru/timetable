import React, {useEffect, useRef, useState} from "react";
import './ThemeElement.css'
import {Theme} from "../../types/theme";
import More from '../../resources/icon/icn_more.svg?react'
import Pencil from '../../resources/icon/icn_pencil.svg?react'
import Share from '../../resources/icon/icn_share.svg?react'
import Eye from '../../resources/icon/icn_eye.svg?react'
import Trashcan from '../../resources/icon/icn_trashcan.svg?react'

interface ThemeElementProps {
    theme: Theme;
}

const ThemeElement = ({theme}: ThemeElementProps) => {
    const containerRef = useRef(null);
    const [overlapMargin, setOverlapMargin] = useState(0);

    const cardWidth = 200
    const count = theme.colorSchemas.length

    useEffect(() => {
        const calculateMargin = () => {
            if (!containerRef.current) {
                return;
            }

            if (count <= 1) {
                setOverlapMargin(0);
                return;
            }

            const containerWidth = containerRef.current.offsetWidth;
            const totalCardsWidth = count * cardWidth;
            const margin = (containerWidth - totalCardsWidth) / (count - 1);
            setOverlapMargin(margin)
        }

        calculateMargin();

        const observer = new ResizeObserver(() => {
            calculateMargin();
        });

        if (containerRef.current)
            observer.observe(containerRef.current);

        return () => observer.disconnect()
    }, [count, cardWidth])

    return (
        <div className="theme-element">
            <div className='body' ref={containerRef}>
                {theme.colorSchemas.map((colorSchema, index) => {
                    return (<div className={'item'} key={index} style={{
                        background: colorSchema.color,
                        color: colorSchema.color,
                        boxShadow: `3px 3px 5px 1px #bababa`,
                        zIndex: index,
                        width: cardWidth,
                        marginLeft: index == 0 ? 0 : `${overlapMargin}px`,
                    }}>
                    </div>)
                })}
            </div>
            <div className={`footer`}>
                <span>{theme.title}</span>
                <div className='icons'>
                    <Pencil/>
                    <Share/>
                    <Eye/>
                    <Trashcan className={'trashcan'}/>
                </div>
            </div>
        </div>
    )
}

export default ThemeElement;