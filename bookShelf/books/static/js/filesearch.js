//

$(document).ready(function(){
	$("button")[0].addEventListener("click", function(){
		DB={};;                        
		$.getJSON( '/books/api/search',{"path":"/","query":$("input")[0].value}, function( data ){
			// var DB={};;
		    DBZ=data;
		    $.getJSON( API_URL,{"path":"/",depth:DEPTH}, function( data ){
		        DB=data;	    
		        // reset output
		        var box = $.parseHTML("<div id='output'></div>")
		        $("#output").remove()
		        $("button").after(box)

				for (var i=0; i< DBZ["result"].length;i++){

			    	var path_prefixer=DBZ["result"][i]
			    	var l =  path_prefixer.length

			    	if (typeof(get_prefix_dict(path_prefixer))==="string"){

				    	var name =path_prefixer[l-1][0]
					  	
					    var display_path=''
					    console.log(path_prefixer)
					    for (var j=0;j<l-1;j++){
					    	display_path+= path_prefixer[j][0]+'/'
					    }
					    display_path+=name
					    console.log(MEDIA_PREFIX+display_path)
					    var html = "<div><a href="+MEDIA_PREFIX+display_path+" target = '_blank'>"+display_path+"</a></div>"
					    var link = $.parseHTML(html)
					    
				        $("#output").append(link)
					}
			    }
			});
		});
	})
})
