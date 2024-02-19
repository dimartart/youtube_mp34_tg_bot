# the structure for dict with all languages {"key_phrase":{"RU":"translation", "ENG":"translation"}}

languages = {'start message': {'RU': 'Приветствую, этот бот предназначен для скачивания видео с ютуб.'
                                     ' Вы можете выбрать скачать видео или аудио в меню справа.'
                                     'Видео не должно превышать размер 50 мегабайтов, это ограничение телеграмма.'
                                     ' Чтобы начать вставьте ссылку на видео с ютуба',
                               'ENG': 'Hello, this bot is about downloading videos from youtube by using url. '
                                      'You can choose to download the video or audio format in buttons menu. '
                                      'Video should not be higher than 50 megabyte, because of telegram restriction. '
                                      'To start just send the link from youtube'},
             'Choose language': {'RU': 'Выберите язык', 'ENG': 'Choose language'},
             'russian': {'RU': 'русский 🇷🇺', 'ENG': 'russian 🇷🇺'},
             'english': {'RU': 'английский 🇺🇲', 'ENG': 'english 🇺🇲'},
             'you will be downloading': {'RU': 'Теперь вы будете скачивать', 'ENG': 'Now you will be downloading'},
             'link validation': {'RU': '⌛ Проверка ссылки', 'ENG': '⌛ Link validation'},
             'not valid': {'RU': 'Неверная ссылка ❌', 'ENG': 'Link is not valid ❌'},
             'higher than 50mb': {'RU': 'Файл весит больше 50 мегабайтов ❌', 'ENG': 'File is higher than 50 megabyte ❌'},
             'file is downloading': {'RU': '⌛ Файл скачивается', 'ENG': '⌛ File is downloading'},
             'file is uploading': {'RU': '⌛ Файл загружается в телеграм', 'ENG': '⌛ File is uploading to telegram'},
             'downloading video': {'RU': 'Скачать видео 🎥', 'ENG': 'Downloading video 🎥'},
             'downloading audio': {'RU': 'Скачать аудио 🎵', 'ENG': 'Downloading audio 🎵'}}


user_state_languages = {} # user_id: "RU"/"ENG"


# language func, it accepts key phrase, then find user's id in user_state_languages dictionary
# and then base on user's language return the translation from RU dict or ENG dict
def lf(key_phrase: str, user_id: int) -> str:
    # by default all users have english language
    language = user_state_languages.setdefault(user_id, "ENG") # language = "RU" or "ENG"
    if language == "ENG":
        return languages[key_phrase]["ENG"]
    else:
        return languages[key_phrase]["RU"]


def change_user_language(language: str, user_id: int) -> None:
    user_state_languages[user_id] = language


