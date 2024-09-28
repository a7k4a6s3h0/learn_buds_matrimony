var WEB_PROTOCOL = window.location.protocol;  // Use window.location.protocol for 'http:' or 'https:'
var HOST_URL = window.location.host;  // Use window.location.host for 'hostname:port'
var WS_START = 'ws://';  // Default to WebSocket (ws://)
var CHAT_URL = '/ws/chat/username/';  // Ensure proper URL format

// Check if the protocol is HTTPS, then use 'wss://'
if (WEB_PROTOCOL === 'https:') {
    WS_START = 'wss://';  // Secure WebSocket (wss://)
}

// Create WebSocket connection
const socket = new WebSocket(WS_START + HOST_URL + CHAT_URL);

// On receiving a message
socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Message from server: ', data.message);
};

// When the connection is open, send a message to the server
socket.onopen = function() {
    socket.send(JSON.stringify({ 'message': 'Hello Server!' }));
};

// Optionally handle connection close
socket.onclose = function(event) {
    console.log('Connection closed', event);
};

// Optionally handle errors
socket.onerror = function(error) {
    console.error('WebSocket error: ', error);
};
