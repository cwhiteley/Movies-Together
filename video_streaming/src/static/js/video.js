const player = videojs('my-video');
const socket = new WebSocket("ws://localhost:8000/ws");
const randomUserName = Math.random().toString(36).substring(7);
let lastTime = player.currentTime();
let paused = true;
socket.onmessage = function (event) {
    const eventData = JSON.parse(event.data);
    const eventName = eventData.event_name;
    const user = eventData.user;

    if (user !== randomUserName) {
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
            if (currentTimeInt !== eventTimeInt) {
                player.currentTime(eventData.time);
            }
        }
    }
};

player.on('pause', function () {
    const data = {
        event_name: 'pause',
        user: randomUserName
    };
    if (!paused) {
        socket.send(JSON.stringify(data));
        paused = true;
    }

});

player.on('play', function () {
    const data = {
        event_name: 'play',
        user: randomUserName
    };
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
            user: randomUserName
        };
        socket.send(JSON.stringify(data))
    }
});
