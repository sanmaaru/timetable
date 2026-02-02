import React from "react";
import './ThemeElement.css'
import {Theme} from "../../types/theme";
import useContainerSize from "../../hooks/useContainerSize";
import View from '../../resources/icon/icn_eye.svg?react';
import Options from '../../resources/icon/icn_options.svg?react'
import {useNavigate} from "react-router-dom";
import {autoUpdate, flip, offset, shift, useClick, useDismiss, useFloating, useInteractions} from "@floating-ui/react";
import ActionMenu from "../ActionMenu";
import Trashcan from '../../resources/icon/icn_trashcan.svg?react'
import Pencil from '../../resources/icon/icn_pencil.svg?react'
import Share from '../../resources/icon/icn_share.svg?react'

interface ThemeElementProps {
    theme: Theme;
}

const ThemeElement = ({theme}: ThemeElementProps) => {
    const { ref: containerRef, width, height } = useContainerSize();
    const [isOpen, setIsOpen] = React.useState(false);

    const navigate = useNavigate();

    const onClickView = () => {
        navigate(`/theme/${theme.theme_id}`)
    }

    const cardNumbers = theme.colorSchemas.length
    const cards = theme.colorSchemas.map((colorSchema, index) => {
        const cardWidth = 160
        const gap = Math.max(width * 0.15, (width-cardWidth) / cardNumbers)
        const leftPos = gap * index

        return (
            <div
                className='card'
                key={`card-${index}`}
                style={{
                    zIndex: cardNumbers-index,
                    width: `${cardWidth}px`,
                    background: colorSchema.color,
                    color: colorSchema.textColor,
                    left: `${leftPos}px`,
                }}>
                <span>{colorSchema.subject}</span>
                <span>{colorSchema.color}</span>
            </div>
        )
    })

    const buttons = [
        { icon: Pencil, text: '수정' , onClick: () => alert('test - trash') },
        { icon: Share, text: '온라인에 공유' , onClick: () => alert('test - trash') },
        { icon: Trashcan, text: '휴지통으로 이동' , onClick: () => alert('test - trash'), color: '#ff0000' },
    ]

    const { refs, floatingStyles, context } = useFloating({
        open: isOpen,
        onOpenChange: setIsOpen,
        placement: 'bottom-start',
        whileElementsMounted: autoUpdate,
        middleware: [
            offset(5),
            flip(),
            shift(),
        ]
    })

    const click = useClick(context)
    const dismiss = useDismiss(context)

    const { getReferenceProps, getFloatingProps } = useInteractions([
        click,
        dismiss
    ])

    return (
        <div className="theme-element">
            <div className="cards" ref={containerRef}>
                {width > 0 && cards}
            </div>
            <div className='descriptions'>
                <span className='title' title={theme.title}>{theme.title}</span>
                <button onClick={onClickView} title={'테마 미리보기'}>
                    <View/>
                </button>
                <button
                    className={isOpen ? 'clicked' : ''}
                    title={'옵션 더보기'}
                    ref={refs.setReference}
                    {...getReferenceProps()}
                >
                    <Options/>
                </button>
            </div>

            {isOpen && <ActionMenu
                context={context}
                setFloating={refs.setFloating}
                floatingMenuProps={getFloatingProps()}
                floatingStyles={floatingStyles}
                buttons={buttons}/>}
        </div>
    )
}

export default ThemeElement;