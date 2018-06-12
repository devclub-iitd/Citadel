//run after tagtest.js

tagInput(document)


var true_input= document.createElement("input")
true_input.id="true_input"
true_input.setAttribute("name", "tags");
true_input.setAttribute("type", "hidden");

var form = document.getElementsByClassName("uploadform")[0]
document.getElementsByClassName("submit")[0].addEventListener("click", function(){
	document.body.appendChild(form)
	var tagsList = [];
	for (var i = 0; i < tags.length; i++) {
        tagsList.push(tags[i].getElementsByClassName("tag-text")[0].innerHTML);
	}
	true_input.value=tagsList.join(',')
	form.appendChild(true_input);
	form.submit()
})