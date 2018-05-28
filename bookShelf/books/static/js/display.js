// Only run after browse.js

// Creates database browser


$(document).ready(function()
{
    if(COLS_ELEM) // checking if the current page has filebrowser div
    {
        $.getJSON( API_URL,{"path":"/",depth:DEPTH}, function( data )
        {
            DB=data;                        
            update_view([]);                    
            redraw_path_bar([["Home","#"]]);
        });
    }
});
