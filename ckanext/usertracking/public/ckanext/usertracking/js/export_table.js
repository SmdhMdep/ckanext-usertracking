/* JS adapted from:
 https://www.geeksforgeeks.org/how-to-export-html-table-to-csv-using-javascript/
*/

function tableToCSV(table_id) {

    // Variable to store the final csv data
    var csv_data = [];
    
    // Get each row data of the specified table
    var table = document.querySelector("table[id='"+table_id+"']");
    var rows = table.getElementsByTagName('tr');
    for (var i = 0; i < rows.length; i++) {
        
        // Get each column data
        var cols = rows[i].querySelectorAll('td,th');
        
        // Stores each csv row data
        var csvrow = [];
        for (var j = 0; j < cols.length; j++) {

            // Get the text data of each cell
            // of a row and push it to csvrow
            csvrow.push(cols[j].innerHTML);
        }
        
        // Combine each column value with comma
        csv_data.push(csvrow.join(","));
    }
    
    // Combine each row data with new line character
    csv_data = csv_data.join('\n');
    
    // Call this function to download csv file
    downloadCSVFile(csv_data, table_id.replace("-form","-table ")+Date().toLocaleString());

}
    
function downloadCSVFile(csv_data, csv_name) {
    
    // Create CSV file object and feed
    // our csv_data into it
    CSVFile = new Blob([csv_data], {
        type: "text/csv"
    });
    
    // Create to temporary link to initiate
    // download process
    var temp_link = document.createElement('a');
    
    // Download csv file
    temp_link.download = csv_name;
    var url = window.URL.createObjectURL(CSVFile);
    temp_link.href = url;
    
    // This link should not be displayed
    temp_link.style.display = "none";
    document.body.appendChild(temp_link);
    
    // Automatically click the link to
    // trigger download
    temp_link.click();
    document.body.removeChild(temp_link);
}