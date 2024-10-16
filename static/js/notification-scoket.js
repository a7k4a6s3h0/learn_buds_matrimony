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

    // Create a new alert dynamically
    const alertContainer = document.getElementById('notification-container');
    
    const alertDiv = document.createElement('div');
    alertDiv.classList.add('row');
    
    const colDiv = document.createElement('div');
    colDiv.classList.add('col');
    
    const alertMessage = document.createElement('div');
    alertMessage.classList.add('alert', 'alert-dismissible', 'fade', 'show', 'notifaction-alert', 'd-flex', 'flex-row', 'align-items-center');
    alertMessage.setAttribute('role', 'alert');

    // Icon element
    const icon = document.createElement('i');
    icon.classList.add('fa-solid', 'fa-bell', 'fa-xl', 'text-success');

    // Text content div
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('ms-3');

    // Message content
    const messageText = document.createElement('small');
    messageText.classList.add('d-block');
    messageText.innerText = data.title || data.description; // Use title or description based on preference

    // Timestamp
    const timeText = document.createElement('small');
    timeText.classList.add('text-white-50', 'd-block');
    timeText.innerText = new Date(data.timestamp).toLocaleString(); // Convert timestamp to readable format

    // Close button
    const closeButton = document.createElement('button');
    closeButton.classList.add('btn-close');
    closeButton.setAttribute('data-bs-dismiss', 'alert');
    closeButton.setAttribute('aria-label', 'Close');
    closeButton.setAttribute('style', 'filter: invert(100%)');

    // Append message and time to the messageDiv
    messageDiv.appendChild(messageText);
    messageDiv.appendChild(timeText);

    // Append elements to the alertMessage
    alertMessage.appendChild(icon);
    alertMessage.appendChild(messageDiv);
    alertMessage.appendChild(closeButton);

    // Append the alertMessage to colDiv
    colDiv.appendChild(alertMessage);

    // Append colDiv to alertDiv
    alertDiv.appendChild(colDiv);

    // Finally, append alertDiv to the container
    alertContainer.appendChild(alertDiv);
};


// When the WebSocket connection is closed
socket.onclose = function() {
     console.log("WebSocket connection closed!");
};

// When the WebSocket connection encounters an error
socket.onerror = function(error) {
     console.log("WebSocket connection error:", error);
};
