var xs=x_spreadsheet('#xspreadsheet');


function parseCSV(csv) {
    var records = CSV.parse(csv, {header: false});
    
    var ret={len: records.length+100}

    for (var i=0; i<records.length; i++) {
        var data = records[i];
        var cells={}

        for (var j=0; j<data.length; j++) {
            cells[j]={text: data[j]}
        }
        ret[i]={cells: cells}
    }
    return ret;
}

var data=[]

for(var key in csvdata) {
    data.push({name: key, rows: parseCSV(csvdata[key])})
}

xs.loadData(
    data
);
