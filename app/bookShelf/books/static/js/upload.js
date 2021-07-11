var TAG_LIST_SEPARATOR=',,'
var TAG_SUB_LIST_SEPARATOR=','

$(document).ready(function() {
	

	$('.nav_li').hide();
	$('.nav_li').fadeIn('slow');

	$('#form').hide();
	$('#form').slideDown('slow');

	var fileDump=document.getElementById('file-dump')
	var next_button=document.getElementById('next-btn')
	fileDump.addEventListener("change",function(){
		document.getElementById('tags-section').innerHTML=''
	})

	next_button.addEventListener("click", function(){
		if(isValid()){
			var default_tags=[]
			default_tags.push(document.getElementById('code-input').value)
			default_tags.push(document.getElementById('prof').value)
			if (fileDump.files.length != 0) {

				document.getElementById('tags-section').innerHTML="<div class='tag-section-heading'><strong>Edit Tags (Optional)</strong></div>" 
				for (var i = 0; i < fileDump.files.length; i++) {
					addTagBox(fileDump.files[i].name,default_tags)
				}

				var img_files = [];
				var IMG_EXT = ['jpg', 'jpeg', 'png', 'gif']
				//check if multiple image files have been uploaded to concatenate them.
				for(var i = 0; i< fileDump.files.length; i++){
					var file_name=fileDump.files[i].name;
					var ext = file_name.split(".").pop();
					if(IMG_EXT.includes(ext)){
						img_files.push(fileDump.files[i]);
					}
				}
				if(img_files.length>1){
					addImageReorderBox(img_files)
				}

				var buttons = document.getElementsByClassName("submit-btn");
				for(var j=0;j<buttons.length;j++){
					buttons[j].parentNode.removeChild(buttons[j]);	
				}
				var submit_button = document.createElement('button')
				submit_button.setAttribute("class","btn btn-outline-primary col-sm-6 upload-btn submit-btn")
				submit_button.innerHTML="Submit"
				submit_button.addEventListener("click", function(){
					submit_data()
				});

				document.getElementById('submit-row').appendChild(submit_button)
			}
		}
	})
});

function addTagBox(name,tags){
	var tagString=tags.join(',')
	var tagsSection=document.getElementById('tags-section')
	var fileBox = document.createElement('div')
	tagsSection.appendChild(fileBox)
	fileBox.setAttribute("class","file-box")
	fileBox.innerHTML+="<div class='file-name'><strong>Filename: </strong>"+name+"</div><div class='tagbox'></div><input class='fake-input form-control col-md-8' placeholder='Enter tags here, eg. Major, Practical, Tutorial' value="+tagString+">"
	tagInput(fileBox)
}

function addImageReorderBox(files){
	document.getElementById('reorder-section').innerHTML="<div class='reorder-section-heading'>"+
		"<strong>You have uploaded more than one image files. Please select the order of the pages in these images</strong>"+
		"</div>";
	for(var i=0; i<files.length; i++){
		var preview = document.createElement('div');
		preview.setAttribute('class', 'image-preview');
		preview.setAttribute('style', 'display: inline-block; margin: 1em;')
		document.getElementById('reorder-section').appendChild(preview);

		var img = document.createElement('img')
		img.setAttribute('src', URL.createObjectURL(files[i]));
		img.setAttribute('height', '100px');
		img.setAttribute('width', '100px');
		img.setAttribute('alt', files[i].name);
		preview.appendChild(img);

		var input = document.createElement('select')
		input.setAttribute('type', 'text');
		input.setAttribute('name', i+1);
		input.setAttribute('class', 'reorder-dropdown');
		input.setAttribute('style', 'display: flex; margin: 0 auto;')
		for(var j=1; j<=files.length; j++){
			var option = document.createElement('option');
			option.setAttribute('value', j);
			option.innerHTML = j;
			if(j==i+1)
			    option.setAttribute('selected', '');
			input.appendChild(option);
		}
		preview.appendChild(input);
	}
}

function getImageOrder(){
	var imageOrder = [];
	if(document.getElementById('reorder-section').children.length>0){
		var imgOrder = document.getElementsByClassName('image-preview');
		for(var i=0; i<imgOrder.length; i++){
			var value = imgOrder[i].getElementsByTagName('select')[0].value;
			imageOrder.push(value);
		}
	}
	return imageOrder;
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

	var orderBox = document.getElementsByClassName('image-preview')[0].getElementsByTagName('select')[0];
	if(valid){
		orderBox.setCustomValidity("");
	}
	else{
		orderBox.setCustomValidity("Page numbering not unique or out of bounds. Please enter valid page numbers");
	}

	return orderBox.checkValidity()
}

function submit_data(){
	var imageOrder = getImageOrder();

	if(isValid() && isValidOrder(imageOrder)){
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

		
		var imageOrderString = ''
		if(imageOrder.length>0)
			imageOrderString = imageOrder.join(TAG_SUB_LIST_SEPARATOR); 
		var imageOrderInput = document.createElement("input")
		imageOrderInput.value=imageOrderString;

		imageOrderInput.setAttribute("type", "hidden");
		imageOrderInput.setAttribute("name", "image-order")
		

		document.getElementById("upload-form").appendChild(imageOrderInput)
		document.getElementById("upload-form").appendChild(hiddenInput)
		document.getElementById("upload-form").submit()
	}
}
