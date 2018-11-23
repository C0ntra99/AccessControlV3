
$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('https://' + document.domain + ':' + location.port + '/doorcontrol');

    //receive details from server
    socket.on('doorchange', function(msg) {
		my_string = ''
		if (msg.is_open){
			my_string = my_string + '<p class="door-info">Door is open.</p>';
		} else {
			my_string = my_string + '<p class="door-info">Door is closed.</p>';
		}
		if (msg.is_locked){
			my_string = my_string + '<p class="door-info">Door is locked.</p>';
		} else {
			my_string = my_string + '<p class="door-info">Door is unlocked.</p>';
		}
		if (msg.is_blocked){
			my_string = my_string + '<p class="door-info">Door is blocked.</p>';
		} else {
			my_string = my_string + '<p class="door-info">Door is not blocked.</p>';
		}
        $('#door-log').html(my_string);
    });

});