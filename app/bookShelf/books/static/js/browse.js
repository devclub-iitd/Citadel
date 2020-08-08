DB = {}

var COLS = [];

var PATH_ELEM = $("#path-bar")[0];
var COLS_ELEM = $("#file-browser")[0];
var MEDIA_PREFIX = "/media/database/";
var API_URL = "/books/api/structure";
//var DEPTH =3;
var DEPTH = -1;  //hacky fix, must fix "db==null" in get_prefix_dict, insert_prefix_dict for search terms
var ZIP_URL = "/books/download_course/?course="


// creates single pathbar navigation element
function create_elem_path(name,url)
{
    var html = '<li class="breadcrumb-item"><a href="'+url+'">'+name+'</a></li>';
    return $.parseHTML(html)[0];
}

// filters the column list-group according to the query here
function search_column()
{
    var list_group = this.nextElementSibling;
    var query = this.value.toUpperCase();

    $(list_group).children().show();
    function filter_fn(index){ return (this.textContent.toUpperCase().indexOf(query) <= -1);}
    $(list_group).children().filter(filter_fn).hide();
}

// creates the base div block which contains a pane of file browser
function create_base_div_col()
{
    var html = '<div class="file-column border rounded"> \
                    <input onkeyup="search_column.call(this);" type="text" class="form-control search_bar" placeholder="Filter Column.." aria-label="search bar"> \
                    <div class="list-group">\
                    </div> \
                </div>';
    return $.parseHTML(html)[0];
}

// removes all the columns in the COLS array except the first num_cols_retain 
function remove_cols(num_cols_retain)
{
    for(var i=num_cols_retain;i<COLS.length;i++)
    {
        COLS[i].remove();
    }
    COLS = COLS.slice(0,num_cols_retain);
}

// updates the current file browser view according to the path prefix given
function update_view(path_prefix)
{
    // number of columns to retain
    var num_cols = path_prefix.length;
    if (path_prefix.length>=1){
        if(path_prefix[0].length==3){
            num_cols=num_cols-path_prefix[0][2]+1
        }
    }
    
    // removing the un-needed columns
    remove_cols(num_cols);

    // removing active status from all the elements in last column
    $(COLS[COLS.length-1]).children().children().removeAttr('style');
    $(COLS[COLS.length-1]).children().val(null);

    // creating column corresponding to the clicked folder
    create_column(path_prefix.slice());

    // redrawing the path bar
    redraw_path_bar(path_prefix);
}

// chooses a random colour to highlight a given jquery obj
function random_highlight(obj)
{
    var style = STYLES[Math.floor(Math.random()*STYLES.length)];
    obj.css(style);
}

// returns the event handler to be called when an element is clicked in file column
function get_event_handler_col(is_file,path_prefix,url)
{
    if(is_file)
    {
        return function(){var win = window.open(url,'_blank');win.focus();};
    }
    else
    {
        return function()
        {
            update_view(path_prefix.slice());
            random_highlight($(this));
        };
    }
}

// create an entry for the div block of column of file viewer
// also add necessary event listener
function create_elem_col(path_prefix,name,is_file)
{
    var new_id = "";
    for(var i=0;i<path_prefix.length;i++)
    {
        new_id += path_prefix[i][0]+"/";
    }

    new_id += name;

    path_prefix.push([name,"#"+new_id]);

    var html = '<a href="#" class="list-group-item list-group-item-action col-item-wrap" id="'+new_id+'"><div class="col-item" title="'+name+'">'+name+'</div></a>';
    var btn = $.parseHTML(html)[0];

    var handler = get_event_handler_col(is_file,path_prefix.slice(),MEDIA_PREFIX+new_id);
    
    btn.onclick = handler;
    if (path_prefix.length == 2){
        //to add the download course button
        html = "<i class='material-icons'>get_app</i>";
        var bt=$.parseHTML(html)[0];

        handler = function(){
            var win = window.open(ZIP_URL+name,'_blank');
            win.focus();
        };
        bt.onclick = handler;
        btn.getElementsByClassName('col-item')[0].append(bt)
    }
    return btn;

}

// redraws the path bar according to the value in PATH array
function redraw_path_bar(path)
{
    //reset the current html
    PATH_ELEM.innerHTML="";

    //add the new path
    for(var i=0;i<path.length;i++)
    {
        PATH_ELEM.append(create_elem_path(path[i][0],path[i][1]));
    }
}

// get the dict corresponding to the given path_prefix
function get_prefix_dict(path_prefix)
{
    var db = DB;

    for(var i=0;i<path_prefix.length;i++)
    {
        db = db[path_prefix[i][0]];
    }
    return db;
}

// inserts the new_value at the path given by path_prefix
function insert_prefix_dict(path_prefix,new_val)
{
    var db = DB;
    for(var i=0;i<path_prefix.length-1;i++)
    {
        db = db[path_prefix[i][0]];
    }
    db[path_prefix[path_prefix.length-1][0]]=new_val
}

// creates column containing the files according to the path_prefix passed
function create_column(path_prefix)
{
    var dic = get_prefix_dict(path_prefix.slice())
    if (dic===null)
    {
        // fetch more data
        path = "/"
        for(var i=0;i<path_prefix.length;i++)
        {
            path += path_prefix[i][0]+"/";
        }
        $.getJSON( API_URL,{"path":path,depth:DEPTH}, function( data )
        {
            insert_prefix_dict(path_prefix,data)
            create_column(path_prefix);
        });

    }
    else
    {

        var base_div = create_base_div_col();
        var search_bar = base_div.children[0];
        var list_group = base_div.children[1];
        var folders = []
        var files = []

        for (var key in dic)
        {
            if(dic.hasOwnProperty(key))
            {
                if(typeof(dic[key])==='string')
                {
                    files.push([key,create_elem_col(path_prefix.slice(),key,true)]);
                }
                else
                {
                    // put in folder
                    folders.push([key,create_elem_col(path_prefix.slice(),key,false)]);
                }
            }
        }

        folders.sort(function(a,b){return (a[0] > b[0]) ? 1 : ((b[0] > a[0]) ? -1 : 0);});
        files.sort(function(a,b){return (a[0] > b[0]) ? 1 : ((b[0] > a[0]) ? -1 : 0);});

        for(var i=0;i<folders.length;i++)
        {
            list_group.append(folders[i][1]);
        }
        for(var i=0;i<files.length;i++)
        {
            list_group.append(files[i][1]);
        }

        $(base_div).hide();

        // adding column to the html of the page
        COLS_ELEM.append(base_div);
    
        // saving the column object in COLS array
        COLS.push(base_div);

        $(base_div).fadeIn(200);

        // scroll this new column into view
        base_div.scrollIntoView();
    }
}

