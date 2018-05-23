

var API_URL = "/books/api/structure";
$("button")[0].addEventListener("click", function(){
    var val = $("input")[0].value;
    $.getJSON( API_URL,{"path":val,depth:-1}, function( data )
        {
        	var db = data
			printer(data,val)
            
        });
});





function printer(data,path){

	for (var key in data){
		if(typeof(data[key])==='string'){
			$("#output").append($.parseHTML("<div>"+path+'/'+key+"</div>"))
		}
		else{
			printer(data[key],path+'/'+key);
		}
	}

}


