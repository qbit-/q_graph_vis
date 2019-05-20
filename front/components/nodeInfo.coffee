import DOM from 'react-dom-factories'
L = DOM

export default NodeInfo = ({info}) ->
    entity=(label,val)->
        L.div
            className:'info-entity'
            L.span
                className:'entity-label'
                style:margin:'2px 10px'
                label
            L.span
                className:'entity-value'
                val
    L.div
        className:'nodeInfo'
        entity 'Expression:', info.expr
        entity 'Memory:', info.mem
        entity 'FLOPS:', info.flops




