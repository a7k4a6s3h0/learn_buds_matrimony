// Select the button by its ID
const sendBtn = document.getElementById('send-btn');

// Use window.location for WebSocket URL
const WEB_PROTOCOL = window.location.protocol;  // 'http:' or 'https:'
const HOST_URL = window.location.host;          // 'hostname:port'
const CHAT_URL = "/ws/chat/aebb407b-842a/";    // Ensure proper URL format

// Set WebSocket protocol based on HTTPS
const WS_START = WEB_PROTOCOL === 'https:' ? 'wss://' : 'ws://'; // Default to WebSocket (ws://)

// Create WebSocket connection
const socket = new WebSocket(`${WS_START}${HOST_URL}${CHAT_URL}`);

// When the WebSocket connection is open
socket.onopen = function() {
    console.log("WebSocket connection established!");
};

// Add a 'click' event listener to the button
sendBtn.addEventListener('click', function() {
    // Get the text input value
    const inputField = document.getElementById('input_message');
    const text = inputField.value.trim();  // Trim whitespace
    console.log("Send button clicked!", text);

    // Send the message to the server if WebSocket is open
    if (socket.readyState === WebSocket.OPEN) {
        if (text) {  // Check if the message is not empty
            socket.send(JSON.stringify({ 'message': text }));
            inputField.value = '';  // Clear input field
        } else {
            alert('Please enter a message to send.');
        }
    } else {
        alert('WebSocket is not open. Ready state: ' + socket.readyState);
        console.log('WebSocket is not open. Ready state: ', socket.readyState);
    }
});

// On receiving a message from the server
socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Message from server: ', data);

    if (data.Warning_Message) {
        alert(data.Warning_Message);
    } else if (data.history_message) {
        // Process chat history
        displayChatHistory(data.history_message);
    }
    else if (data.user_status){
        const result = data.user_status
        console.log(result.username)
        const name = document.getElementById('user-name');
        name.innerHTML = result.username
        const online_status = document.getElementById('status');
        online_status.innerHTML = result.is_online
    }
    else {
        // Display the chat message
        displayChatMessage(data);
    }
};

// Function to display chat history
function displayChatHistory(history) {
    const chatLog = document.getElementById('chat-log');

    history.forEach(chatData => {
        const chatMessage = document.createElement('div');
        chatMessage.innerHTML = `
            <div class="row text-white pt-3 ${
              chatData.isSender ? "" : "justify-content-end"
            }">
                <div class="col-auto ${
                  chatData.isSender ? "chat-message-left" : "chat-message-right"
                }">
                    <p class="float-end" style="font-size: x-small;">${
                      chatData.timestamp
                    }</p>
                    <p class='fs-5'> ${chatData.message}</p>
                </div>
            </div>
        `;
        chatLog.appendChild(chatMessage);
    });

    // Scroll to the bottom of the chat log to show the latest messages
    chatLog.scrollTop = chatLog.scrollHeight;
}

// Function to display a single chat message
function displayChatMessage(data) {
    const chatLog = document.getElementById('chat-log');
    const chatMessage = document.createElement('div');

    chatMessage.innerHTML = `
        <div class="row text-white pt-3 ${
          data.isSender ? "" : "justify-content-end"
        }">
            <div class="col-auto ${
              data.isSender ? "chat-message-left" : "chat-message-right"
            }">
                <p class="float-end" style="font-size: x-small;">${
                  data.timestamp
                }</p>
                <p class='fs-5'>${data.message}</p>
            </div>
        </div>
    `;

    chatLog.appendChild(chatMessage);

    // Scroll to the bottom of the chat log to show the latest message
    chatLog.scrollTop = chatLog.scrollHeight;
}

// Handle WebSocket close event
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
