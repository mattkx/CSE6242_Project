alert("This chart will display the order to reallocate bicycles for Citibike based upon multiple criteria. \
  Wind Speed, Precipitation, Snow, and Temperature expect float values.")
// enter code to define margin and dimensions for svg
var svgWidth = 960;
var svgHeight = 1160;
var margin = 24;

// enter code to create svg
var svg = d3.select("#choropleth").append("svg")
.attr("id", "svg")
.attr("width", svgWidth+2*margin)
.attr("height", svgHeight+2*margin);

//define "globals"
var projection = d3.geoMercator()
.scale(100*svgWidth)
.translate([.4*svgWidth , .40*svgHeight ])

var baseServerURL = 'http://127.0.0.1:5000/demand'


//define a tool tip too
nodeTip = d3.tip().attr("id","tooltip")
.html(function(d, pos) {
  //will need to add handling for lookup from list of stations for actual name
    var stationID = d.station_id;
    var stationName = d.station_name

    return "<p><b>" + "Station ID: " + "</b>" + stationID + "</p>" +
    "<p><b>" + "Station Name: " + "</b>" + stationName + "</p>" +
    "<p><b>" + "Reallocation Order: " + "</b>" + String(pos) + "</p>"
})

lineTip = d3.tip().attr("id","tooltip")
.html(function(source, target, pos) {
  //will need to add handling for lookup from list of stations for actual name
    let sourceName = source.station_name;
    let targetName = target.station_name;

    return "<p><b>" + "Source Station: " + "</b>" + sourceName + "</p>" +
    "<p><b>" + "Target Station: " + "</b>" + targetName + "</p>" +
    "<p><b>" + "Reallocation Position: " + "</b>" + String(pos) + "</p>"
})

Promise.all([
    // enter code to read files
    d3.json("boros2.geojson") 
  ]).then(
      // enter code to call ready() with required arguments
      function(data)
      {
          NYC_MapInfo = data[0]
          stations= [
  {
  "station_id": 2017,
  "station_name": "E 43 St & 2 Ave",
  "station_latitude": 40.75022392,
  "station_longitude": -73.97121414
  },
  {
  "station_id": 351,
  "station_name": "Front St & Maiden Ln",
  "station_latitude": 40.70530954,
  "station_longitude": -74.00612572
  },
  {
  "station_id": 259,
  "station_name": "South St & Whitehall St",
  "station_latitude": 40.70122128,
  "station_longitude": -74.01234218
  },
  {
  "station_id": 2001,
  "station_name": "7 Ave & Farragut St",
  "station_latitude": 40.69892054,
  "station_longitude": -73.97332996
  },
  {
  "station_id": 423,
  "station_name": "W 54 St & 9 Ave",
  "station_latitude": 40.76584941,
  "station_longitude": -73.98690506
  },
  {
  "station_id": 247,
  "station_name": "Perry St & Bleecker St",
  "station_latitude": 40.73535398,
  "station_longitude": -74.00483091
  },
  {
  "station_id": 297,
  "station_name": "E 15 St & 3 Ave",
  "station_latitude": 40.734232,
  "station_longitude": -73.986923
  },
  {
  "station_id": 2004,
  "station_name": "6 Ave & Broome St",
  "station_latitude": 40.724399,
  "station_longitude": -74.004704
  },
  {
  "station_id": 345,
  "station_name": "W 13 St & 6 Ave",
  "station_latitude": 40.73649403,
  "station_longitude": -73.99704374
  },
  {
  "station_id": 376,
  "station_name": "John St & William St",
  "station_latitude": 40.70862144,
  "station_longitude": -74.00722156
  }
  ]
          
          ready(null, NYC_MapInfo, stations);
      }
  ).catch(function (error) {
  console.log(error);
  });

//call ready on map load
function ready(error, NYC_MapInfo, stations) {
    
    var center = d3.geoCentroid(NYC_MapInfo);
    projection.center(center);

    var path = d3.geoPath().projection(projection);

    //make the map of the 4 main boros
    map = svg.append("g")
    .attr("id", "boros")
    .selectAll("path")
    .data(NYC_MapInfo.features)
    .enter()
    .append("path")
    .attr("id", function(d) {
        return d.properties.boro_name;
    })
    .attr("fill", function(d) {
        return '#abdbe3'
    })
    .attr("d",path)
    
    //loop this on input

    

    
}

// this function should create a Choropleth and legend using the world and gameData arguments for a selectedGame
// also use this function to update Choropleth and legend when a different game is selected from the dropdown
function writeNewAllocationMap(stations, svg, projection)
{
  //delete nodes and lines for current station groupings
  d3.selectAll("#stations").remove()
  d3.selectAll('#lines').remove()

  //add on the circles for the top ten stations
  svg.append("g")
  .attr("id", "stations")
  .selectAll("stations")
  .data(stations)
  .enter()
  .append("circle")
      .attr("id", function(d) {return String(d.station_id)})
      .attr("cx", function(d){ return projection([d.station_longitude, d.station_latitude])[0] })
      .attr("cy", function(d){ return projection([d.station_longitude, d.station_latitude])[1] })
      .attr("r", 5)
      .on('mouseover', function(d,i) {
        nodeTip.show(d, i)
      })
      .on('mouseout', nodeTip.hide)
      .style("fill", "69b3a2")
      .attr("stroke-width", 3)
      .attr("fill-opacity", 1)

  //add on the lines
  let lines = svg.append('g').attr('id', "lines")
  for (let j = 1; j < stations.length; j++)
  {
    let sourceCircle = document.getElementById(String(stations[j-1]['station_id']))
    let sourceCircleBox = sourceCircle.getBBox();
    let xCoordSource = sourceCircleBox.x + sourceCircleBox.width / 2
    let yCoordSource = sourceCircleBox.y + sourceCircleBox.height / 2
    let destinationCircleBox =document.getElementById(String(stations[j]['station_id'])).getBBox();
    let xCoordDst = destinationCircleBox.x + destinationCircleBox.width / 2
    let yCoordDst = destinationCircleBox.y + destinationCircleBox.height / 2
    var link = d3.linkHorizontal()({
      source: [xCoordSource,yCoordSource],
      target: [xCoordDst,yCoordDst]
    })
    lines.append('path')
    .attr('d', link)
    .attr('stroke', 'black')
    .attr('fill', 'none')
    .on('mouseover', function(d) {
      lineTip.show(stations[j-1], stations[j], j)
    })
    .on('mouseout', lineTip.hide)
  }

  svg.call(nodeTip)
  svg.call(lineTip)
}

function validateAndSubmit(data) {
  const formData = new FormData(data)
  let newURL =baseServerURL + "?"
  console.log(formData.entries())
  
  for (var pair of formData.entries()) {
    if (pair[0] === ('avgWind') || pair[0] === ('precipitation') || pair[0] === ('snow') || pair[0] === ('temp'))
    {
      if (isNaN(parseFloat(pair[1])))
      {
        alert("ERROR: Non-float value found for field " + pair[0])
        return false;
      }
    }
    newURL = newURL + String(pair[0]) + "=" + String(pair[1]) + "&"
  }
  newURL = newURL.substring(0,newURL.length-1)

  console.log(newURL)

  stations = fetchAsync(newURL)
  console.log(stations)

  //writeNewAllocationMap(stations, svg, projection)

  

}

async function fetchAsync (url) {
  fetch(url).then(data=>{return data.json()})
  .then(res=>{console.log(res)})
  .catch(error=>console.log(error))
}