var graphConfig = {
      "automaticRearrangeAfterDropNode": true,
      "collapsible": false,
      "height": 400,
      "highlightDegree": 1,
      "highlightOpacity": 1,
      "linkHighlightBehavior":true,
      "maxZoom": 8,
      "minZoom": 0.1,
      "nodeHighlightBehavior":true,
      "panAndZoom": false,
      "staticGraph": false,
      "width": 800,
      "d3": {
              "alphaTarget": 0.05,
              "gravity": -400,
              "linkLength": 4,
              "linkStrength": 2
            },
      "node": {
              "color": "#d3d3d3",
              "fontColor": "black",
              "fontSize": 8,
              "fontWeight": "normal",
              "highlightColor": "#f55",
              "highlightFontSize": 8,
              "highlightFontWeight": "normal",
              "highlightStrokeColor": "SAME",
              "highlightStrokeWidth": 1.5,
              "labelProperty": "id",
              "mouseCursor": "pointer",
              "opacity": 1,
              "renderLabel": true,
              "size": 200,
              "strokeColor": "none",
              "strokeWidth": 1.5,
              "svg": "",
              "symbolType": "circle"
            },
      "link": {
              "color": "#d3d3d3",
              "highlightColor": "#faa",
              "opacity": 1,
              "semanticStrokeWidth": false,
              "strokeWidth": 1.5
            }
}
export default graphConfig 
