import React, {useCallback, useState} from "react";
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
import {deleteTheme} from "../../api/fetchTheme";
import DeleteConfirmDialog from "../alert/dialog/DeleteConfirmDialog";
import {useDialog} from "../alert/dialog/DialogProvider";
import {useToast} from "../alert/toast/ToastContext";
import useThemeActions from "../../hooks/useThemeActions";

interface ThemeElementProps {
    theme: Theme;
}

const ThemeElement = ({theme}: ThemeElementProps) => {
    const { ref: containerRef, width } = useContainerSize();
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const { open, close, isOpen }  = useDialog()

    const navigate = useNavigate();

    const handleView = () => {
        navigate(`/theme/${theme.theme_id}`)
    }

    const cardNumbers = theme.colorSchemes.length
    const cards = theme.colorSchemes.map((colorSchema, index) => {
        const cardWidth = 160
        const gap = Math.min(width * 0.15, (width-cardWidth) / cardNumbers)
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

    const { handleDeleteTheme } = useThemeActions(theme.theme_id)

    const handleConfirmDelete = useCallback(async () => {
        await handleDeleteTheme()
        close()
    }, [handleDeleteTheme, close])

    const handleDelete = () => {
        open(<DeleteConfirmDialog
            context={{ open, close, isOpen }}
            content={'한 번 삭제한 테마는 다시 복구할 수 없습니다. \n그래도 삭제하시겠습니까?'}
            onConfirm={handleConfirmDelete}
            />
        )
    }



    const buttons = [
        { icon: Pencil, text: '수정' , onClick: () => alert('test - trash') },
        { icon: Share, text: '온라인에 공유' , onClick: () => alert('test - trash') },
        { icon: Trashcan, text: '휴지통으로 이동' , onClick: handleDelete, color: '#ff0000' },
    ]

    const { refs, floatingStyles, context } = useFloating({
        open: isMenuOpen,
        onOpenChange: setIsMenuOpen,
        placement: 'bottom-start',
        whileElementsMounted: (reference, floating, update) =>
            autoUpdate(reference, floating, update, {
                layoutShift: false
            }),
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
                <button onClick={handleView} title={'테마 미리보기'}>
                    <View/>
                </button>
                <button
                    className={isMenuOpen ? 'clicked' : ''}
                    title={'옵션 더보기'}
                    ref={refs.setReference}
                    {...getReferenceProps()}
                >
                    <Options/>
                </button>
            </div>

            {isMenuOpen && <ActionMenu
                context={context}
                setFloating={refs.setFloating}
                floatingMenuProps={getFloatingProps()}
                floatingStyles={floatingStyles}
                buttons={buttons}
                isOpen={isMenuOpen}
            />}
        </div>
    )
}

export default ThemeElement;