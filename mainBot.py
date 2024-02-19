import asyncio

from languages import lf, change_user_language, languages
from youtube import *
from dotenv import find_dotenv, load_dotenv

from aiogram import Bot, Dispatcher, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram import F

load_dotenv(find_dotenv())
token = os.getenv("TOKEN")

dp = Dispatcher()
main_router = Router(name=__name__)
dp.include_router(main_router)

bot_commands = [
    BotCommand(command="start", description="information about the bot/информация о боте"),
    BotCommand(command="language", description="set language/изменить язык ")
]
# each user can choose to download video or audio format of video from youtube
user_states_download_mode = {}  # user_id: "video"/"audio"
# all phrases that we need to handle to change downloading format
# the structure for dict languages {"key_phrase":{"RU":"translation", "ENG":"translation"}}
change_mode_phrases_video = [languages["downloading video"][key] for key in languages["downloading video"]]
change_mode_phrases_audio = [languages["downloading audio"][key] for key in languages["downloading audio"]]


# each time when user will be in process of downloading something, we will change his state,
# so bot will ignore all next messages from user during downloading
class DownloadStatus(StatesGroup):
    downloading = State()


def set_keyboard(vbt="Downloading video 🎥", abt="Downloading audio 🎵") -> ReplyKeyboardMarkup:
    button_video, button_audio = KeyboardButton(text=vbt), KeyboardButton(text=abt)
    first_buttons_row = [button_video, button_audio]
    keyboard = ReplyKeyboardMarkup(keyboard=[first_buttons_row], resize_keyboard=True)
    return keyboard


@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    user_id = message.from_user.id
    await message.answer(lf("start message", user_id), # lf - custom function to understand on which language
                         reply_markup=set_keyboard())  # we should send messages for each user


# user can choose russian or english language
@dp.message(Command('language'))
async def set_language(message: types.Message):
    user_id = message.from_user.id
    ikb_ru = InlineKeyboardButton(text=lf("russian", user_id), callback_data="russian")
    ikb_eng = InlineKeyboardButton(text=lf("english", user_id), callback_data="english")
    ik_markup = InlineKeyboardMarkup(inline_keyboard=[[ikb_eng, ikb_ru]])

    await message.answer(lf("Choose language", user_id), reply_markup=ik_markup)


# function for changing language
@dp.message(lambda message: message.text in change_mode_phrases_audio + change_mode_phrases_video)
async def change_mode(message: types.Message) -> None:
    user_id = message.from_user.id

    if message.text in change_mode_phrases_video:
        user_states_download_mode[user_id] = "video"  # {user_id: "video"/"video"}
    elif message.text in change_mode_phrases_audio:
        user_states_download_mode[user_id] = "audio"  # # {user_id: "video"/"audio"}

    await message.answer(f"{lf('you will be downloading', user_id)} {user_states_download_mode.get(user_id, 'video')}")


# main function which handles all text messages
@dp.message(StateFilter(None), F.text)
async def message_handler(message: types.Message, state: FSMContext) -> None:
    url, user_id = message.text, message.from_user.id

    # by default video format will be downloading
    downloading_mode = user_states_download_mode.setdefault(message.from_user.id, "video")

    await message.answer(lf("link validation", user_id))

    # check if url is valid
    if not is_youtube_url(url):
        await message.answer(lf("not valid", user_id))
        return
    # telegram allows upload file under 50 megabyte, so checking the size of video
    if not is_lower_than_50mb(url, downloading_mode):
        await message.answer(lf("higher than 50mb", user_id))
        return
    # all test are passed so changing the state of user on 'downloading'
    await state.set_state(DownloadStatus.downloading)

    await download_and_send(message, url, downloading_mode, state)


# function for download video/audio to file system and then send it to user in telegram
async def download_and_send(message: types.Message, url: str, downloading_mode: str, state: FSMContext) -> None:
    user_id = message.from_user.id

    await message.answer(lf("file is downloading", user_id))

    # we put process of downloading in separate thread
    path_to_file = await asyncio.to_thread(download_file, url=url, file_type=downloading_mode)
    # prepare file to upload it to telegram
    tg_file = FSInputFile(path_to_file)

    await message.answer(lf("file is uploading", user_id))

    if downloading_mode == "video":
        await message.answer_video(tg_file)
    else:
        await message.answer_audio(tg_file)
    # when everything is done we delete file and set the state of our user to None
    delete_file(path_to_file)
    await state.clear()


# handling event of changing languages
@main_router.callback_query()
async def callback_query_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if callback_query.data == "russian":
        change_user_language("RU", user_id)
        await callback_query.message.answer("Язык изменен", reply_markup=set_keyboard(vbt="Скачать видео 🎥", abt="Скачать аудио 🎵"))

    elif callback_query.data == "english":
        change_user_language("ENG", user_id)
        await callback_query.message.answer("Language has changed", reply_markup=set_keyboard(vbt="Downloading video 🎥", abt="Downloading audio 🎵"))


async def main() -> None:
    bot = Bot(token)
    await bot.set_my_commands(commands=bot_commands, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=['message', 'callback_query'])


if __name__ == '__main__':
    asyncio.run(main())


