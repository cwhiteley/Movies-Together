const chat_host = document.getElementById("chat_host").textContent;
const chat_port = document.getElementById("chat_port").textContent;
const path_chat_socket = document.getElementById("path_chat_socket").textContent;
const socket_chat = new WebSocket("ws://"+chat_host+':'+ chat_port + path_chat_socket);
const randomUserName_chat = Math.random().toString(36).substring(7);

socket_chat.onmessage = function(event) {
    var messages = document.getElementById('messages')
    var message = document.createElement('div')
    var content = document.createTextNode(event.data)
    message.appendChild(content)
    messages.appendChild(message)
};
function sendMessageChat(event) {
    var input = document.getElementById("messageText")
    const message = {
        data: input.value,
        user: randomUserName_chat
    };
    socket_chat.send(JSON.stringify(message))
    input.value = ''
    event.preventDefault()
}
