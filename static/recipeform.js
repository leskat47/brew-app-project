$(document).ready(function () {
    "use strict";

//  *********************************************
//  Ingredient add/delete-a-row functions 
//  *********************************************
// TODO: 

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
    	$('.del-extract').prop('disabled', true);
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
    console.log($('.repeat-hops').length); 
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


// $('.del-yeast').prop('disabled', true);
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

$("#name").change(function () {
	checkName();
});

function checkName (){
	$.post("/check_recipe_name",
	"name="+$("#name").val(),
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

	postparams.name = $("#name input").serialize();
	postparams.source = $("#source input").serialize();
	postparams.style = $("#style select").serialize();
	postparams.share = $("#share select").serialize();
	postparams.batch_size = $("#batch_size input").serialize();
	postparams.units = $("#units select").serialize();
	postparams.notes = $("#notes textarea").serialize();
	postparams.grains = $('.repeat-grain :input').serializeArray();
	postparams.hops = $('.repeat-hops :input').serializeArray();
	postparams.extracts = $('.repeat-extract :input').serializeArray();
	postparams.miscs = $('.repeat-special :input').serializeArray();
	postparams.yeasts = $('.repeat-yeast :input	').serializeArray();

	console.log(postparams);
	// TODO: find a way to sort ingredients so name is the key for each input

//  *********************************************
//  Send data to server
	$.ajax({url: "/addrecipe", 
		type: "POST",
		data:JSON.stringify(postparams),
		contentType: "application/json; charset=utf-8",});
});
});




