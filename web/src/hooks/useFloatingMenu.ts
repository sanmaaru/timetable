import {
    autoUpdate,
    flip, FloatingContext,
    offset,
    shift,
    useClick,
    useDismiss,
    useFloating,
    useInteractions,
    useTransitionStyles
} from "@floating-ui/react";
import {getTransformOrigin} from "../constants/placements";
import {CSSProperties, HTMLProps} from "react";

export interface FloatingMenuContext {
    isMounted: boolean;
    setOpen: (value: boolean) => void;
    styles: CSSProperties;
    context: FloatingContext;
    floatingProps: (userProps?: (HTMLProps<HTMLElement> | undefined)) => Record<string, unknown>;
    ref: (node: (HTMLElement | null)) => void;
}

const useFloatingMenu = (open: boolean, setOpen: (value: boolean) => void) => {
    const {
        refs,
        floatingStyles,
        context
    } = useFloating({
        open: open,
        onOpenChange: setOpen,
        placement: 'bottom-start',
        strategy: 'fixed',
        middleware: [
            offset(8),
            flip({ padding: 8 }),
            shift({ padding: 8 })
        ],
        whileElementsMounted: autoUpdate
    })

    const dismiss = useDismiss(context, {
        bubbles: false,
        outsidePressEvent: 'mousedown'
    })
    const click = useClick(context)
    const { getReferenceProps, getFloatingProps } = useInteractions([ dismiss, click ])

    const { isMounted, styles: transitionStyles } = useTransitionStyles(context, {
        duration: 100,
        common: ({placement}) =>({
            transformOrigin: getTransformOrigin(placement)
        }),
        initial: {
            transform: 'scale(0.9)',
            opacity: 0,
        },
        open: {
            transform: 'scale(1)',
            opacity: 1,
        },
        close: {
            transform: 'scale(0.9)',
            opacity: 0,
        }
    })

    const styles = {
        ...floatingStyles,
        ...transitionStyles,
        transform: `${floatingStyles.transform || ''} ${transitionStyles.transform || ''}`,
        zIndex: 9999
    }

    const menuContext = {
        isMounted,
        setOpen,
        styles,
        context,
        floatingProps: getFloatingProps,
        ref: refs.setFloating,
    }

    return { menuContext, getReferenceProps, ref: refs.setReference  }
}


export default useFloatingMenu