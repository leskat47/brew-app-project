$(document).ready(function () {
    "use strict";


// $("#add-grain").click(function(){
// 	var containerClass = ".repeat-grain"
// 	var containerId = $(".repeat-grain").attr('id');
// 	addRow(containerId, containerClass)
// });

// function addRow(containerId, containerClass){
// 	var ingredientId = $(containerClass).children().attr("id");
// 	var ingredientName = $(containerClass).children(":first").name;
// 	var amountId = $(containerClass).children(":nth-child(2)").id;
// 	var amountName = $(containerClass).children(":nth-child(2)").name;
// 	var unitId = $(containerClass).children(":last-child").id;
// 	var unitName = $(containerClass).children(":last-child").name;

// 	var num = $(containerClass).length;
// 	var newNum = new Number(num + 1);
// 	var newElement = $(containerId + num).clone().attr('id', containerClass + newNum);
// 	newElement.children(":first").attr('id', ingredientId + newNum).attr('name', ingredientName + newNum);
// 	newElement.children(":nth-child(2)").attr('id', amountId + newNum).attr('name', amountName + newNum);
// 	newElement.children(":last-child").attr('id', unitId +  newNum).attr('name', unitName + newNum);
// 	$(containerId + num).after(newElement);
// }

$("#add-grain").click(function(){
	var num = $(".repeat-grain").length;
	var newNum = new Number(num + 1);
	var newElement = $("#moregrains" + num).clone().attr('id', 'moregrains' + newNum);
	newElement.children(":first").attr('id', 'grain' + newNum).attr('name', 'grain' + newNum);
	newElement.children(":nth-child(2)").attr('id', 'grain_amount' + newNum).attr('name', 'grain_amount' + newNum);
	newElement.children(":last-child").attr('id', 'grain_units' +  newNum).attr('name', 'grain_units' + newNum);
	$("#moregrains" + num).after(newElement);
});

$("#add-extract").click(function(){
	var num = $(".repeat-extract").length;
	var newNum = new Number(num + 1);
	var newElement = $("#moreextract" + num).clone().attr('id', 'moreextract' + newNum);
	console.log(newElement)
	newElement.children(":first").attr('id', 'extract' + newNum).attr('name', 'extract' + newNum);
	newElement.children(":nth-child(2)").attr('id', 'extract_amount' + newNum).attr('name', 'extract_amount' + newNum);
	newElement.children(":last-child").attr('id', 'extract_units' +  newNum).attr('name', 'extract_units' + newNum);
	$("#moreextract" + num).after(newElement);
});

$("#add-hop").click(function(){
	var num = $(".repeat-hops").length;
	var newNum = new Number(num + 1);
	var newElement = $("#morehops" + num).clone().attr('id', 'morehops' + newNum);
	newElement.children(":first").attr('id', 'hop' + newNum).attr('name', 'hop' + newNum);
	newElement.children(":nth-child(2)").attr('id', 'hop_amount' + newNum).attr('name', 'hop_amount' + newNum);
	newElement.children(":nth-child(3)").attr('id', 'hop_units' +  newNum).attr('name', 'hop_units' + newNum);
	newElement.children(":nth-child(4)").attr('id', 'hop_phase' + newNum).attr('name', 'hop_phase' + newNum);
	newElement.children(":nth-child(5)").attr('id', 'hop_time' + newNum).attr('name', 'hop_time' + newNum);
	newElement.children(":last-child").attr('id', 'hop_kind' + newNum).attr('name', 'hop_kind', + newNum);
	$("#morehops" + num).after(newElement);
});

$("#add-yeast").click(function(){
	var num = $(".repeat-yeast").length;
	var newNum = new Number(num + 1);
	var newElement = $("#moreyeast" + num).clone().attr('id', 'moreyeast' + newNum);
	newElement.children(":first").attr('id', 'yeast' + newNum).attr('name', 'yeast' + newNum);
	newElement.children(":nth-child(2)").attr('id', 'yeast_amount' + newNum).attr('name', 'yeast_amount' + newNum);
	newElement.children(":last-child").attr('id', 'yeast_units' +  newNum).attr('name', 'yeast_units' + newNum);
	$("#moreyeast" + num).after(newElement);
});

$("#add-misc").click(function(){
	var num = $(".repeat-special").length;
	var newNum = new Number(num + 1);
	var newElement = $("#morespecial" + num).clone().attr('id', 'morespecial' + newNum);
	newElement.children(":first").attr('id', 'misc' + newNum).attr('name', 'misc' + newNum);
	newElement.children(":nth-child(2)").attr('id', 'misc_amount' + newNum).attr('name', 'misc_amount' + newNum);
	newElement.children(":nth-child(3)").attr('id', 'misc_units' +  newNum).attr('name', 'misc_units' + newNum);
	newElement.children(":nth-child(4)").attr('id', 'misc_phase' + newNum).attr('name', 'misc_phase' + newNum);
	newElement.children(":last-child").attr('id', 'misc_time' + newNum).attr('name', 'misc_time' + newNum);
	$("#morespecial" + num).after(newElement);
});

// $("#submit").click(function(){
// 	var Data = $("ajaxform").serializeArray();
// 	console.log(Data);
// });
// var AddRecipeForm = $("#ajaxform").serializeJSON():
// console.log(MyForm);
// $.ajax(
// {
// 	url: "/addrecipe",
// 	type: "POST",
// 	data: {valArray: AddRecipeForm},
// 	success: function(maindta) {
// 		alert(maindta);
// 	}
// }

});