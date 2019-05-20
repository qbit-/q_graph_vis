import * as d3 from 'd3'
#Function to choose what color circle we have

#Function to choose the line colour and thickness 

#Drag functions 
#d is the node 

export drag_start = (simulation)->(d) ->
  if !d3.event.active
    simulation.alphaTarget(0.1).restart()
  d.fx = d.x
  d.fy = d.y
  return

#make sure you can't drag the circle outside the box

export drag_drag = (d) ->
  d.fx = d3.event.x
  d.fy = d3.event.y
  return

export drag_end = (simulation)->(d) ->
  if !d3.event.active
    simulation.alphaTarget 0.1
  #d.fx = null
  #d.fy = null
  return

#Zoom functions 

export zoom = (g)->() ->
  g.attr 'transform', d3.event.transform
  return

export tick = (node,link)->()->
  #update circle positions each tick of the simulation 
  node
   .attr("transform",(d) ->
       "translate(" + d.x + "," + d.y + ")"
       )
  #update link positions 
  link
      .attr 'x1', (d) -> d.source.x
      .attr 'y1', (d) -> d.source.y
      .attr 'x2', (d) -> d.target.x
      .attr 'y2', (d) -> d.target.y
  return
