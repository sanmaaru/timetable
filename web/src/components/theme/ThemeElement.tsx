import React, {useCallback, useState} from "react";
import style from './ThemeElement.module.css'
import {Theme} from "../../types/theme";
import useContainerSize from "../../hooks/useContainerSize";
import View from '../../resources/icon/icn_eye.svg?react';
import Options from '../../resources/icon/icn_options.svg?react'
import {useNavigate} from "react-router-dom";
import {autoUpdate, flip, offset, shift, useClick, useDismiss, useFloating, useInteractions} from "@floating-ui/react";
import ActionMenu from "../ActionMenu";
import {useDialog} from "../alert/dialog/DialogProvider";
import useThemeActions from "../../hooks/theme/useThemeActions";
import ThemePreviewDialog from "../alert/dialog/ThemePreviewDialog";

import Trashcan from '../../resources/icon/icn_trashcan.svg?react'
import Pencil from '../../resources/icon/icn_pencil.svg?react'
// import Share from '../../resources/icon/icn_share.svg?react'
import Magnifier from '../../resources/icon/icn_magnifier.svg?react'
import Sparkle from '../../resources/icon/icn_sparkle.svg?react'
import DefaultDialog from "../alert/dialog/DefaultDialog";
import IconButton from "../button/IconButton";
import useFloatingMenu from "../../hooks/useFloatingMenu";
import {useIsMobile} from "../../hooks/useMediaQuery";

interface ThemeElementProps {
    theme: Theme;
    loader: () => void;
}

const ThemeElement = ({theme, loader}: ThemeElementProps) => {
    const { ref: containerRef, width } = useContainerSize();
    const [isMenuOpen, setMenuOpen] = useState(false);
    const { open, close, isOpen }  = useDialog()
    const navigate = useNavigate();
    const { handleDeleteTheme, handlePutSelectedTheme } = useThemeActions(theme.themeId)
    const isMobile = useIsMobile();

    const selected = theme.selected

    const cardNumbers = theme.colorSchemes.length
    const cards = theme.colorSchemes.map((colorSchema, index) => {
        const cardWidth = 120;
        const gap = Math.min(width * 0.15, (width-cardWidth) / cardNumbers)
        const leftPos = gap * index

        return (
            <div
                className={style.card}
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
    const handleConfirmChange = useCallback(async () => {
        await handlePutSelectedTheme(loader)
        close()
    }, [handlePutSelectedTheme, close, loader])

    const handleChange = useCallback(() => {
        if (selected)
            return;

        open(<DefaultDialog
            context={{ open, close, isOpen }}
            title={'! 정말로 변경하시겠습니까?'}
            onConfirm={handleConfirmChange}
            confirm={'변경'}
        >{`사용자의 시간표의 테마를 \'${theme.title}\'로 바꾸시겠습니까?`}</DefaultDialog>)
    }, [selected, theme.title, open, close, isOpen, handleConfirmChange]);

    const handleView = useCallback(() => {
        open(<ThemePreviewDialog
            context={{ open, close, isOpen }}
            themeId={theme.themeId}
            title={theme.title}
        />)
    }, [open, close, isOpen]);

    const handleDelete = () => {
        open(<DefaultDialog
            context={{ open, close, isOpen }}
            title={'! 정말로 삭제하시겠습니까?'}
            onConfirm={handleConfirmDelete}
            color={'#ff0000'}
            confirm={'삭제'}
        >한번 삭제한 테마는 다시 복구할 수 없습니다. \n그래도 삭제하시겠습니까?</DefaultDialog>)
    }

    const handleConfirmDelete = useCallback(async () => {
        await handleDeleteTheme(loader)
        close()
    }, [handleDeleteTheme, close])


    const { menuContext, getReferenceProps, ref } = useFloatingMenu(isMenuOpen, setMenuOpen)

    const buttons = [
        { icon: Pencil, text: '수정' , onClick: () => navigate(`/theme/${theme.themeId}/edit`) },
        { icon: Magnifier, text: '미리보기', onClick: () => navigate(`/theme/${theme.themeId}`) },
        { icon: Trashcan, text: '휴지통으로 이동' , onClick: handleDelete, color: '#ff0000' },
    ]

    return (
        <div className={style.themeElement}>
            <div className={style.cards} ref={containerRef}>
                {width > 0 && cards}
            </div>
            <div className={style.descriptions}>
                <span title={theme.title}>{theme.title}</span>
                <IconButton
                    onClick={handleChange}
                    title={selected ? '사용 중인 테마' : '테마 사용하기'}
                    className={`${style.button} ${selected ? style.selected : ''}`}
                >
                    <Sparkle/>
                </IconButton>
                {!isMobile && <IconButton className={style.button} onClick={handleView} title={'테마 미리보기'}>
                    <View/>
                </IconButton>}
                <IconButton
                    className={`${style.button} ${style.menu} ${isMenuOpen ? style.clicked : ''}`}
                    title={'옵션 더보기'}
                    props={{
                        ref: ref,
                        ...getReferenceProps()
                    }}
                >
                    <Options/>
                </IconButton>
            </div>

            <ActionMenu context={menuContext} buttons={buttons}/>
        </div>
    )
}

export default ThemeElement;