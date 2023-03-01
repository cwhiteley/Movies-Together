Генерация ссылки для совместного просмотра.

### 1. Определяем ручку для создания ссылки.

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from uuid import uuid4

app = FastAPI()


@app.get("/watch/{movie_id}")
def watch_movie(movie_id: str, session_id: str = str(uuid4())):
    return HTMLResponse(f"""
        <h1>Movie ID: {movie_id}</h1>
        <h2>Session ID: {session_id}</h2>
        <p>Share this link with your friends to watch the movie together:</p>
        <a href="/join/{movie_id}/{session_id}">Join the session</a>
    """)
```

Затем сохраняем:

```python
sessions = {}
sessions[session_id] = {
    "movie_id": movie_id,
    "connections": set()
}
```

Далее можно будет проверять, соответствует ли movie_id сессии, а также контролировать количество подключений.

### 2. Работа с сессиями.

Session_id будет передаваться на бэкэнд с каждым сообщением клиента.
Бэкэнд будет проверять, что сессия существует, а также, что movie_id совпадает с movie_id сессии, затем отправлять ответ
клиенту.



