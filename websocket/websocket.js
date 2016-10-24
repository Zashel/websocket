// Messages parser
function parse_data(data) {
    console.log(data)
    if (data.signal === "ping") {
        webSocket.send(signal("pong"))
    } else if (data.signal === "message") {
        console.log(data.text)
    } else if (data.signal === "bye") {
        console.log("Connection close as requested by server")
        webSocket.close()
    }
};

// Initialize WebSocket
function initWebSocket(direction, port, secure_connection, protocols=[], parser=parse_data) {
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
            parser(received)
        };
        webSocket.onclose = function() {
            send_bye()
        };
    }
    else {
        alert("Browser Not Supported");
    };
};

function get_now() {
    var now = new Date()
    var nowStr = now.getFullYear()+"-"+
             now.getMonth()+"-"+
             now.getDate()+" "+
             now.getHours()+":"+
             now.getMinutes()+":"+
             now.getSeconds();
    return nowStr
}

function signal(identifier) {
    if (identifier === "pong") {
        return JSON.stringify({
                "signal": "pong", 
                "date": get_now()
                })
    };
}

function send_bye(){
    webSocket.send(
        JSON.stringify({
            "signal": "bye",
            "date": get_now(),
        })
    );
}

function send_message(to, text) {
    webSocket.send(
        JSON.stringify({
            "signal": "message",
            "date": get_now(),
            "to": to,
            "text": text
        })
    );
};
