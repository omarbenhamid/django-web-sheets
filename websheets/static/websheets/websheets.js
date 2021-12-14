const messageEl=document.getElementById("message");
var tiIdx;

function message(html, timeout) {
    if(html) {
        messageEl.innerHTML=html;
        messageEl.style.display='block';
    } else {
        messageEl.style.display='none';
    }
    if(tiIdx) clearTimeout(tiIdx);
    if(timeout)
        tiIdx=setTimeout(() => message(), timeout)
}

function parseCSV(csv) {
    var records = CSV.parse(csv, {header: false});
    
    var ret={len: records.length+100}

    for (var i=0; i<records.length; i++) {
        var data = records[i];
        var cells={}

        for (var j=0; j<data.length; j++) {
            if(i==0) cells[j]={text: data[j], style: 1}; //Title style
            else cells[j]={text: data[j]};
        }
        ret[i]={cells: cells}
    }
    return ret;
}

function loadData(xs, csvdatajson) {
    var data=[];

    for(var key in csvdatajson) {
        var records=parseCSV(csvdatajson[key].data);
        var sheet={
            name: key, 
            styles: [
                {color: '#ff0000', textwrap: true}, //Validation erros style
                {
                    "font": {
                        "bold": true,
                        "italic": true
                    },
                    "border": {
                        "bottom": [
                            "thin",
                            "#000"
                        ]
                    },
                    "align": "center"
                }, //Title Stype
            ],
            rows: records,
            cols: {}
        }
        if(hideIdCol){
            for(ci in records[0].cells) {
                if(records[0].cells[ci].text == 'id') {
                    sheet.cols[ci]={'hide':true};
                    break;
                }
            }
        }
        
        for(var sk in csvdatajson[key].format) {
            if(sk == 'rows') continue;
            sheet[sk]=csvdatajson[key].format[sk];
        }
        
        data.push(sheet);
    }
    
    xs.loadData(data);
    message("Saved");
    dirty=false;
}


function postData(params){
    // Turn the data object into an array of URL-encoded key/value pairs.
    let urlEncodedData = "", urlEncodedDataPairs = [], name;
    for( name in params ) {
     urlEncodedDataPairs.push("__data__"+encodeURIComponent(name)+'='
        +encodeURIComponent(params[name].data));
    }
    for( name in params ) {
     urlEncodedDataPairs.push("__format__"+encodeURIComponent(name)+'='
        +encodeURIComponent(JSON.stringify(params[name].format)));
    }
    
    var http = new XMLHttpRequest();

    http.open('POST', '', true);
    http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    http.setRequestHeader('X-CSRFToken', csrf_token);
    
    http.onreadystatechange = function() {//Call a function when the state changes.
        if(http.readyState == 4) {
            if (http.status == 200) {
                const currSheet = xs.getActiveSheet().name;
                loadData(xs, JSON.parse(http.responseText));
                const si = xs.getSheetIndex(currSheet);
                if(si >= 0) xs.activateSheet(si)
            }else{
                message("<span style='color:red'>Saving errors</span>");
                //TODO: better rendendering of validation errors
                errors=JSON.parse(http.responseText);
                console.log(errors);
                for(var sheet in errors) {
                    var sheetIndex=xs.getSheetIndex(sheet);
                    if(sheetIndex < 0) {
                        console.log("Should never happen: sheet not found", sheet);
                        continue;
                    }
                    w=params[sheet]['width']
                    xs.cellText(0,w,'Validation Errors',sheetIndex)
                    xs.cell(0,w,sheetIndex).style=0;
                    
                    for(var row in errors[sheet]) {
                        xs.cellText(row,w,errors[sheet][row].join('\r\n'),sheetIndex)
                        xs.cell(row,w,sheetIndex).style=0;
                    }
                }
                xs.reRender();
            }
        }
    }
    http.send(urlEncodedDataPairs.join("&"));
    message("<i>Saving ...</i>");
}

function serialize(xsdata) {
    var ret={};
    for(var si in xsdata) {
        var records=[];
        var s=xsdata[si];
        
        for(var ri in s.rows) {
            var row=[];
            records[ri]=row;
            var cells=s.rows[ri].cells
            for(var ci in cells) {
                if(cells[ci].style == 0) {
                    xs.cellText(ri,ci,'',si);
                    continue;
                }
                row[ci]=cells[ci].text;
            }
            for(var i=0; i < row.length; i++) 
                if(row[i]===undefined) row[i]=''
        }
        
        var w=0;
        
        for(var i=0; i < records.length; i++) {
            if(records[i]===undefined) records[i]=[]
            l=records[i].length
            if(l > w) w=l;
        }
            
        
        ret[s.name]={
            data:CSV.serialize(records),
            width: w,
            format: {
                autofilter:s.autofilter, 
                cols:s.cols, 
                freeze:s.freeze, 
                merges:s.merges, 
                validations:s.validations 
            }
        }
    }
    return ret;
}





var opts={
    showToolbar: true,
    showGrid: true,
    showBottomBar: true,
    extendToolbar: {
        left:[]
    }
};

