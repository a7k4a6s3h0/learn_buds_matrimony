// Select the button by its ID
const sendBtn = document.getElementById('send-btn');
var WEB_PROTOCOL = window.location.protocol;  // Use window.location.protocol for 'http:' or 'https:'
var HOST_URL = window.location.host;  // Use window.location.host for 'hostname:port'
var WS_START = 'ws://';  // Default to WebSocket (ws://)
var CHAT_URL = '/ws/chat/aebb407b-842a/';  // Ensure proper URL format

// Check if the protocol is HTTPS, then use 'wss://'
if (WEB_PROTOCOL === 'https:') {
    WS_START = 'wss://';  // Secure WebSocket (wss://)
}

// Create WebSocket connection
const socket = new WebSocket(WS_START + HOST_URL + CHAT_URL);

// When the WebSocket connection is open
socket.onopen = function() {
    console.log("WebSocket connection established!");
};

// Add a 'click' event listener to the button
sendBtn.addEventListener('click', function() {
    // Get the text input value
    var input_field = document.getElementById('input_message');
    let text = input_field.value;
    console.log("Send button clicked!", text);

    // Send the message to the server if WebSocket is open
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ 'message': text }));
        input_field.value = ''
    } else {
        alert('WebSocket is not open. Ready state: ')
        console.log('WebSocket is not open. Ready state: ', socket.readyState);
    }
});

// On receiving a message from the server
socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Message from server: ', data);

    if (data.Warning_Message){
        alert(data.Warning_Message)
    }
    else{
        const chatLog = document.getElementById('chat-log');
        const chatMessage = document.createElement('div');

        // Depending on the message type (left or right), add the appropriate classes
        if (data.isSender) {
            // Message sent by the user (right-aligned)
            chatMessage.innerHTML = `
                <div class="row text-white pt-3">
                    <div class="col-auto chat-message-left">
                        <p>${data.timestamp}</p>
                        <p>${data.username}: ${data.message}</p>
                    </div>
                </div>
            `;
        } else {
            // Message received from another user (left-aligned)
            chatMessage.innerHTML = `
                <div class="row text-white pt-3 justify-content-end">
                    <div class="col-auto chat-message-right">
                        <p>${data.timestamp}</p>
                        <p>${data.username}: ${data.message}</p>
                    </div>
                </div>

            `;
        }

        // Append the message to the chat log
        chatLog.appendChild(chatMessage);

        // Scroll to the bottom of the chat log to show the latest message
        chatLog.scrollTop = chatLog.scrollHeight;

    }


};

socket.onclose = function(event) {
    if (event.code === 4001) {
        console.log('Disconnected: ', event.reason);
    } else {
        console.log('Disconnected: ', event);
    }
};


// Optionally handle errors
socket.onerror = function(error) {
    console.error('WebSocket error: ', error);
};
