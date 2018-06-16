//run after tagtest.js

var input= document.getElementsByClassName("fake-input")[0]
var true_input= document.createElement("input")
var current_tags_string =document.getElementById("current-tags").value
var form = document.getElementsByClassName("uploadform")[0]

true_input.id="true_input"
true_input.setAttribute("name", "tags");
true_input.setAttribute("type", "hidden");
input.value=current_tags_string

tagInput(document)

document.getElementsByClassName("submit")[0].addEventListener("click", function(){
	var tagsList = [];
	var tags = document.getElementsByClassName("tag")
	for (var i = 0; i < tags.length; i++) {
        tagsList.push(tags[i].getElementsByClassName("tag-text")[0].innerHTML);
	}
	true_input.value=tagsList.join(',')
	form.appendChild(true_input);
	form.submit()
})
document.getElementsByClassName("reset")[0].addEventListener("click", function(){
	
	form.reset()
	var tags = document.getElementsByClassName("tag")
	console.log(tags)

	while(tags.length>0) {
		tags[0].parentNode.removeChild(tags[0])
	}
	input.value=current_tags_string
	tagInput(document)
})