if(allowSave) {
    var saveIcon = 'data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBzdGFuZGFsb25lPSJubyI/PjwhRE9DVFlQRSBzdmcgUFVCTElDICItLy9XM0MvL0RURCBTVkcgMS4xLy9FTiIgImh0dHA6Ly93d3cudzMub3JnL0dyYXBoaWNzL1NWRy8xLjEvRFREL3N2ZzExLmR0ZCI+PHN2ZyB0PSIxNTc3MTc3MDkyOTg4IiBjbGFzcz0iaWNvbiIgdmlld0JveD0iMCAwIDEwMjQgMTAyNCIgdmVyc2lvbj0iMS4xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHAtaWQ9IjI2NzgiIHdpZHRoPSIxOCIgaGVpZ2h0PSIxOCIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiPjxkZWZzPjxzdHlsZSB0eXBlPSJ0ZXh0L2NzcyI+PC9zdHlsZT48L2RlZnM+PHBhdGggZD0iTTIxMy4zMzMzMzMgMTI4aDU5Ny4zMzMzMzRhODUuMzMzMzMzIDg1LjMzMzMzMyAwIDAgMSA4NS4zMzMzMzMgODUuMzMzMzMzdjU5Ny4zMzMzMzRhODUuMzMzMzMzIDg1LjMzMzMzMyAwIDAgMS04NS4zMzMzMzMgODUuMzMzMzMzSDIxMy4zMzMzMzNhODUuMzMzMzMzIDg1LjMzMzMzMyAwIDAgMS04NS4zMzMzMzMtODUuMzMzMzMzVjIxMy4zMzMzMzNhODUuMzMzMzMzIDg1LjMzMzMzMyAwIDAgMSA4NS4zMzMzMzMtODUuMzMzMzMzeiBtMzY2LjkzMzMzNCAxMjhoMzQuMTMzMzMzYTI1LjYgMjUuNiAwIDAgMSAyNS42IDI1LjZ2MTE5LjQ2NjY2N2EyNS42IDI1LjYgMCAwIDEtMjUuNiAyNS42aC0zNC4xMzMzMzNhMjUuNiAyNS42IDAgMCAxLTI1LjYtMjUuNlYyODEuNmEyNS42IDI1LjYgMCAwIDEgMjUuNi0yNS42ek0yMTMuMzMzMzMzIDIxMy4zMzMzMzN2NTk3LjMzMzMzNGg1OTcuMzMzMzM0VjIxMy4zMzMzMzNIMjEzLjMzMzMzM3ogbTEyOCAwdjI1NmgzNDEuMzMzMzM0VjIxMy4zMzMzMzNoODUuMzMzMzMzdjI5OC42NjY2NjdhNDIuNjY2NjY3IDQyLjY2NjY2NyAwIDAgMS00Mi42NjY2NjcgNDIuNjY2NjY3SDI5OC42NjY2NjdhNDIuNjY2NjY3IDQyLjY2NjY2NyAwIDAgMS00Mi42NjY2NjctNDIuNjY2NjY3VjIxMy4zMzMzMzNoODUuMzMzMzMzek0yNTYgMjEzLjMzMzMzM2g4NS4zMzMzMzMtODUuMzMzMzMzeiBtNDI2LjY2NjY2NyAwaDg1LjMzMzMzMy04NS4zMzMzMzN6IG0wIDU5Ny4zMzMzMzR2LTEyOEgzNDEuMzMzMzMzdjEyOEgyNTZ2LTE3MC42NjY2NjdhNDIuNjY2NjY3IDQyLjY2NjY2NyAwIDAgMSA0Mi42NjY2NjctNDIuNjY2NjY3aDQyNi42NjY2NjZhNDIuNjY2NjY3IDQyLjY2NjY2NyAwIDAgMSA0Mi42NjY2NjcgNDIuNjY2NjY3djE3MC42NjY2NjdoLTg1LjMzMzMzM3ogbTg1LjMzMzMzMyAwaC04NS4zMzMzMzMgODUuMzMzMzMzek0zNDEuMzMzMzMzIDgxMC42NjY2NjdIMjU2aDg1LjMzMzMzM3oiIHAtaWQ9IjI2NzkiIGZpbGw9IiMyYzJjMmMiPjwvcGF0aD48L3N2Zz4='
    opts.extendToolbar.left.push(
        {
          tip: 'Save',
          icon: saveIcon,
          onClick: (data, sheet) => {
            postData(serialize(xs.getData()));
          }
        }
    );
}

var xs=x_spreadsheet('#xspreadsheet', opts);
var dirty=false;
xs.change(data => {
    message("<span style='color:red'>Unsaved</span>");
    dirty=true;
});
loadData(xs, csvdata)

// Save with control S
window.onkeydown=(function(event) { 
    if ((event.ctrlKey || event.metaKey) && (String.fromCharCode(event.which).toLowerCase() == 's')) {
            event.preventDefault();
            postData(serialize(xs.getData()));
    }
});

window.onbeforeunload = function(e){
    if(dirty) {
        // Cancel the event
        e.preventDefault(); // If you prevent default behavior in Mozilla Firefox prompt will always be shown
        // Chrome requires returnValue to be set
        e.returnValue='';
    }else{
        delete e['returnValue'];
        return;
    }
};
