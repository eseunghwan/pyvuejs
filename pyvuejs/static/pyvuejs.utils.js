
function format_date(datetime) {
    var year = datetime.getFullYear().toString();
    var month = ("0" + (datetime.getMonth() + 1)).slice(-2);
    var date = ("0" + datetime.getDate()).slice(-2);
    var hour = ("0" + datetime.getHours()).slice(-2);
    var minute = ("0" + datetime.getMinutes()).slice(-2);
    var second = ("0" + datetime.getSeconds()).slice(-2);

    return `${year}-${month}-${date}T${hour}:${minute}:${second}Z`;
}

function log(level, content) {
    console.log(`[pyvuejs | ${format_date(new Date())}] ${level.toUpperCase()}: ${content}`);
}
