import DOM from 'react-dom-factories'
import * as d3 from 'd3'
import * as hlp from './chart/dataHelpers.coffee'

L = DOM
log = console.log

_get_svg = ()->
    box = svg.node().getBBox()
    log box
    svg:svg,bbox:box
_prepare=(svg)->
    margin = {top: 0, right: 20, bottom: 30, left: 42}
    g = svg.append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
    g
_data_mode_map =  (data)->
    console.log('dd')
    data
_mode = 'normal'
export change_mode = (mode)->
    if mode=='cumulative'
        _data_mode_map = (data)->
            console.log('cumcum')
            cum  =0
            data__ = []
            for d in data
                cum+=d.value
                data__.push {index:d.index,value:cum}
            data__
    else
        _data_mode_map = (data)->
            data
    m = d3.select('#mode-text')
    m.html('mode: '+mode)

export start=({data})->
    svg = d3.select('svg#chart-vis')
    div = d3.select('div#chart').append('div')
        .attr 'id','mode'
    
    text = div.append('div').attr 'id','mode-text'
        .html 'mode: '+_mode
    g = _prepare(svg)
    bbox = svg.node().getBoundingClientRect()
    g.append("path")
    g.append("g").attr('id','axis-y')
    div.append('div')
        .attr 'id','mode-switch'
        .on('click',(e)->
            console.log(_mode)
            if _mode=='cumulative'
                _mode = 'normal'
            else
                _mode = 'cumulative'
            change_mode(_mode)
            update(data:data)
        )
        .html('switch mode')

    g.append("linearGradient")
        .attr('id', 'area-gradient')
    g.append("path")
        .attr('id', 'area-path')

    _update(data:data,width:bbox.width,height:bbox.height)

export update=({data})->
    svg = d3.select('svg#chart-vis')
    bbox = svg.node().getBoundingClientRect()
    _update(data:data,width:bbox.width,height:bbox.height)

_update=({data,width,height})->
    log width,height,data
    GRAPH_ID ='chart-vis'
    g = d3.select('svg#'+GRAPH_ID).select('g')
    svg = d3.select('svg#'+GRAPH_ID)

    x = d3.scaleLinear().range([6, width+(width)/(data.length-1)-40])
    y = d3.scaleLinear().range([height-8, 8])

    data = _data_mode_map(data)
    # this hides path between last 2 points, for smooth animation
    e = data.slice().pop()
    data = data.slice()
    data.push({index:e.index+1,value:e.value})
    data.push({index:e.index+2,value:0})
    #svg.attr("transform", "translate(" + ()+ ",0)")
    x.domain( d3.extent(data,(d) -> d.index ))
    y.domain([0, d3.max(data, (d) -> d.value )])

    # define the area
    area = d3.area()
        .x (d) -> x(d.index)
        .y0(height)
        .curve d3.curveNatural
        .y1 (d) -> y(d.value)
    line = d3.line()
        .curve d3.curveNatural
        .x (d) -> x(d.index)
        .y (d) -> y(d.value)
    # set the gradient

    # Line Path, that is on top
    # ---------------------------
    svg.select("path#area-path")
        .data([data])
        .attr("class", "area")
    g.select("path")
        .data([data])
        .attr("class", "line")
        .transition()
            .duration(200)
            .ease(d3.easeLinear)
        .attr("d", line)
        #.attr("d", area)
        .attr("stroke", "#1370c6")
        .attr("stroke-width", "2")
        .attr('fill','none')

    # Area Path, that is filled by gradient
    # ---------------------------
    svg.select("path#area-path")
        .data([data])
        .attr("class", "area")
        .transition()
            .duration(200)
            .ease(d3.easeLinear)
        .attr("d",area)
        .attr("stroke-width", "0")
        .attr('fill','url(#area-gradient)')


    # Gradient
    # ---------------------------
    svg.select('linearGradient')
        .attr('gradientUnits', 'userSpaceOnUse')
        .attr('x1', 0)
        .attr('y1', y(0))
        .attr('x2', 0)
        .attr('y2', y(d3.max(data, (d)->d.value)))
        .selectAll('stop')
        .data([
            { offset: '0%', color: '#b3e0dd11' },
            { offset: '100%', color: '#b3e0dd' },
        ]).enter().append('stop')
            .attr('offset', (d) -> d.offset)
        .attr 'stop-color', (d) -> d.color
    g.select("g#axis-y")
        .call(d3.axisLeft(y).ticks(5))

export Ui = ({w,h}) ->
    L.div
        id:'chart'
        L.svg
            id:'chart-vis'
            width:w
            height:h
            preserveAspectRatio='none'
