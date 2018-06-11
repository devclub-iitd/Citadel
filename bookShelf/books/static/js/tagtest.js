var input= document.getElementById("fake-input")
var true_input= document.createElement("input")
var form = document.getElementById("form")
var tagbox = document.getElementById("tagbox")

true_input.id="true_input"
true_input.setAttribute("name", "tags");
true_input.setAttribute("type", "hidden");

tags=[]

input.addEventListener("input", function(){
	runTag();
});

document.getElementById("submit").addEventListener("click", function(){
	document.body.appendChild(form)
	var tagsList = [];
	for (var i = 0; i < tags.length; i++) {
        tagsList.push(tags[i].getElementsByClassName("tag-text")[0].innerHTML);
	}
	true_input.value=tagsList.join(',')
	form.appendChild(true_input);
	form.submit()
})

runTag();


function runTag(){
	var text= input.value.split(',')
	if (text.length > 1){
		for (var i = 0; i <=text.length - 1; i++) {
			if (text[i].length>0){
				text[i]=text[i].trim().toLowerCase()
				if (isUnique(text[i])){
					makeTag(text[i])
				}
			}
		}
		input.value=''
	}
}

function makeTag(text){
	var tag = document.createElement("span")
	var close = document.createElement("span")
	close.addEventListener("click", function(){
		removeTag(tags.indexOf(tag))
	})
	tag.innerHTML="<span class='tag-text'>"+text+"</span>"
	close.innerHTML="X"
	tag.appendChild(close)
	tagbox.appendChild(tag)
	tags.push(tag)
}


function isUnique(text){
	for (var i = 0; i < tags.length; i++) {
		if (tags[i].getElementsByClassName("tag-text")[0].innerHTML==text){
			return false
		}
	}
	return true
}

function removeTag(index){
	var rtag = tags[index]
	tags.splice(index,1)
	tagbox.removeChild(rtag)

}