
var start = 2005;
var end = new Date().getFullYear();
var options = "";
for(var year = end ; year >= start; year--){
  options += "<option value=\""+ year +"\" >"+ year +"</option>";
}
document.getElementById("year").innerHTML = options;

document.getElementById("customFilename").addEventListener("input", function() {
    if (document.getElementById("customFilename").validity.typeMismatch) {
        document.getElementById("customFilename").setCustomValidity("Only letters, numbers and spaces are allowed for this field");
    } else {
        document.getElementById("customFilename").setCustomValidity("");
    }
});
// document.getElementById("next-btn").addEventListener("mouseover", function() {
// 	console.log(isValid())
    
// });

function isValid(){
	var course_code = document.getElementsByClassName("form-control")[0];
    var sem = document.getElementsByClassName("form-control")[1];
    var year = document.getElementsByClassName("form-control")[2];
    var prof = document.getElementsByClassName("form-control")[3];
    var type = document.getElementsByClassName("form-control")[4];
    var other_text = document.getElementsByClassName("form-control")[5];
    var file_dump = document.getElementById("file-dump");


    var valid=true;

	if(!(/^[a-zA-Z]{3}[0-9]{3}$/).test(course_code.value)){
		course_code.setCustomValidity("Please enter a valid course code");
		valid=false;
	}
	else{
		course_code.setCustomValidity("");
	}

	if(type.value==''){
		type.setCustomValidity("Please choose a valid document type")
		valid=false
	}
	else{
		type.setCustomValidity("")
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
		if(required[i].value==''){
			required[i].setCustomValidity("Please enter a valid value");
			valid=false
		}
		else{
			required[i].setCustomValidity("")
		}
	}

	if(file_dump.files.length==0){
		file_dump.setCustomValidity("Please select one or more files to upload");
		valid=false
	}
	else{
		file_dump.setCustomValidity("");
	}

  	return valid
}