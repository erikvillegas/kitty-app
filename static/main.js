$(document).ready(function(){
    // fetch latest weights on page load and insert as placeholder values
    $.getJSON("/latest_weights", function(json) {
        window.localStorage.setItem('latest_weights', JSON.stringify(json));
        
        $('#red').attr('placeholder', json['red'])
        $('#orange').attr('placeholder', json['orange'])
        $('#yellow').attr('placeholder', json['yellow'])
        $('#green').attr('placeholder', json['green'])
        $('#blue').attr('placeholder', json['blue'])
        $('#purple').attr('placeholder', json['purple'])
    });

    // Returns a formatted weight string for a particular kitten (i.e. +823g)
    function gains(color) {
        weights = JSON.parse(window.localStorage.getItem('latest_weights'));
        newWeight = parseInt($('#' + color).val())
        if (!Number.isNaN(newWeight)) {
            var gain = parseInt(newWeight) - weights[color]
            var symbol = gain >= 0 ? '+' : ''
            return symbol + gain + 'g'
        }
        return ''
    }

    $("#red").blur(function() {
        $('#red-gain').text(gains('red'))
    });

    $("#orange").blur(function() {
        $('#orange-gain').text(gains('orange'))
    });

    $("#yellow").blur(function() {
        $('#yellow-gain').text(gains('yellow'))
    });

    $("#green").blur(function() {
        $('#green-gain').text(gains('green'))
    });

    $("#blue").blur(function() {
        $('#blue-gain').text(gains('blue'))
    });

    $("#purple").blur(function() {
        $('#purple-gain').text(gains('purple'))
    });
});

$(function() {
    // Submit weights to API on submit click
    $('a#submit').on('click', function(e) {
        e.preventDefault()
        $.ajax({
            url: "/weight_submit",
            type: "get",
            data: { 
                red: $('#red').val(),
                orange: $('#orange').val(),
                yellow: $('#yellow').val(),
                green: $('#green').val(),
                blue: $('#blue').val(),
                purple: $('#purple').val()
            },
            success: function(response) {
                window.location = response;
            }
        });
    });
});