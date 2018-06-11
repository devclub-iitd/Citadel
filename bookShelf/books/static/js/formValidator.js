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
document.getElementById("upload-btn").addEventListener("click", function() {
    // console.log("yo");
    var radios = document.getElementsByName("type_exam");
    var course_code = document.getElementById("upload-form").elements[1].value;
    var sem = document.getElementById("upload-form").elements[2].value;
    var year = document.getElementById("upload-form").elements[3].value;
    var prof = document.getElementById("upload-form").elements[4].value;
    var exam = "none";
    var other_text = document.getElementById("upload-form").elements[11].value;
    for(var i=0,length=radios.length;i<length;i++) {
        if (radios[i].checked) {
            exam = radios[i].value;
            break;
        }
    }
    if(sem=="" && year=="" && exam!= "other") {
        document.getElementById("other").setCustomValidity("Other must be selected if Semester and Year are left blank.");
    } else {
        document.getElementById("other").setCustomValidity("");
    }
    if (exam=="other" && other_text=="") {
        document.getElementById("customFilename").setCustomValidity("Please enter the file name as well");
    } else {
        document.getElementById("customFilename").setCustomValidity("");            
    }
});

