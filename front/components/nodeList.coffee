import DOM from 'react-dom-factories'
L = DOM

export default NodeList= ({nodeList,onRemove}) ->

    fileReader = null
    remove_node=(id)->(e)->
        console.log 'list: removing node',id
        onRemove(id)
        
    nodeElem = (data)->
        L.div
            className:'nodeElem'
            L.div className:'node id', data.id
            L.div className:'node name', data.name
            L.div className:'node cost', data.cost
            L.div
                className:'node rem button'
                onClick: remove_node(data.id)
                "rm"
    L.div
        className:'nodelist'
        L.div className:"nodelist title",
            "Nodes to elimitate:"
        L.div className:'nodelist container',
            if nodeList.length>0
                [ nodeElem n for n in nodeList ]
            else
                "no nodes in here. Try running some ordering algorithm"

