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
			    		var is_file=true;
			    	}
			    	else{
			    		var is_file=false;
			    	}
			    	var name =path_prefixer[l-1][0]
			    	if(is_file){ 

			    		// repeated code from browse.js, TODO: cleanup
			    		// get data from filename of metafile

				        var desc = name.split("==")
				        if (desc.length==3){
				            if (desc[2]=='.meta'){
				                name = desc[0]
				                var raw_loc = desc[1]
				                var dirs = raw_loc.split('-')
				                var file_dir = dirs.join("/")
				                var file_loc = '../'+file_dir + '/' + name
				            }
				        }
				  	
				    var display_path=''
				    console.log(path_prefixer)
				    for (var j=0;j<l-1;j++){
				    	display_path+= path_prefixer[j][0]+'/'
				    }
				    display_path+=name
				    var html = "<div><a href="+file_loc+" target = '_blank'>"+display_path+"</a></div>"
				    var link = $.parseHTML(html)
				    
			        $("#output").append(link)
				  	}
			    }
			});
		});
	})
})
