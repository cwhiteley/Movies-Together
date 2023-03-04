const host_chat = document.getElementById("host_chat").textContent;
const port_chat = document.getElementById("port_chat").textContent;
const path_chat_socket = document.getElementById("path_chat_socket").textContent;
const socket_chat = new WebSocket("ws://"+host_chat+':'+ port_chat + path_chat_socket);
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
