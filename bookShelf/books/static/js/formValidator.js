document.getElementById("other_text").addEventListener("input", function() {
    if (document.getElementById("other_text").validity.typeMismatch) {
        document.getElementById("other_text").setCustomValidity("Only letters, numbers and spaces are allowed for this field");
    } else {
        document.getElementById("other_text").setCustomValidity("");
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
    if(sem=="" && year=="" && exam!="other") {
        // console.log("done");
        document.getElementById("other").setCustomValidity("Other must be selected if sem and year are left blank.");
    } else {
        document.getElementById("other").setCustomValidity("");
    }
    if (exam=="other" && other_text=="") {
        // console.log("done2");
        document.getElementById("other_text").setCustomValidity("Please enter the file name as well");
    } else {
        document.getElementById("other_text").setCustomValidity("");            
    }
});