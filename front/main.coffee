import React from "react"
import ReactDOM from "react-dom"
import axios from 'axios'
import DOM from 'react-dom-factories'

import {Graph} from 'react-d3-graph'

import FileInput from './components/fileInput.coffee'
import FileNameInput from './components/fileNameInput.coffee'
import NodeInfo from './components/nodeInfo.coffee'
import NodeList from './components/nodeList.coffee'
import ActionButtons from './components/actionButtons.coffee'

import * as Gv from './components/graph.coffee'
import * as Chart from './components/chart.coffee'

import graphConfig from './graphConfig.js'

log = console.log
L_ = React.createElement
L = DOM

# graph payload (with minimalist structure)
export default class App extends React.Component
    constructor:(props)->
        super(props)
        @state=
            nodeInfo:
                expr:undefined
                mem:undefined
                flops:undefined
            graphData: {
                nodes: [ {id:'a'} , {id: 'b'} , {id: 'c'} ],
                links: [ {source: 'c' , target: 'a',id:123} , {source: 'a', target: 'b',id:13} ]
                }
        @api_path='http://'+location.hostname+':5000'
        @graphStyle =
            nodeColor:'red'
            lineColor:'#a3e1cc'
        @shift= 0
        @chartData = [{index:0,value:0}]
        document.body.onkeydown = (e)=>
            if (e.keyCode == 16)
                @shift = true
        document.body.onkeyup = (e)=>
            if (e.keyCode == 16)
                @shift =false

    startGraph:(graph)=>
        vis = Gv.start
            data:graph
            style:@graphStyle
            onClick:@onClickNode
            onMouseOver:@onOverNode
        @sim = vis
    startChart:(data)=>
        vis = Chart.start
            data:data
    updateChart:(data)=>
        vis = Chart.update
            data:data
    addDataPoints:(e)=>
        l = @chartData.length
        @chartData.push({index:l+3,value:Math.random()*10})
        @updateChart @chartData
        
    componentDidMount:()=>
        @startGraph @state.graphData
        @startChart @chartData
        return
    componentDidUpdate:()=>
        if @shift
            return
        Gv.update
            data:@state.graphData
            onClick:@onClickNode
            onMouseOver:@onOverNode
            style:@graphStyle
            sim:@sim
        return
    # graph event callbacks
    onOverNode:(nodeId)=>
        #@setState @set_node nodeId, color:'blue'
        log 'over'
        if not @shift
            return
        @getNodeInfo(nodeId)
    onOutNode:(nodeId)=>
        #@setState @set_node nodeId, color:''
    onClickNode:(nodeId) =>
        if @chosen_node==nodeId
            log 'Eliminating node',nodeId
            @eliminate(nodeId)
        else
            log 'Chosen node',nodeId
            @getNodeInfo(nodeId)
            @chosen_node=nodeId
    highlightNodes:(ids,props)=>(state,_)->
        nodes = state.graphData.nodes
        for node in nodes
            if ids.indexOf(node.id)==-1
                for k in Object.keys(props)
                    node[k]=''
            else
                for k in Object.keys(props)
                    node[k]=props[k]
        return state

    set_node:(id,props)=>(state,_)->
        nodes = state.graphData.nodes
        if Object.keys(props).length==0
            return null
        n_ = nodes.map (el)=>
            if el.id==parseInt id
                n_el = Object.assign el, props
                return n_el
            else
                el
        state.graphData.nodes = n_
        return state

    pushFlopsChart:(nodeId)=>
        info = @state.nodeInfo
        if nodeId!=info.id
            @getNodeInfo(nodeId).then (info)=>
                @chartData.push index:@chartData.length,value:info.flops
                @updateChart(@chartData)
        else
            @chartData.push index:@chartData.length,value:info.flops
            @updateChart(@chartData)
    ## Endpoint methods
    callQBB:()=>
        axios.get @api_path+'/get_qbb_ordering'
            .then (r)=>
                @setState nodeList:@onOrderingReceived(r.data)

    eliminate:(nodeId)=>
        @pushFlopsChart(nodeId)
        axios.get @api_path+'/eliminate',params:vertex_id:nodeId
            .then (r)=>
                @setState graphData:@onGraphReceived(r.data)

    getNodeInfo:(id)=>
        #@setState @highlightNodes [id], color:'red'
        axios.get @api_path+'/node_info',params:vertex_id:id
            .then (r)=>
                info = r.data
                log 'got info',info
                info.id = id
                @setState nodeInfo:info
                info
    # -------

    filter_self_loops:(graph)->
        #TODO: check the validity of graph
        return graph
    elimQueue:()=>
        @state.nodeList.reduce (p, next ,i)=>
            p.then ()=>
                new Promise (resolve)=>
                    log 'eliminating queue node',next
                    @eliminate next.id
                    setTimeout (()-> resolve()), 1000
        , Promise.resolve()

    onOrderingReceived: (qbb_result)=>
        {nodes} = @state.graphData
        console.log 'gd',@state.graphData
        {ordering}=qbb_result
        ordered_nodes = ordering.map (nodeId)->
            n = nodes.filter((n)=>n.id==nodeId)[0]
            log n
            return n
        log 'ord,no',ordered_nodes, nodes
        return ordered_nodes

    onGraphReceived: (graph)=>
        {links,nodes} = graph
        fl = links.map (l)->
            l.id = l.tensor+' ('+l.source+'.'+l.target
            return l

        graph.links = fl
        # use only nodes with names
        graph.nodes = nodes.filter (n)-> n.name?
        return graph

    onFileNameRead:(file)=>
        api_path=@api_path+'/parse_graph'
        axios.post api_path, 'inst_name='+file
            .then (resp)=>
                log 'response',resp
                #TODO: figure out why setState not working
                @state.graphData = @onGraphReceived(resp.data)
                @startGraph @onGraphReceived(resp.data)
    onFileRead:(file)=>
        api_path=@api_path+'/parse_graph'
        axios.post api_path, 'inst='+file
            .then (resp)=>
                log 'response',resp
                @state.graphData = @onGraphReceived(resp.data)
                @startGraph @onGraphReceived(resp.data)

    render:()->
        data = @state.graphData
        span = (t)->L.span className:'note',t
        L.div
            className:'main-cont'
            L.div className:'controls',style:display:'flex',#flexWrap:'wrap',
                L.div className:'loading_info',style:width:'78%',display:'inline-block',
                    L_ FileInput,
                        onRead:@onFileRead
                    L_ FileNameInput,
                        onRead:@onFileNameRead
                    NodeInfo info:@state.nodeInfo
                    Chart.Ui w:'300px',h:'120px'
                L.div className:'elim',style:width:'20%',minWidth:'160px',
                    ActionButtons( buttons:
                        [
                            text:'Run QuickBB',fun:@callQBB
                        ,
                            text:'Eliminate queue',fun:@elimQueue
                        ]
                    )
                    NodeList nodeList:@state.nodeList||[]
            L.div className:'desc',
                span 'Hover on node with shift key pressed to get node info'
                span 'Move node to pin it'
                span 'Click on node to eliminate it'
                span 'Drag and zoom is supported'
            Gv.Ui w:'100%',h:'100%'

ReactDOM.render(React.createElement(App) , document.getElementById('app'))

