import {
    autoUpdate,
    flip,
    offset,
    shift,
    useClick,
    useDismiss,
    useFloating,
    useInteractions,
    useTransitionStyles
} from "@floating-ui/react";
import React from "react";
import {getTransformOrigin} from "../../constants/placements";


const usePalette = (initialOpen = false) => {
    const [isOpen, setOpen] = React.useState(initialOpen);
    const { refs, floatingStyles, context, placement } = useFloating({
        open: isOpen,
        onOpenChange: setOpen,
        placement: 'bottom-start',
        whileElementsMounted: autoUpdate,
        middleware: [
            offset(5),
            flip(),
            shift()
        ]
    })

    const click = useClick(context)
    const dismiss = useDismiss(context)

    const { getReferenceProps, getFloatingProps } = useInteractions([
        click, dismiss
    ])

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
    }

    const paletteContext = {
        isMounted: isMounted,
        setOpen: setOpen,
        styles: styles,
        getFloatingProps: getFloatingProps,
        context: context,
    }

    return {
        isOpen,
        setOpen,
        refs,
        getReferenceProps,
        paletteContext,
    }
}

export default usePalette;