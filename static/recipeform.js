$(document).ready(function () {
    "use strict";

//  *********************************************
//  Ingredient add/delete-a-row functions 

$("#hidden").hide();

// $('.del-grain').prop('disabled', true);
$('#moregrains1').hide();
$("#add-grain").click(function() {
	var num = $(".repeat-grain").length;
	var newNum = num + 1;
	if (num > 0) {
		$('.del-grain').prop('disabled', false);	
	}	
	var newElement = $("#moregrains1").clone(true).attr('id', 'moregrains' + newNum).show();
	$("#add-grain").before(newElement);
});

$('.del-grain').click(function () {
    $(this).parent('div').remove(); 
    if ($('.repeat-grain').length === 2) {
    	$('.del-grain').prop('disabled', true);
	} 
    });

// $('.del-extract').prop('disabled', true);
$("#moreextract1").hide();
$("#add-extract").click(function() {
	var num = $(".repeat-extract").length;
	var newNum = num + 1;
	if (num > 0) {
		$('.del-extract').prop('disabled', false);	
	}
	var newElement = $("#moreextract1").clone(true).attr('id', 'moreextract' + newNum).show();
	$("#add-extract").before(newElement);
});

$('.del-extract').click(function () {
    $(this).parent('div').remove();  
    if ($('.repeat-extract').length === 2) {
    	// $('.del-extract').prop('disabled', true);
	} 
    });

// $('.del-hop').prop('disabled', true);
$("#morehops1").hide();
$("#add-hop").click(function() {
	var num = $(".repeat-hops").length;
	var newNum = num + 1;
	if (num > 0) {
		$('.del-hop').prop('disabled', false);	
	}
	var newElement = $("#morehops1").clone(true).attr('id', 'morehops' + newNum).show();
	$("#add-hop").before(newElement);
});
$('.del-hop').click(function () {
    $(this).parent('div').remove();  
    if ($('.repeat-hops').length === 2) {
    	$('.del-hop').prop('disabled', true);
	} 
    });

$("#moremisc1").hide();
$("#add-misc").click(function() {
	var num = $(".repeat-misc").length;
	var newNum = num + 1;
	if (num > 0) {
		$('.del-misc').prop('disabled', false);	
	}
	var newElement = $("#moremisc1").clone(true).attr('id', 'moremisc' + newNum).show();
	$("#add-misc").before(newElement);
});
$('.del-misc').click(function () {
    $(this).parent('div').remove();  
    });

$("#moreyeast1").hide();
$("#add-yeast").click(function() {
	var num = $(".repeat-yeast").length;
	var newNum = num + 1;
	if (num > 0) {
		$('.del-yeast').prop('disabled', false);	
	}
	var newElement = $("#moreyeast1").clone(true).attr('id', 'moreyeast' + newNum).show();
	$("#add-yeast").before(newElement);
});
$('.del-yeast').click(function () {
    $(this).parent('div').remove();  
    if ($('.repeat-yeast').length === 2) {
    	$('.del-yeast').prop('disabled', true);
	} 
    });


// ***********************************************
// Get current color for recipe

$("#colorcalc").click(function () {
	var ing = {}
	ing.batch_size = ($("form #batch_size").val());
	ing.units = ($("form #units").val());
	ing.grains = $('form .repeat-grain :input').serializeArray();
	ing.extracts = $('form .repeat-extract :input').serializeArray();

	$.ajax({url: "/colorcalc",
	type: "POST",
	data: JSON.stringify(ing),
	contentType: "application/json; charset=utf-8",
	success: function(result){
		console.log(result)
		$("#color").css('background-color', result)
	}
});
});


// ***********************************************
// Check recipe name for database and deny duplicates

$("#name").change(function () {
	checkName();
});

function checkName (){
	$.post("/check_recipe_name",
	"name=" + $("#name").val(),
	function(result) { 
		if (result === "nope") {
		$("#nameWarning").text('Sorry that recipe name is taken, please try a different name.');
		$("#name").val('');
		} else {
		$("#nameWarning").empty()
		}
	});
}


//  *********************************************
//  Create objects to convert to JSON

var postparams = {}

$("#submit").click(function (event){	

	postparams.name = ($("#name").val());
	postparams.source = ($("#source").val());
	postparams.style = ($("#style").val());
	postparams.share = ($("#share").val());
	postparams.batch_size = ($("#batch_size").val());
	postparams.units = ($("#units").val());
	postparams.notes = ($("#notes").val());
	postparams.grains = $('form .repeat-grain :input').serializeArray();
	postparams.hops = $('form .repeat-hops :input').serializeArray();
	postparams.extracts = $('form .repeat-extract :input').serializeArray();
	postparams.miscs = $('form .repeat-special :input').serializeArray();
	postparams.yeasts = $('form .repeat-yeast :input').serializeArray();

	console.log(postparams);

//  *********************************************
//  Send data to server
	$.ajax({url: "/addrecipe", 
		type: "POST",
		data:JSON.stringify(postparams),
		contentType: "application/json; charset=utf-8",
		success: function(result){
			console.log(result)
			alert("Recipe added!")
			var url = "/recipe/" + postparams.name;
			$(location).attr('href',url);
		}
	});
});
});




