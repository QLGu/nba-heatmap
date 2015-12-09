
function initializeData() {
    $.ajax({
        url: "/nba/games",
        method: "GET",
        data: {movement: "true"},
        dataType: "JSON",
        global: false,
        async: true,
        success: function(games) {
            console.log("got games")
            getPlayers(updateGames(games))
        }
    });
}

function getPlayers(game_id) {
    $.ajax({
        url: "/nba/games",
        method: "GET",
        data: {
            game_id: game_id,
        },
        global: false,
        async: false,
        success: function(object) {
            console.log("got players")
            home_team_id = object[game_id]['home_team_id']
            away_team_id = object[game_id]['away_team_id']
            console.log(object)
            $('#home-team').find('img').attr('src', getLogo(home_team_id))
            $('#away-team').find('img').attr('src', getLogo(away_team_id))
            $('#game-date').html(object[game_id]['game_date'])
            $('#home-team-score').html(object[game_id]['home_team_score'])
            $('#away-team-score').html(object[game_id]['away_team_score'])
            $('#home-team-name').html(object['home_team']['name'])
            $('#away-team-name').html(object['away_team']['name'])

            updatePlayers(object, game_id)
        }
    });
}

function getCoordinates(game_id, player_id) {
    startLoading()
    $.get('/nba/movement', {game_id: game_id, player_id: player_id}, function(coords) {
        stopLoading(coords)
    });
    //
    //$.ajax({
    //    url: "/nba/movement",
    //    method: "GET",
    //    data: {
    //        game_id: game_id,
    //        player_id: player_id
    //    },
    //    global: false,
    //    async: true,
    //    success: function(coords) {
    //        console.log("got coords");
    //        updateHeatmap(coords['locations']);
    //        $('#loading').fadeOut(1000, function() {
    //            updateHeatmap(coords['locations']);
    //        })
    //    }
    //})
}

function updateGames(games) {
    $.each(games, function(k, v) {
        $('#games-selector').append($('<option>', {
            value: k,
            text: v['game_name']
        }));
    })
    return $('#games-selector').val()
}

function getLogo(team_id) {
    return '/static/assets/logos/' + team_id + '.svg'
}

function updatePlayers(players, game_id) {

    $('.player-selector').empty()

    $('#other_players_selector').append($('<option>', {
        value: -1,
        text: "Ball"
    }));

    $(players['home_team']['players']).each(function() {
        $('#home_players_selector').append($('<option>', {
            value: this['playerid'],
            text: this['firstname'] + " " + this['lastname'] + " (" + this['jersey'] + ")"
        }));
    })

    $(players['away_team']['players']).each(function() {
        $('#away_players_selector').append($('<option>', {
            value: this['playerid'],
            text: this['firstname'] + " " + this['lastname'] + " (" + this['jersey'] + ")"
        }));
    })

    $.get('/nba/players', {game_id: game_id}, function(active_players) {
        $('#object-selector option').each(function() {
            if (active_players['active_players'].indexOf($(this).val()) == -1 ) {
                console.log(this)
                $(this).attr('disabled','disabled');
            }
        })
    });

    $("select").select2();

    return $('#object-selector').val()

}

function startLoading() {
    pauseHeatmap()

      $("select").prop("disabled", true);

    $('#loading').fadeIn(500, function() {

    })
            $('.heatmap-canvas').animate(500, {'opacity':0}, function(){
            clearHeatmap()
            })

}

function stopLoading(location_data) {

    updateHeatmap(location_data['locations']);
    $('#loading').fadeOut(500, function() {
        $('.heatmap-canvas').animate(500, {'opacity':1})
              $("select").prop("disabled", false);
    })
}


function updateHeatmap(data) {
    updateBackgroundImage(home_team_id)
    current = 0
    full_data = standardizeCoords(data)
    current_data = full_data
    nba_heatmap.setData({
        max: 5,
        min: 0,
        data: current_data
    });
}

function getCurrentGame() {
    return $('#games-selector').val()
}

function getCurrentPlayer() {
    return $('#object-selector').val()
}

function updateBackgroundImage(team_id) {
    background_image = "url(/static/assets/logos/"+team_id+".svg),url(/static/assets/backgrounds/fullcourt.svg),url(/static/assets/backgrounds/wood.jpg)"
    $('#heatmapContainer').css("background-image", background_image)
}

function changeHeatmapRange(range) {
    pauseHeatmap()
    current  = 0
    data_length = full_data.length
    min_range = timeToIndex(range[0], data_length)
    max_range = timeToIndex(range[1], data_length)
    current_data = full_data.slice(min_range, max_range)

    nba_heatmap.setData({
        max: 5,
        min: 0,
        data: current_data
    });

}

function clearHeatmap() {
    pauseHeatmap()
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
            game_clock: coords[i]['g'],
            value: 0.35
        }
    }
    return coords_stand
}

function timeToIndex(time, data_length) {
    return parseInt(data_length * (time / 60))
}

function indexToTime(index) {
    return parseInt(current * 60 / coords.length)
}

function animateHeatmap() {

    end = current_data.length
    
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
			$('#game-clock').html(current_data[current]['game_clock'])
			nba_heatmap.addData(current_data.slice(current - diff, current));
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


$(document).ready(function() {
    court_width = 94;
    court_height = 50;
    heatmapContainer = $('#heatmapContainer');
    heatmap_width = heatmapContainer.width();
    heatmap_height = heatmapContainer.height();
    nba_heatmap = h337.create({
        container: document.getElementById('heatmapContainer'),
        maxOpacity: .65,
        radius: 8,
        blur: 0.5
    });

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

    $("select").select2();

    initializeData();


    handlesSlider.noUiSlider.on('change', function(values, handle) {
        heatmap_range = [values[0], values[1]];
        changeHeatmapRange(heatmap_range);
    });

    $('#games-selector').change(function() {
        getPlayers(getCurrentGame())
    });

    //$('#object-selector').change(function() {
	 //  getCoordinates(getCurrentGame(),getCurrentPlayer())
    //});

    $('.fa-refresh').click(function() {
        getCoordinates(getCurrentGame(),getCurrentPlayer())
    })

    $('#play').click(function() {
        pauseHeatmap()
        animateHeatmap()
    });

    $('#pause').click(function() {
        pauseHeatmap();
    });

})

