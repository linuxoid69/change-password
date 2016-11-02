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
    %if ok == '0':
      <form method="post">
        <label for="email">Почтовый ящик</label>
        <input id="email" name="email" value="{{ get('email', '') }}" type="email" required autofocus>
	    <img src="{{path_captcha}}">
	    <label for="captcha">Код</label>
	    <input id="captcha" name="captcha" type='text' required>
        <button type="submit">Отправить пароль</button></br>
      	<a id='back' href='/'>&lt; Назад</a>

      </form>
      %end
        %if ok != '0':
        <!--<a id='mainpage' href="/">На главную</a>-->
        %end
      <div class="alerts">
        %for type, text in get('alerts', []):
          <div class="alert {{ type }}">{{ text }}</div>
        %end
      </div>
    </main>
  </body>
</html>
