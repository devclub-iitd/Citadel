
// $("button")[0].addEventListener("click", function(){
//     var val = $("input")[0].value;
//     $.getJSON( API_URL,{"path":val,depth:-1}, function( data )
//         {
//         	var db = data
// 			printer(data,val)
            
//         });
// });





// function printer(data,path){

// 	for (var key in data){
// 		if(typeof(data[key])==='string'){
// 			$("#output").append($.parseHTML("<div>"+path+'/'+key+"</div>"))
// 		}
// 		else{
// 			printer(data[key],path+'/'+key);
// 		}
// 	}

// }

$("button")[0].addEventListener("click", function(){
	var DB={};;                        
	update_view([]);                    
	redraw_path_bar([["Home","#"]]);

	$.getJSON( '/books/api/search',{"path":"/","query":$("input")[0].value}, function( data ){
	        
	    $.getJSON( API_URL,{"path":"/",depth:DEPTH}, function( data ){
	        DB=data;
	    });
	   
	    DBZ=data;
		for (var i=0; i< DBZ["result"].length;i++){
	    	var path_prefixer=DBZ["result"][i]   
	    	var l =  path_prefixer.length
	        $(".list-group").append(create_elem_col(path_prefixer.slice(0,l-1),path_prefixer[l-1][0],false))
	    }
	});
})
