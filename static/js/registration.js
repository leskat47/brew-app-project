$(document).ready(function () {
	$(function()
	{
		$("#register").validate(
			{
			rules: {
				fname:
				{
					required: true
				},
				lname:
				{
					required: true
				},
				email:
				{
					required: true,
					email: true
				},
				username:
				{
					required: true,
					minlength: 2
				},
				password:
				{
					required: true,
					minlength: 5
				}
			},
			messages: {
				lname:
				{
					required: "Please enter your first name"
				},
				fname:
				{
					required: "Please enter your last name"
				},
				email:
				{
					required: "Please enter your email",
					email: "Your email must be in the format of name@example.com"
				},
				username:
				{
					required: "Please select a username",
					minlength: "At least 2 characters required!"
				},
				password:
				{
					required: "Please select a password",
					minlength: jQuery.format("Password must be at least 5 characters long.")
				}
			}
		});
	});
	
	$("#register").validate();

});
