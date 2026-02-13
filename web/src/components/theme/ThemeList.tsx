import React from 'react';
import './ThemeList.css';
import ThemeElement from "./ThemeElement";
import {Theme} from "../../types/theme";
import {DialogProvider} from "../alert/dialog/DialogProvider";

interface ThemeListProps {
    themes: Theme[]
    loader: () => void;
}

const ThemeList = ({themes, loader}: ThemeListProps) => {
    const drawThemeElements = (themes: Theme[]) => (
        themes.map((theme: Theme, index) => (
            <ThemeElement theme={theme} key={index} loader={loader}/>
        ))
    )

    return (
        <div className='theme-list'>
            <DialogProvider>
                {drawThemeElements(themes)}
            </DialogProvider>
        </div>
    );
}

export default ThemeList;