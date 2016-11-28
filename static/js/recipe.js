$(document).ready(function() {

$("#style").change(function(){
	this.form.submit();
})

$("#recipe").change(function(){
	this.form.submit();
})

$("#makerecipe").click(function(){
	name = $("#makerecipe").attr("name");
	console.log("clicked")
	checkBrew(name);
});


function checkBrew(name){
	$.post("/check_brew",
	"name=" + name,
	function(result) { 
		if (result === "duplicate") {
			var loadBrew = confirm("You already have a brew for this recipe today. Start another?");
			if (loadBrew == true) {
				console.log("Go to the next page")
				var url = "/addbrew/" + name;    
				$(location).attr('href',url);
			} else if (loadBrew == false) {
				console.log("Stay on this page.");
			}
		} else {
			console.log("Go to the next page")
			var url = "/addbrew/" + name;    
			console.log(url)
			$(location).attr('href',url);
		}

		}
	)
}

});