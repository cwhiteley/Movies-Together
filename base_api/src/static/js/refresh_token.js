async function refreshAccessToken() {
    const refreshCookie = document.cookie.split('; ').find(row => row.startsWith('refresh_token='));
    const refreshToken = refreshCookie ? refreshCookie.split('=')[1] : null;

    console.log(refreshToken)
    const response = await fetch(`http://127.0.0.1:80/api/refresh`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${refreshToken}` // Add this line to include the refresh token in the header
        },
    });

    const data = await response.json();
    console.log(data);

    if (response.ok) {
        const newAccessToken = data.access_token;
        const newRefreshToken = data.refresh_token;
        const d = new Date();
        const d2 = new Date();

        d.setTime(d.getTime() + (100 * 60 * 1000));
        d2.setTime(d2.getTime() + (1000 * 60 * 1000));

        document.cookie = `refresh_token=${newRefreshToken};expires=${d2.toUTCString()}`;
        document.cookie = `access_token=${newAccessToken};expires=${d.toUTCString()}`;

        console.log('Access token refreshed: ' + newAccessToken);
    } else {
        console.error('Access token refresh failed.');
    }
}

setInterval(refreshAccessToken, (20 * 60) * 1000);
