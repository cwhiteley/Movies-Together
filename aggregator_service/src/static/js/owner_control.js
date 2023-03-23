// const owner_user = document.getElementById("owner_user").textContent;
// if (x = Забронирована) $('botton').css({display: 'none'});
const control_host = document.getElementById("control_host").textContent;
const control_port = document.getElementById("control_port").textContent;
const path_control_socket = document.getElementById("path_control_socket").textContent;
const socket_control = new WebSocket(url="ws://"+control_host+':'+ control_port + path_control_socket+'?'+document.cookie);

socket_control.onmessage = function(event) {
    var data = JSON.parse(event.data)
    if (data["token_value"]){
        document.cookie = `${data["token_key"]}=${data["token_value"]};expires=300`;
    }
    if (data["command"] == 'Delete user'){
        location.reload()
    }
    var messages = document.getElementById('messages')
    var message = document.createElement('div')
    var content = document.createTextNode(data["message"])
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
