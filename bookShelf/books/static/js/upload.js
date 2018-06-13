var TAG_LIST_SEPARATOR=',,'
var TAG_SUB_LIST_SEPARATOR=','

$(document).ready(function() {
	

	$('.nav_li').hide();
	$('.nav_li').fadeIn('slow');

	$('#form').hide();
	$('#form').slideDown('slow');

	var fileDump=document.getElementById('file-dump')
	var next_button=document.getElementsByClassName('btn-primary')[0]
	fileDump.addEventListener("change",function(){
		document.getElementById('tags-section').innerHTML=''
	})

	next_button.addEventListener("click", function(){
		var default_tags=[]
		default_tags.push(document.getElementById('code-input').value)
		default_tags.push(document.getElementById('prof').value)
		if (fileDump.files.length != 0) {
			document.getElementById('tags-section').innerHTML="<div class='tag-section-heading'><strong>Add Tags</strong></div>" 
			for (var i = 0; i < fileDump.files.length; i++) {
				addTagBox(fileDump.files[i].name,default_tags)
			}
			var submit_button = document.createElement('button')
			submit_button.setAttribute("class","btn btn-default")
			submit_button.className = "btn btn-primary";
			submit_button.innerHTML="Submit"
			submit_button.addEventListener("click", function(){
				submit_data()
			});
			document.getElementById('tags-section').appendChild(submit_button)
		}
	})
});

function addTagBox(name,tags){
	var tagString=tags.join(',')
	var tagsSection=document.getElementById('tags-section')
	var fileBox = document.createElement('div')
	tagsSection.appendChild(fileBox)
	fileBox.setAttribute("class","file-box")
	fileBox.innerHTML+="<div>"+name+"</div><span class='tagbox'></span><br><input class='fake-input' placeholder='Enter tags here, eg. Major, Practical, Tutorial' value="+tagString+"><br><br><br>"
	tagInput(fileBox)
}

function submit_data(){
	
	var tagBoxes = document.getElementsByClassName('tagbox')
	var tagList=[]
	for (var i = 0; i < tagBoxes.length; i++) {
		var tagSubList=[]
		for (var j = 0; j < tagBoxes[i].getElementsByClassName('tag-text').length; j++) {
			tagSubList.push(tagBoxes[i].getElementsByClassName('tag-text')[j].innerHTML)
		}
		var tagSubString=tagSubList.join(TAG_SUB_LIST_SEPARATOR)
		tagList.push(tagSubString)
	}

	var tagString=tagList.join(TAG_LIST_SEPARATOR)
	var hiddenInput=document.createElement("input")
	hiddenInput.value=tagString

	hiddenInput.setAttribute("type", "hidden")
	hiddenInput.setAttribute("name", "tag-string")
	document.getElementById("upload-form").appendChild(hiddenInput)
	document.getElementById("upload-form").submit()
}
