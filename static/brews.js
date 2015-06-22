$(document).ready(function() {
  var alarmBell = new buzz.sound("/static/bells/alarmbell", {
	    formats: [ "mp3", "wav"]
  });
	var timeonclock = 0;
	$("#cal-reminder").hide();
	$("#g-days").hide();

	$("#steep_target").click(function(){
		$('.collapse').collapse();
	});

// *******************************************
// Save the boil start time


$('#boil_start').change(function(){
	boil_start = ($('#boil_start').val());

	$.post('/boil',
	{boil_start: boil_start, brew_id: brew_id},
	console.log("Boil time saved."));

});


$('.glyphicon').click(function(){
	$(this).toggle();
	$(this).siblings($('.glyphicon')).toggle();

})



// ********************************************
// timer functionality

// TIMER:
// timer box toggle and drag:
	$(".timer").click(function(evt){
		$(".timer").css("background-color", "#ffffff").text("Start a Timer");
		$(this).css("background-color", "#e5f4c0;").text("Timer Running");
		timer.start($(this).val() * 60000);
	});
	$("#showtimer").hide();
	$(".clos").click(function(){
		$(this).parent().toggle();
		$("#showtimer").show();

	$("#showtimer").click(function(){
		$("#popUpDiv").show();
		$("#showtimer").hide();
	})

	});
	$('#timergoodies').draggable({
		containment: '.brew',
    	stack: ".draggable"
	});

var timer = new Tock({
	  	countdown: true,
	  	interval: 10,
	  	callback: function(timer) {
		    var current_time = timer.msToTimecode(timer.lap());
		    $("#clock").val(current_time);
		},
	  	complete: function () {
		  	alarmBell.play();
		    alarm = confirm("Time's up!");
		    if (alarm == true) {
		    	alarmBell.stop();
		    } else if (alarm == false) {
		    	alarmBell.stop();
		    }
		}
	});

$(".stop").on('click', function() {
	timer.pause();
	});


// CALENDAR:
$("#rem-display").hide()
$("input[name=rem]:radio").change( function(){
	$("#get-inst").val('');
	$("#c-days").val('');

	$("#rem-display").show()
	if (this.value == "gravity") {
		$("#cal_title").text("Check beer gravity");
		$("#cal_desc").text("Check gravity for {{ recipe }}");
		$("#prompt").html('Gravity instructions: <input type="text" id="get-inst"><br>');
	}
	else if (this.value == "add-ing") {
		$("#cal_title").text("Add next brew ingredient");
		$("#cal_desc").text("Add next brew ingredient");
		$("#prompt").html('Ingredient reminder: <input type="text" id="get-inst"><br>');

	}
	else if (this.value == "temperature") {	
		$("#cal_title").text("Check beer temperature");
		$("#cal_desc").text("Check beer temperature");
		$("#prompt").html('Temperature instruction: <input type="text" id="get-inst"><br>');

	}
	else if (this.value == "reminder") {
		$("#cal_title").text("Beer reminder");
		$("#cal_desc").text("Beer reminder");
		$("#prompt").html('Other instructions: <input type="text" id="get-inst"><br>');
	}
});
$("#get-inst").change( function(){
	$("#cal_desc").text($("#get-inst").val());

});

$("#c-days").change( function(){
	console.log("change")
	var date = new Date();
	var days = parseInt($("#c-days").val());
	date.setDate(date.getDate() + days);

	year = date.getFullYear();
	month = date.getMonth() + 1;
	if (month < 10) {
		month = "0" + month;
	}
	day = date.getDate();
	if (day < 10) {
		day = "0" + day;
	}
	newdate = year + "-" + month + "-" + day + " 12:00:00";

	$("#date_start").text(newdate);
	$("#date_end").text(newdate);
	$("#g-days").show();

	(function () {
			if (window.addtocalendar)if(typeof window.addtocalendar.start == "function")return;
            if (window.ifaddtocalendar == undefined) { window.ifaddtocalendar = 1;
                var d = document, s = d.createElement('script'), g = 'getElementsByTagName';
                s.type = 'text/javascript';s.charset = 'UTF-8';s.async = true;
                s.src = ('https:' == window.location.protocol ? 'https' : 'http')+'://addtocalendar.com/atc/1.5/atc.min.js';
                var h = d[g]('body')[0];h.appendChild(s); }})();

});

// ABV:
$("#final_gravity").change( function(){
	var fg = parseFloat($("#final_gravity").val());
	if ($("#orig_gravity").val() > 0) {
		var og = parseFloat($("#orig_gravity").val());
		var abv  = round(((og - fg) * 131), 2);
		$("#abv").text(abv);
		$("#abv").html(abv);
	}
});

});


