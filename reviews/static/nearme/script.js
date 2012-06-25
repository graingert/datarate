var earth_r = 6371.0; //Earth's radius

function rad2deg (angle) {
	// Converts the radian number to the equivalent number in degrees  
	// 
    // version: 1109.2015
    // discuss at: http://phpjs.org/functions/rad2deg    // +   original by: Enrique Gonzalez
    // +      improved by: Brett Zamir (http://brett-zamir.me)
    // *     example 1: rad2deg(3.141592653589793);
    // *     returns 1: 180
    return angle * 57.29577951308232; // angle / Math.PI * 180}
}

function deg2rad (angle) {
    // Converts the number in degrees to the radian equivalent  
    // 
    // version: 1109.2015
    // discuss at: http://phpjs.org/functions/deg2rad    // +   original by: Enrique Gonzalez
    // +     improved by: Thomas Grainger (http://graingert.co.uk)
    // *     example 1: deg2rad(45);
    // *     returns 1: 0.7853981633974483
    return angle * 0.017453292519943295; // (angle / 180) * Math.PI;
}

function distance(location1, location2){
	var l1 = location1
	var l2 = location2
	return Math.acos(Math.sin(deg2rad(l1.lat))*Math.sin(deg2rad(l2.lat)) + Math.cos(deg2rad(l1.lat))*Math.cos(deg2rad(l2.lat))*Math.cos(deg2rad(l2.lng-l1.lng)))*earth_r
}

$(function(){
	
	var sparqlThingsNearme = Handlebars.compile($("#sparql-things-nearme").html())
	var thingsNearme = Handlebars.compile($("#things-nearme-tmpl").html())
	
	var sparqler = new SPARQL.Service("http://sparql.data.southampton.ac.uk/");
	
	sparqler.setPrefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
	sparqler.setPrefix("geo", "http://www.w3.org/2003/01/geo/wgs84_pos#")
	sparqler.setPrefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
	
	sparqler.setOutput("json")
	sparqler.setMethod("POST")
	
	
	
	if (navigator.geolocation) {
		console.log("geolocation supported")
		$("#geolocate").click(geolocate)
	} else {
		fallback("Geolocation is unsuported on this platform")
	}
	
	function fallback(reason){
		$("#geo").attr("hidden", "hidden")
		
		$("#nearme-settings").submit(function(e){
			var lat = parseFloat($(this).find("input[name=latitude]").val())
			var lng = parseFloat($(this).find("input[name=longitude]").val())
			var radius = parseFloat($(this).find("input[name=radius]").val())
			
			nearme(lat, lng, radius)
			return false
		})
		$("#nearme-settings input[type=submit]").removeAttr("disabled")
		
		
		$("#geofallback reason").html(reason)
		$("#geofallback").removeAttr("hidden")
	}
	
	function geolocate(e){
		navigator.geolocation.getCurrentPosition(
		function(position){
			nearme(position.coords.latitude, position.coords.longitude, 0.1)
		}, function (error){
			console.log(error)
			switch(error.code) 
			{
				case error.TIMEOUT:
					fallback('Geolocation Timed out');
					break;
				case error.POSITION_UNAVAILABLE:
					fallback ('your Position was unavailable');
					break;
				case error.PERMISSION_DENIED:
					fallback ('permission to the Geolocation API was denied');
					break;
				case error.UNKNOWN_ERROR:
				default:
					fallback ('something went wrong');
					break;
			}
		},
		
		{ enableHighAccuracy: true }
		)
	}
	
	function nearme(lat, lng, radius){
		// first-cut bounding box (in degrees)
		var maxLat = lat + rad2deg(radius/earth_r)
		var minLat = lat - rad2deg(radius/earth_r)
		// compensate for degrees longitude getting smaller with increasing latitude
		var maxLng = lng + rad2deg(radius/earth_r/Math.cos(deg2rad(lat)))
		var minLng = lng - rad2deg(radius/earth_r/Math.cos(deg2rad(lat)))
		
		var query = sparqler.createQuery()
		
		query.query(
			sparqlThingsNearme({minLng:minLng, maxLng:maxLng, minLat:minLat, maxLat:maxLat}),
			{
				failure: function(){
					console.log("fail")
				},
				success: function(json) {
					context = {
							lng: lng,
							lat: lat,
							things: []
					}
					
					var center = {lat:lat, lng:lng}
					for(var i=0; i<json.results.bindings.length; i++){
						var item = json.results.bindings[i]
						var prot = URI(item.s.value).protocol()
						if (prot == "http" || prot == "https" ){
						
							context.things.push(
								{
									uri : item.s.value,
									name : item.label.value,
									api_url: URI("/thing.html").search({uri : item.s.value}),
									distance: distance(center, {
										lat :item.lat.value,
										lng:item.long.value
									})
								}
							)
						}
					}
					context.things.sort(function(a,b){
						return (a.distance - b.distance)
					})
					$("#things-nearme").html(thingsNearme(context))
					$("#things-nearme").removeAttr("hidden")
				}
			}
		)
	}
})
