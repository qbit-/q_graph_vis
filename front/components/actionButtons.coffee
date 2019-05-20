import DOM from 'react-dom-factories'
L = DOM

export default ActionButtons= ({buttons}) ->
    if not buttons
        buttons = [
            {text:"Run quickBB",fun:()->console.log("Runqbb")}
            {text:"Run greedy",fun:()->console.log("greedy")}
            {text:"Select all low-grade nodes",fun:()->console.log("low grade")}
            ]

    button = (button)->
        L.div
            className:'action button'
            onClick: button.fun
            button.text
    L.div
        className:'actions'
        "Buttons"
        L.div '',
            [ button b for b in buttons]

