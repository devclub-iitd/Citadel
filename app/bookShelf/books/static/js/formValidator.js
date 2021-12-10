
var start = 2005;
var end = new Date().getFullYear();
var options = "";
for(var year = end ; year >= start; year--){
  options += "<option value=\""+ year +"\" >"+ year +"</option>";
}
document.getElementById("year").innerHTML = options;

// var customFilename = document.getElementById("customFilename");
// customFilename.addEventListener("input", function() {
//     if (customFilename.validity.patternMismatch) {
//         customFilename.setCustomValidity("Only letters, numbers and spaces are allowed for this field");
// 		customFilename.parentNode.getElementsByClassName("invalid-feedback")[0].innerHTML = customFilename.validationMessage;
//     } else {
//         customFilename.setCustomValidity("");
//     }
// });

// Once form inputs are validated, continuously check when inputs are changed.
document.getElementById('upload-form').addEventListener("input", function(){
	if(document.getElementById('upload-form').classList.contains('was-validated')){
		var valid = isValid();
	}
	
	var customFilename = document.getElementById("customFilename");
	if (customFilename.validity.patternMismatch) {
        customFilename.setCustomValidity("Only letters, numbers and spaces are allowed for this field");
		customFilename.parentNode.getElementsByClassName("invalid-feedback")[0].innerHTML = customFilename.validationMessage;
    } else {
        customFilename.setCustomValidity("");
    }
});
document.getElementById('reorder-section').addEventListener("input", function(){
	if(document.getElementById('reorder-section').classList.contains('was-validated')){
		var valid = isValidOrder(getImageOrder());
	}
});
// document.getElementById("next-btn").addEventListener("mouseover", function() {
// 	console.log(isValid())
    
// });

function isValid(){
	var course_code = document.getElementById("code-input");
    var sem = document.getElementById("sem");
    var year = document.getElementById("year");
    var prof = document.getElementById("prof");
    var type = document.getElementById("type_file");
    var other_text = document.getElementById("customFilename");
    var file_dump = document.getElementById("file-dump");


    var valid=true;

	if(!(/^[a-zA-Z]{3}[0-9]{3}$/).test(course_code.value)){
		course_code.setCustomValidity("Please enter a valid course code");
		course_code.parentNode.getElementsByClassName("invalid-feedback")[0].innerHTML = course_code.validationMessage;
		valid=false;
	}
	else{
		course_code.setCustomValidity("");
	}

	if(type.value==''){
		type.setCustomValidity("Please choose a valid document type");
		type.parentNode.getElementsByClassName("invalid-feedback")[0].innerHTML = type.validationMessage;
		valid=false;
	}
	else{
		type.setCustomValidity("")
	}

	// reset the validity of these fields
	sem.setCustomValidity("");
	if(sem.hasAttribute('required')){
		sem.removeAttribute('required');
	}
	year.setCustomValidity("");
	if(year.hasAttribute('required')){
		sem.removeAttribute('required');
	}
	prof.setCustomValidity("");
	if(prof.hasAttribute('required')){
		prof.removeAttribute('required');
	}


	if(type.value=="Minor1" || type.value=="Minor2" || type =="Major"){
		var required=[sem,year]
	}

	else if(type.value=="Books" || type.value=="Others"){
		var required=[]
	}

	else{
		var required=[sem,year,prof]
	}


	for (var i = 0; i < required.length; i++) {
		required[i].setAttribute('required', '');
		if(required[i].value==''){
			required[i].setCustomValidity("Please enter a valid value");
			required[i].parentNode.getElementsByClassName("invalid-feedback")[0].innerHTML = required[i].validationMessage;
			valid=false;
		}
		else{
			required[i].setCustomValidity("")
		}
	}

	if(file_dump.files.length==0){
		file_dump.setCustomValidity("Please select one or more files to upload");
		file_dump.parentNode.getElementsByClassName("invalid-feedback")[0].innerHTML = file_dump.validationMessage;
		valid=false
	}
	else{
		file_dump.setCustomValidity("");
	}
	showValidation();
  	return valid
}

//function to check the validity of the page number order of the images selected by the user 
function isValidOrder(order){
	var valid = true;

	if(order.length==0){
		return valid;
	}

	for(var i=0; i<order.length-1; i++){
		if(order[i]<1 || order[i]>order.length){
			valid = false;
			break;
		}
		for(var j=i+1; j<order.length; j++){
			if(order[i]==order[j]){
				valid = false;
				break;
			}
		}
		if(!valid){
			break;
		}
	}

	var orderBox = [];

	for(var i=0; i<order.length; i++){
		orderBox[i] = document.getElementsByClassName('image-preview')[i].getElementsByTagName('select')[0];
		if(valid){
			orderBox[i].setCustomValidity("");
		}
		else{
			orderBox[i].setCustomValidity("Page numbering not unique.");
		}
	}

	var imageOrderInput = document.getElementById('image-order');
	
	if(valid){
		imageOrderInput.setCustomValidity("");
		if(imageOrderInput.parentNode.getElementsByClassName("invalid-feedback")[0].classList.contains("d-block"))
			imageOrderInput.parentNode.getElementsByClassName("invalid-feedback")[0].classList.remove("d-block");
	}
	else{
		imageOrderInput.setCustomValidity("Page numbering not unique. Please enter valid page numbers");
		//force display of invalid message since element is outside form.
		if(!imageOrderInput.parentNode.getElementsByClassName("invalid-feedback")[0].classList.contains("d-block"))
			imageOrderInput.parentNode.getElementsByClassName("invalid-feedback")[0].classList.add("d-block");
	}


	return valid;
}

function showValidation(){
	forms = document.getElementsByClassName('needs-validation');
	for(var i=0; i<forms.length; i++){
		if(!forms[i].classList.contains('was-validated')){
			forms[i].classList.add('was-validated');
		}
	}
}