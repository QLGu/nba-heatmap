function getGames() {
    var games = $.ajax({
        url: "get_games.php",
        dataType: "JSON",
        global: false,
        async: false,
        success: function(json) {
            return json
        }
    }).responseJSON;

    return games
}

function getPlayers(home_team, away_team) {
    var players = $.ajax({
        url: "get_players.php",
        method: "POST",
        data: {
            away_team_id: away_team,
            home_team_id: home_team
        },
        dataType: "JSON",
        global: false,
        async: false,
        success: function(json) {
            return json
        }
    }).responseJSON;

    return players;

}

function getCoordinates(game, player) {
    var coords = $.ajax({
        url: "get_coordinates.php",
        method: "POST",
        data: {
            game_id: game,
            player_id: player
        },
        dataType: "JSON",
        global: false,
        async: false,
        success: function(json) {
            return json
        }
    }).responseJSON;

    return coords;

}



function updateGames(games) {
    $.each(games, function(k, v) {
        $('.games-list').append($('<li>', {
            value: k,
            text: v[0]
        }));
        $('#games-selector').append($('<option>', {
            value: k,
            text: v[0]
        }));
    })
}


function updatePlayers(players) {


    $('.player-selector').empty()

    $('#other_players_selector').append($('<option>', {
        value: -1,
        text: "Ball"
    }));

    $(players['home_players']).each(function() {
        $('#home_players_selector').append($('<option>', {
            value: this['player_id'],
            text: this['player_name']
        }));
    })

    $(players['away_players']).each(function() {
        $('#away_players_selector').append($('<option>', {
            value: this['player_id'],
            text: this['player_name']
        }));
    })

}

function updateHeatmap(coords) {
    pauseHeatmap()
    
    current_coords = coords.slice(current_index[0], current_index[1])
    current_coords_stand = standardizeCoords(current_coords)
    
    current = 0
    
    nba_heatmap.setData({
        max: 5,
        min: 0,
        data: current_coords_stand
    });
}

function clearHeatmap() {
	nba_heatmap.setData({
        max: 5,
        min: 0,
        data: []
    });
}

function standardizeCoords(coords) {
    coords_stand = []
    for (i = 0; i < coords.length; i++) {
        coords_stand[i] = {
            x: (parseFloat(coords[i]['x'] / 94) * heatmap_width),
            y: (parseFloat(coords[i]['y'] / 50) * heatmap_height),
            game_clock: coords[i]['game_clock'],
            value: 0.35
        }
    }
    return coords_stand
}

function timeToIndex(time) {
    return parseInt(coords.length * (time / 60))
}

function indexToTime(index) {
    return parseInt(current * 60 / coords.length)
}


function animateHeatmap(animate_coords) {

    
    end = animate_coords.length
    
    if(current == 0) {
	    clearHeatmap()
    }
    
    add_points_to_map = setInterval(function() {
		
		diff = 30
		
		if ((current + diff) < end) {
        	current += diff
		} else {
			var pause = true
			diff = (end - current - 1)
			current += diff
		}
		
 		try {
			$('#game-clock').html(animate_coords[current]['game_clock'])
			nba_heatmap.addData(animate_coords.slice(current - diff, current));
		} catch(err) {
			pauseHeatmap()
			console.log(err)
			console.log("error location 1")
		}
		

        if (pause) {
            pauseHeatmap()
        }


    }, 20);

}

function pauseHeatmap() {
    try {
        clearInterval(add_points_to_map)

    } catch (err) {
	    console.log(err)
    }
}




window.onload = function() {

    court_width = 94
    court_height = 50

    heatmap_width = $('#heatmapContainer').width()
    heatmap_height = $('#heatmapContainer').height()


    games = getGames()
    game_id = Object.keys(games)[0]
    players = getPlayers(games[game_id][1], games[game_id][2])
    player_id = -1

    coords = getCoordinates(game_id, player_id)
    coords_stand = standardizeCoords(coords)

    current_coords = coords
    current_coords_stand = standardizeCoords(current_coords)

    current = 0

    nba_heatmap = h337.create({
        container: document.getElementById('heatmapContainer'),
        maxOpacity: .65,
        radius: 8,
        blur: 0.5,
    });


    heatmapContainer = document.getElementById('heatmapContainerWrapper');

    var handlesSlider = document.getElementById('slider-handles');

    noUiSlider.create(handlesSlider, {
        start: [0, 60],
        range: {
            min: 0,
            max: 60
        },
        margin: 3,
        pips: {
            mode: 'values',
            values: [0, 15, 30, 45, 60],
            density: 1,
            stepped: true
        }
    });

    slider_val = handlesSlider.noUiSlider.get()
    current_index = [timeToIndex(slider_val[0]), timeToIndex(slider_val[1])]
    
    updateGames(games)
    updatePlayers(players)
    updateHeatmap(coords)

    handlesSlider.noUiSlider.on('change', function(values, handle) {
        current_index = [timeToIndex(values[0]), timeToIndex(values[
            1])]
        updateHeatmap(coords)
    })
	
	
	
	
	$('#games-selector').change(function() {
	    game_id = $(this).val()
	    home_team = games[game_id][1]
	    away_team = games[game_id][2]
	
	    players = getPlayers(home_team, away_team)
	    player_id = -1
	
		background_image = "url(logos/"+home_team+".svg),url(fullcourt.svg),url(wood_floor_by_gnrbishop.jpg)"
	
		$('#heatmapContainer').css("background-image", background_image)
	
	    coords = getCoordinates(game_id, -1)
	
	    updatePlayers(players)
	    updateHeatmap(coords)
	
	});
	
	$('#object-selector').change(function() {
	    player_id = $(this).val()
	    coords = getCoordinates(game_id, player_id)
	
	    updateHeatmap(coords)
	});
	

    $('#play').click(function() {
	    console.log(current)
        pauseHeatmap()
        animate_coords = current_coords_stand.slice(current_index)
        animateHeatmap(animate_coords)
    })

    $('#pause').click(function() {
        pauseHeatmap()
    })


}