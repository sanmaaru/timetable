import React, {useCallback, useEffect} from "react";
import './Theme.css'
import ThemeList from "../../components/theme/ThemeList";
import Add from '../../resources/icon/icn_add.svg?react'
import { useThemes } from "../../hooks/theme/useThemes";
import {useToast} from "../../components/alert/toast/ToastContext";
import {useDialog} from "../../components/alert/dialog/DialogProvider";
import CreateThemeDialog from "../../components/alert/dialog/CreateThemeDialog";

const Theme = () => {
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
        return (<div id={'theme'}>
            <span className='title'>시간표 테마</span>
            <div className='container'>
                <div className='subtitle'>
                    <span>나의 테마</span>
                    <button>
                        <Add/>
                    </button>
                </div>
                <div className='subtitle'>
                    {/*<span>온라인 테마</span>*/}
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
                    <button onClick={handleCreateTheme}>
                        <Add/>
                    </button>
                </div>
                <ThemeList themes={themes} loader={loadData}/>
                <div className='subtitle'>
                    {/*<span>온라인 테마</span>*/}
                </div>
            </div>
        </div>
    )
}

export default Theme;