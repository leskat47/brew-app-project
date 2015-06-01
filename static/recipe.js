$(document).ready(function() {

$("#style").change(function(){
	this.form.submit();
})

$("#recipe").change(function(){
	this.form.submit();
})

$("#makerecipe").click(function (){
	name = $("#makerecipe").attr("name");
	checkBrew(name);
});

function checkBrew (name){
	$.post("/check_brew",
	"name=" + name,
	function(result) { 
		var loadBrew = false
		if (result === "duplicate") {
			loadBrew = confirm("You already have a brew for this recipe today. Start another?");
			if (loadBrew == true) {
				// var url = "/addbrew/" + name;    
				// $(location).attr('href',url);
			} else {
				console.log("Stay on this page.");
			}
		// } else {
		// 	var url = "/addbrew/" + name;    
		// 		$(location).attr('href',url);
		}
		}
	)
}

});