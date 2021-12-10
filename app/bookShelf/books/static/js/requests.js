var requests_data = [];

const API_URL = "/books/api/requests";
var COL_ELEM = $("#requests-browser")[0];

const COURSE_CODE = "course_code"
const SEM = "sem"
const YEAR = "year"
const TYPE_FILE = "type_file"
const PROF = "prof"
const OTHER_INFO = "other_info"


$(document).ready(function() {
    if(COL_ELEM){
        set_up();
    }
});

function set_up(){
    // clearing any prior list, if present
    COL_ELEM.innerHTML = "";

    $.getJSON(API_URL, function(data) {
        requests_data = data["requests_data"]
        create_col_elem();
        add_close_btn();
        
        var start = 2005;
        var end = new Date().getFullYear();
        var options = "";
        for(var year = end ; year >= start; year--){
          options += "<option value=\""+ year +"\" >"+ year +"</option>";
        }
        document.getElementById("year-filter").innerHTML = options;
        
        $('#prof-filter').select2({theme: 'bootstrap4', });
    });
}

function create_col_elem(){
    if(requests_data.length == 0){
        var msg = document.createElement('div');
        msg.classList.add('card', 'bg-transparent');
        var msgbody = document.createElement('div');
        msgbody.classList.add('card-body')
        msgbody.innerHTML = '<h6 style="text-align: center;">No one has requested for any material yet!</h6>';
        msg.appendChild(msgbody);
        COL_ELEM.appendChild(msg);

        $('.filter-bar').hide();
        return;
    }

    var i=1;
    for(data of requests_data){

        var html = '<div class="list-group-item card bg-transparent p-0" id="requests_card_'+i+'">\
                        <div class="card-body row justify-content-around">\
                            <h5 class="col-sm-1 card-title align-self-center text-center p-0">'+data[COURSE_CODE]+'</h5>\
                            <h6 class="col-sm-2 card-subtitle align-self-center text-center">'+data[SEM]+' - '+data[YEAR]+'</h6>\
                            <input class="col-sm-2 btn btn-outline-secondary" readonly value="'+data[TYPE_FILE]+'">\
                            <input class="col-sm-5 btn btn-outline-secondary" readonly value="'+data[PROF]+'">\
                            <button class="col-sm-2-wrap btn btn-secondary" type="button" data-toggle="collapse" data-target="#other_info_'+i+'">Other Info</button>\
                        </div>\
                        <div class="collapse" id="other_info_'+i+'">\
                            <div class="card-body">'+data[OTHER_INFO]+'</div>\
                        </div>\
                    </div>';
        
        var card = $.parseHTML(html)[0];
        COL_ELEM.appendChild(card);
        i+=1;
    }
    $('.filter-bar').show();
}



function filter_col(){
    var query = this.value.toUpperCase();

    $(COL_ELEM).children().show();
    function filter_fn(index){
        return (this.textContent.toUpperCase().indexOf(query) <= -1);
    }
    $(COL_ELEM).children().filter(filter_fn).hide();
}