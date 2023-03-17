const player = videojs('my-video');
const video_host = document.getElementById("video_host").textContent;
const video_port = document.getElementById("video_port").textContent;
const path_video_socket = document.getElementById("path_video_socket").textContent;
const socket = new WebSocket("ws://" + video_host + ":" + video_port + path_video_socket);
const currentUsername = document.getElementById("username").textContent;
let lastTime = player.currentTime();
let paused = true;
socket.onmessage = function (event) {
    const eventData = JSON.parse(event.data);
    const eventName = eventData.event_name;
    const user = eventData.user;
    if (user !== currentUsername) {
        if (eventName === "play" && paused) {
            player.play();
            paused = false;
            console.log('play');

        } else if (eventName === "pause" && !paused) {
            player.pause();
            paused = true;
            console.log('pause');

        } else if (eventName === "change_time") {
            let currentTimeInt = parseInt(player.currentTime());
            let eventTimeInt = parseInt(eventData.time);
            console.log('Change time')
            if (Math.abs(currentTimeInt - eventTimeInt) > 1) {
                player.currentTime(eventData.time);
            }
        }
    }
};

player.on('pause', function () {
    const data = {
        event_name: 'pause',
        time: player.currentTime(),
        user: currentUsername
    };
    if (!paused) {
        socket.send(JSON.stringify(data));
        paused = true;
    }

});

player.on('play', function () {
    const data = {
        event_name: 'play',
        time: player.currentTime(),
        user: currentUsername
    };
    console.log(data)

    if (paused) {
        socket.send(JSON.stringify(data));
        paused = false;

    }
});

player.on('seeked', function () {
    const currentTime = player.currentTime();

    if (currentTime !== lastTime) {
        lastTime = currentTime;
        const data = {
            time: currentTime,
            event_name: 'change_time',
            user: currentUsername
        };
        socket.send(JSON.stringify(data))
    }
});