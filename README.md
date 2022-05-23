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


## Questions processing
1. Startup params

* Options for tg_bot.py, vk_bot.py, questions_data_processing.py scripts:
  * Default path to files with questions: 'questions/questions_data'.
You can change it with '-q' or '--questpath' option.
  * Default encoding of files with questions: 'KOI8-R'.
You can change it with '-e' or '--encoding' option.


* Specific option for questions_data_processing.py is destination of json with parsed questions:
  * Default destination path: 'questions/questions.json'.
You can change it with '-d' or '--destpath' option.

2. Place parsing files with data into 'questions\questions_data' or custom path if it specified with option while running script. Default format:
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

For another format you should change questions_data_processing.match_data regex patterns.

Output file format for questions_data_processing.py:
```
{
    'title_1':
        {
            'question': text,
            'answer': text,
            'comment': text
        },
    'title_2': {...},
}
```


## Preparations for using VK group bot
1. Create group
2. Add API key with sending messages permission.
3. Enable messages in group.
## Preparations for using TG chat bot
1. [Create bot for project](https://telegram.me/BotFather)
2. Add TG_BOT_TOKEN to env
## Preparations for using TG logging bot
1. [Create bot for project](https://telegram.me/BotFather)
2. Add TG_LOGS_TOKEN to env

## Run

0. Don't forget to place questions files to customized/default path.
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

5. Start bot on local machine if default params suit you

```
python tg_bot.py
```
or 

```
python vk_bot.py
```

## Heroku deploy
1. Start new project
2. Connect to GitHub
3. Add env vars in project's settings
4. Deploy your app
5. Enjoy
