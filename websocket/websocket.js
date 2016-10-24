// Messages parser
function parse_data(data) {
    if (data.signal === "ping"):
        webSocket.send(signal("pong"))
};

// Initialize WebSocket
function initWebSocket(direction, port, secure_connection, protocols=[]) {
    // Getting the connection String for WebSocket
    connString = "://"+direction+":"+port;
    if (secure_connection === true) {
        connString = "wss"+connString
    }
    else {
        connString = "ws"+connString
    };

    // Test compatibility
    if ("WebSocket" in window) {
        // Set the WebSocket
        webSocket = new WebSocket(connString);  // No Protocols by now. TODO

        // Set the main handlers
        webSocket.onopen = function() {
            console.log("Connected");
        };
        webSocket.onmessage = function(event) {
            var received = JSON.parse(event.data);
            parse_data(received)
        };
        webSocket.onclose = function() {
            // Send signal Bye. TODO
        };
    }
    else {
        alert("Browser Not Supported");
    };
}

function signal(identifier) {
    var now = Date()
    nowStr = now.getFullYear()+"-"+
             now.getMonth()+"-"+
             now.getDate()+" "+
             now.getHours()+":"+
             now.getMinutes()+":"+
             now.getSeconds()
    if identifier === "pong" {
        return JSON.dumps({
                "signal": "pong", 
                "date": nowStr
                })
    };
}
