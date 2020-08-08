
function tagInput(box){
	var input= box.getElementsByClassName("fake-input")[0]
	var tagbox = box.getElementsByClassName("tagbox")[0]

	var tags=[]

	input.addEventListener("input", function(){
		runTag();
	});

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
		tag.setAttribute("class", "tag");
		var close = document.createElement("span")
		close.setAttribute("style", "cursor: pointer;");
		close.addEventListener("click", function(){
			removeTag(tags.indexOf(tag))
		})
		tag.innerHTML="<span class='tag-text'>"+text+"</span>"
		close.innerHTML="×"
		close.setAttribute("class", "close-button");
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
	runTag();
}



