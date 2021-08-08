// Need to pass CSRF token with POST request for security (Django would forbid it otherwise)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// function to add a delete button on each request for admins only
function add_close_btn(){
    var html = '<button type="button" class="close close-button" onclick="removeRequest($(COL_ELEM).children().index(this.parentNode))" aria-label="Close">\
                    <span aria-hidden="true" style="cursor: pointer;">&times;</span>\
                </button>';
    var close_btn = $.parseHTML(html)[0];
    
    $('.list-group-item').prepend(close_btn);
}

function removeRequest(index){
    var pattern = /\brequests_card_\d+\b/;
    var end_pattern = /\d+\b/

    var req_request = $(COL_ELEM).children().filter('.list-group-item')[index];
    var req_request_id = req_request.getAttribute('id');
    if(pattern.test(req_request_id)){
        if(end_pattern.exec(req_request_id) == String(index+1)){
            content = {
                'course_code': requests_data[index][COURSE_CODE],
                'sem': requests_data[index][SEM],
                'year': requests_data[index][YEAR],
                'prof': requests_data[index][PROF],
                'type_file': requests_data[index][TYPE_FILE],
                'csrfmiddlewaretoken': csrftoken
            }
            $.post(API_URL, content, function(data) {
                set_up();
            });
        }
    }
    else console.log("Failure. Index= " +index+ " not found")
}