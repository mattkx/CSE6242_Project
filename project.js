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
    d3.json("boros.geojson"), 
    d3.csv("2014_stations.csv")
  ]).then(
      // enter code to call ready() with required arguments
      function(data)
      {
          NYC_MapInfo = data[0]
          stations_map= data[1]
          
          ready(null, NYC_MapInfo, stations_map);
      }
  ).catch(function (error) {
  console.log(error);
  });

//call ready on map load
function ready(error, NYC_MapInfo, stations_map) {
  //station_master_list = d3.nest().key(d => d.station_id).entries(stations_map)
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
function writeNewAllocationMap(stations, svg, projection, station_list)
{
  //delete nodes and lines for current station groupings
  d3.selectAll("#stations").remove()
  d3.selectAll('#lines').remove()

  filtered_station_list = station_list.filter(function(d) {
    for (let i = 0; i < stations.length; i++)
    {
      if (d.station_id == stations[i])
      {
        return true
      }
    }
    return false
  })

  //add on the circles for the top ten stations
  svg.append("g")
  .attr("id", "stations")
  .selectAll("stations")
  .data(filtered_station_list)
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
  for (let j = 1; j < filtered_station_list.length; j++)
  {
    let sourceCircle = document.getElementById(String(filtered_station_list[j-1]['station_id']))
    let sourceCircleBox = sourceCircle.getBBox();
    let xCoordSource = sourceCircleBox.x + sourceCircleBox.width / 2
    let yCoordSource = sourceCircleBox.y + sourceCircleBox.height / 2
    let destinationCircleBox =document.getElementById(String(filtered_station_list[j]['station_id'])).getBBox();
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
      lineTip.show(filtered_station_list[j-1], filtered_station_list[j], j)
    })
    .on('mouseout', lineTip.hide)
  }

  svg.call(nodeTip)
  svg.call(lineTip)
}

function validateAndSubmit(data) {
  const formData = new FormData(data)
  let newURL =baseServerURL + "?"
  
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

  //took a while to figure out async request
  fetchAsync(newURL).then(stations => {
    writeNewAllocationMap(stations['data'], svg, projection, stations_map)
  })
  

  

}

async function fetchAsync (url) {
  const resp = await fetch(url)
  const data = await resp.json()
  return data
}
