// Use window.location for WebSocket URL
const WEB_PROTOCOL = window.location.protocol;  // 'http:' or 'https:'
const HOST_URL = window.location.host;          // 'hostname:port'
const CHAT_URL = "/ws/notification/aebb407b-842a/";    // Ensure proper URL format

// Set WebSocket protocol based on HTTPS
const WS_START = WEB_PROTOCOL === 'https:' ? 'wss://' : 'ws://'; // Default to WebSocket (ws://)

// Create WebSocket connection
const socket = new WebSocket(`${WS_START}${HOST_URL}${CHAT_URL}`);

// When the WebSocket connection is open
socket.onopen = function() {
    console.log("WebSocket connection established!");
    socket.send(JSON.stringify({ 'message': 'hi from js' }));
};

// On receiving a message from the server
socket.onmessage = function(event) {
     const data = JSON.parse(event.data);
     console.log('Message from server: ', data);
};

// When the WebSocket connection is closed
socket.onclose = function() {
     console.log("WebSocket connection closed!");
};

// When the WebSocket connection encounters an error
socket.onerror = function(error) {
     console.log("WebSocket connection error:", error);
};
