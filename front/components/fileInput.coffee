import DOM from 'react-dom-factories'
L = DOM

export default FileInput = ({onRead}) ->
	fileReader = null
	read = (e)->
		console.log e
		content = fileReader.result
		onRead(content)
	chosen = (file)->
		fileReader = new FileReader()
		fileReader.onloadend = read
		fileReader.readAsText(file)

	L.div
		className:'input-file'
		"Choose circuit file:"
		L.input
			type:'file'
			id:'file'
			onChange:(e)->chosen e.target.files[0]



