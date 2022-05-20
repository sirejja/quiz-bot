# Quiz bot for Telegram and VK Groups
 

## Features:
* Bot for [Telegram](https://t.me/squizzy_bot)
* Bot for [VK Group](https://vk.com/public213359082)
* Telegram bot for logging
* Answer buttons
* Script for reading n parsing questions
* Redis db for questions, answers, users




## Env vars:

* VK_BOT_TOKEN=<API token VK group\>
* TG_BOT_TOKEN=<[main telegram bot token](https://t.me/botfather)>
* TG_LOGS_TOKEN=<[telegram token for logs](https://t.me/botfather)>.
* TG_CHAT_ID=<bot's admin id>
* REDIS_HOST= <redis host\>
* REDIS_PORT= <redis port\>
* REDIS_PASSWORD= <redis passwd\>


## Questions parsing
1. Place parsing files with data into 'questions\questions_data'. Format:
```
Чемпионат:
text

Тур:
text

Вопрос 1:
text

Ответ:
text

Вопрос 2:
text
```
2. Run script with full or empty params.
```
python questions_data_processing.py -p "questions/questions.json" -e "KOI8-R"

or 

python questions_data_processing.py
```

Output file format:
```
'question':
'answer':
'comment':
```


## Preparations for using VK group bot
1. Create group
2. Add API key with sending messages permission.
3. Enable messages in group.


## Run


1. git clone <repository url\>
2. Create virtual environment

```
python -m venv .venv
```

3. Activate venv

```
.venv\scripts\activate
```

4. Install requirements

```
pip install -r requirements.txt
```

5. Start TG bot on local machine

```
python tg_bot.py
```

## Heroku deploy
1. Start new project
2. Connect to GitHub
3. Add env vars in project's settings
4. Deploy your app
5. Enjoy
