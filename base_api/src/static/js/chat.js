const host = document.getElementById("host").textContent;
const port = document.getElementById("port").textContent;
const path_chat_socket = document.getElementById("path_chat_socket").textContent;
const socket_chat = new WebSocket("ws://"+host+':'+port+path_chat_socket);
const randomUserName = Math.random().toString(36).substring(7);

socket_chat.onmessage = function(event) {
    var messages = document.getElementById('messages')
    var message = document.createElement('div')
    var content = document.createTextNode(event.data)
    message.appendChild(content)
    messages.appendChild(message)
};
function sendMessage(event) {
    var input = document.getElementById("messageText")
    const message = {
        data: input.value,
        user: randomUserName
    };
    socket_chat.send(JSON.stringify(message))
    input.value = ''
    event.preventDefault()
}
