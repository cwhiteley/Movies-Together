const owner_user = document.getElementById("owner_user").textContent;
var messages = document.getElementById('messages')
if (x = Забронирована) $('botton').css({display: 'none'});

function executeControl(event) {
    var input = document.getElementById("messageText")
    const message = {
        data: input.value,
        user: randomUserName_chat
    };
    socket_chat.send(JSON.stringify(message))
    input.value = ''
    event.preventDefault()
}