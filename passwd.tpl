<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="robots" content="noindex, nofollow">

    <title>{{ page_title }}</title>

    <link rel="stylesheet" href="{{ url('static', filename='style.css') }}">
</head>

<body>
<main>
    <h1>{{ page_title }}</h1>

    <form method="post">
        <label for="passwd_1">Новый пароль</label>
        <input id="passwd_1" name="passwd_1" type='password' required>
        <label for="passwd_2">Еще раз</label>
        <input id="passwd_2" name="passwd_2" type='password' required>
        <button type="submit">Сменить пароль</button>
        </br>
        <a id='back' href='/'>&lt; Назад</a>
    </form>

    <div class="alerts">
        %for type, text in get('alerts', []):
        <div class="alert {{ type }}">{{ text }}</div>
        %end
    </div>
</main>
</body>
</html>
