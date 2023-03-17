// const owner_user = document.getElementById("owner_user").textContent;
// if (x = Забронирована) $('botton').css({display: 'none'});
const control_host = document.getElementById("control_host").textContent;
const control_port = document.getElementById("control_port").textContent;
const path_control_socket = document.getElementById("path_control_socket").textContent;
const socket_control = new WebSocket("ws://"+control_host+':'+ control_port + path_control_socket);

socket_control.onmessage = function(event) {
    if (event.data == 'close channel'){
        location.reload()
    }
    var messages = document.getElementById('messages')
    var message = document.createElement('div')
    var content = document.createTextNode(event.data)
    message.appendChild(content)
    messages.appendChild(message)
};
function executeControl(event) {
    var command = document.getElementById("control_command")
    var user_name = document.getElementById("name_client")
    const message = {
        command: command.options[command.selectedIndex].text,
        user_name: user_name.value
    };
    socket_control.send(JSON.stringify(message))
    event.preventDefault()
}
