import React, {useCallback, useEffect} from "react";
import style from './Themes.module.css'
import Add from '../../resources/icon/icn_add.svg?react'
import {useThemes} from "../../hooks/theme/useThemes";
import {useToast} from "../../components/alert/toast/ToastContext";
import {useDialog} from "../../components/alert/dialog/DialogProvider";
import CreateThemeDialog from "../../components/alert/dialog/CreateThemeDialog";
import ThemeElement from "../../components/theme/ThemeElement";
import {Theme} from "../../types/theme";
import IconButton from "../../components/button/IconButton";

const Themes = () => {
    const { isLoading, themeData: themes, loadData } = useThemes();
    const { open, close, isOpen } = useDialog()

    const { addToast } = useToast();
    useEffect(() => {
        if (!isLoading && !themes) {
            addToast('테마를 불러오는 과정에서 오류가 발생하였습니다. 관리자에게 문의해주세요', 'error')
        }
    }, [isLoading, themes])

    const handleCreateTheme = useCallback(() => {
        open(<CreateThemeDialog
            context={{ open, close, isOpen }}
            onSuccess={async () => {await loadData()}}
        />)
    }, [open, close, isOpen])


    if (isLoading || (!themes)) {
        return (<div className={style.theme}>
            <span className={style.title}>시간표 테마</span>
            <div className={style.container}>
                <div className={style.subtitle}>
                    <span>나의 테마</span>
                    <IconButton onClick={handleCreateTheme} className={style.button}>
                        <Add/>
                    </IconButton>
                </div>
                <div className={style.subtitle}>
                    {/*<span>온라인 테마</span>*/}
                </div>
            </div>
        </div>)
    }


    return (
        <div className={style.theme}>
            <span className={style.title}>시간표 테마</span>
            <div className={style.container}>
                <div className={style.subtitle}>
                    <span>나의 테마</span>
                    <IconButton onClick={handleCreateTheme} className={style.button}>
                        <Add/>
                    </IconButton>
                </div>
                <div className={style.themeList}>
                    {themes.map((theme: Theme, index) => (
                        <ThemeElement theme={theme} key={index} loader={loadData}/>
                    ))}
                </div>
                <div className={style.subtitle}>
                    {/*<span>온라인 테마</span>*/}
                </div>
            </div>
        </div>
    )
}

export default Themes;