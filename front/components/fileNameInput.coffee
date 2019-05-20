import DOM from 'react-dom-factories'
L = DOM

export default FileNameInput = ({onRead}) ->
    fileReader = null
    submit = (e)->
        t = document.getElementById('filename')
        onRead(t.value)

    L.div className:'input-file',
        L.input
            type:'text'
            id:'filename'
            defaultValue:'inst_2x2_7_0.txt'
        L.button
            className:'submitfn'
            onClick:submit
            "Load by filename"



