import React, {FC, SVGProps, useTransition} from "react";
import './ActionMenu.css'
import {FloatingContext, FloatingFocusManager, FloatingPortal, useTransitionStyles} from "@floating-ui/react";

export interface ActionMenuButton {
    icon: FC<SVGProps<SVGSVGElement>>;
    text: string;
    onClick: () => void;
    color?: string | undefined;
}

interface ActionMenuProps {
    context: FloatingContext;
    setFloating: any;
    floatingMenuProps: Record<string, unknown>;
    floatingStyles: React.CSSProperties;
    buttons: ActionMenuButton[];
}

const ActionMenu = ({
                        context,
                        setFloating,
                        floatingMenuProps,
                        floatingStyles,
                        buttons,
}: ActionMenuProps) => {
    const menuButtons = buttons.map((value, index) => {
        return <button
            key={index}
            onClick={value.onClick}
        >
            <value.icon style={{ fill: value.color }}/>
            <span style={{ color: value.color }}>{value.text}</span>
        </button>
    })

    const { styles } = useTransitionStyles(context, {
        duration: 100,
        initial: {
            transform: 'scale(0.9)',
            transformOrigin: 'top left',
            opacity: 0
        },
        open: {
            transform: 'scale(1)',
            transformOrigin: 'top left',
            opacity: 1,
        },
        close: {
            transform: 'scale(0.9)',
            transformOrigin: 'top left',
            opacity: 0,
        }
    })

    return (<FloatingPortal>
        <FloatingFocusManager context={context} modal={false}>
            <div
                className={'action-menu'}
                ref={setFloating}
                style={{
                    ...floatingStyles,
                    ...styles,
                    transform: `${floatingStyles.transform || ''} ${styles.transform || ''}`
                }}
                {...floatingMenuProps}
            >
                {menuButtons}
            </div>
        </FloatingFocusManager>
    </FloatingPortal>)
}

export default ActionMenu;