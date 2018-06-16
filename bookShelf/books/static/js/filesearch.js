//

$(document).ready(function(){

	$("button")[1].addEventListener("click", function(){
		reset_results();
		$("input")[0].value=''
	})

	$("input")[0].addEventListener("keydown",function(e){
        if(e.keyCode === 13 || e.which ===13){
            e.preventDefault(); 
            file_search();
        }
    })

	$("button")[0].addEventListener("click", function(){
		file_search()
	})
})


function file_search(){
	DB={};;                        
	$.getJSON( '/books/api/search',{"path":"/","query":$("input")[0].value}, function( data ){
		// var DB={};;
	    DBZ=data;
	    $.getJSON( API_URL,{"path":"/",depth:DEPTH}, function( data ){
	        DB=data;	    
	        // reset output
	        reset_results()

			for (var i=0; i< DBZ["result"].length;i++){

		    	var path_prefixer=DBZ["result"][i]
		    	var l =  path_prefixer.length

		    	if (typeof(get_prefix_dict(path_prefixer))==="string"){

			    	var name =path_prefixer[l-1][0]
				  	
				    var display_path=''
				    for (var j=0;j<l-1;j++){
				    	display_path+= path_prefixer[j][0]+'/'
				    }
				    display_path+=name
				    var html = "<div class='file-name file-box'><a href="+MEDIA_PREFIX+display_path+" target = '_blank'>"+display_path+"</a></div>"
				    var link = $.parseHTML(html)
				    
			        $("#output").append(link)
				}
		    }
		});
	});
}

function reset_results(){
	var box = $.parseHTML("<div id='output' class='results-box'></div>")
    $("#output").remove()
    $(".input-group").after(box)
}