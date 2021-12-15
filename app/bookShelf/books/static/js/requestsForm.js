var requests_data = [];

const API_URL = "/books/api/requests";


$(document).ready(function() {

    $('.nav_li').hide();
    $('.nav_li').fadeIn('slow');

    $('#form').hide();
    $('#form').slideDown('slow');

    $.getJSON(API_URL, function(data) {
        requests_data = data["requests_data"]
    });

    $('#prof').select2({theme: 'bootstrap4', });

    var start = 2005;
    var end = new Date().getFullYear();
    var options = "";
    for(var year = end ; year >= start; year--){
      options += "<option value=\""+ year +"\" >"+ year +"</option>";
    }
    document.getElementById("year").innerHTML = options;

    var submit_button = document.getElementById('submit-btn');

    document.getElementById('requests-form').addEventListener("input", function(){
        if(document.getElementById('requests-form').classList.contains('was-validated')){
            var valid = isValid();
        }
    });

    submit_button.addEventListener("click", function() {
        if(isValid()){
            document.getElementById("requests-form").submit();
        }
    });

});

// function to check the validity of the entered data
function isValid(){
    var course_code = document.getElementById("code-input");
    var sem = document.getElementById("sem");
    var year = document.getElementById("year");
    var prof = document.getElementById("prof");
    var type = document.getElementById("type_file");
    var other_info = document.getElementById("other_info");

    var valid = true;

    if(!(/^[a-zA-Z]{3}[0-9]{3}$/).test(course_code.value)){
        course_code.setCustomValidity("Please enter a valid course code");
        course_code.parentElement.getElementsByClassName("invalid-feedback")[0].innerHTML = course_code.validationMessage;
        valid = false;
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


	if(type.value=="Quizzes" || type.value=="Minor1" || type.value=="Minor2" || type =="Major"){
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

    if(checkPresence(course_code.value, sem.value, year.value, type_file.value, prof.value, other_info.value) === true){
        valid = false;
    }

    showValidation();

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

function checkPresence(course_code, sem, year, type_file, prof, other_info){
    var is_present = false;

    var filtered_data = requests_data.filter(function(value){
        var present = true;
        
        if(value['course_code'].toUpperCase() != course_code.toUpperCase()){
            present = false;
        }
        if(value['type_file'] != type_file){
            present = false;
        }
        if(value['sem'] != sem && value['sem']!="None"){
            present = false;
        }
        if(value['year'] != year){
            present = false;
        }
        if(value['prof'] != prof && value['prof']!="None"){
            present = false;
        }

        return present;
    });

    if(filtered_data.length>0){
        is_present = true;
        show_matches(filtered_data);
    }
    else is_present=false;

    return is_present;
}

// TODO: Display matching requests already present
function show_matches(filtered_data){
    var filtered_requests_browser = document.getElementById('filtered-requests');
    filtered_requests_browser.innerHTML = "";
    var i=1;
    for(data of filtered_data){

        var html = '<div class="list-group-item card bg-transparent p-0" id="requests_card_'+i+'">\
                        <div class="card-body row justify-content-around">\
                            <h5 class="col-sm-1 card-title align-self-center text-center p-0">'+data["course_code"]+'</h5>\
                            <h6 class="col-sm-2 card-subtitle align-self-center text-center">'+data["sem"]+' - '+data["year"]+'</h6>\
                            <input class="col-sm-2 btn btn-outline-secondary" readonly value="'+data["type_file"]+'">\
                            <input class="col-sm-5 btn btn-outline-secondary" readonly value="'+data["prof"]+'">\
                            <button class="col-sm-2-wrap btn btn-secondary" type="button" data-toggle="collapse" data-target="#other_info_'+i+'">Other Info</button>\
                        </div>\
                        <div class="collapse" id="other_info_'+i+'">\
                            <div class="card-body">'+data["other_info"]+'</div>\
                        </div>\
                    </div>';
        
        var card = $.parseHTML(html)[0];
        filtered_requests_browser.appendChild(card);
        i+=1;
    }

    $('#filtered-requests-modal').modal('show');
}