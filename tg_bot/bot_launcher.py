import telebot

from tg_bot.repository.sqlite_repository import SQLiteRepository
from tg_bot.models.wordcard import WordCard
from tg_bot.models.lesson import Lesson

API_token = '6093284104:AAEaVsWdq-0UmuKA2myzfI_reVCc41kAEJM'

bot = telebot.TeleBot(API_token)

DB_FILE = 'database.db'
FILE_PATH = 'C:\\Users\\Russkin Dmitry\\Documents\\python\\tg_bot\\repository\\'

text = []
text.append("Привет! Я бот для хранения информации по обучению английскому языку\n\n")
text.append("Добавить карточку со словом: /addcard\n")
text.append("Добавить информацию об уроке: /addlesson\n")
text.append("Посмотреть все карточки со словами: /getallcards\n")

HelpMessage = ""
for msg in text:
	HelpMessage = HelpMessage + msg

def bind_database():
    filepath = FILE_PATH
    db_name = DB_FILE

    SQLiteRepository.bind_and_map(db_name)

bind_database()
wordcard_repo = SQLiteRepository[WordCard](WordCard, WordCard.__name__)
lesson_repo = SQLiteRepository[Lesson](Lesson, Lesson.__name__)

@bot.message_handler(content_types=['text'])
def get_start_messages(message):

	if message.text == "Привет":
		bot.send_message(message.from_user.id, "Привет! Напиши /help для отображения информации обо мне")
	elif message.text == "/help":
		bot.send_message(message.from_user.id, HelpMessage)
	elif message.text == "/addcard":
		bot.send_message(message.from_user.id, "Напиши слово, которое хочешь добавить в карточку")
		bot.register_next_step_handler(message, add_word)
	elif message.text == "/getallcards":
		card_lst = wordcard_repo.get_all()
		cards_info = "Сохраненные карточки:\n\n"
		for card in card_lst:
			cards_info = cards_info + f"{card.word}  -  {card.translation}\n"
		bot.send_message(message.from_user.id, cards_info)
		bot.register_next_step_handler(message, get_start_messages)
	else:
		bot.send_message(message.from_user.id, "Я тебя не понимаю :(\nНапиши /help для отображения информации обо мне")

def add_word(message):
	word = message.text
	bot.send_message(message.from_user.id, "Напиши перевод этого слова")
	bot.register_next_step_handler(message, add_translation, word)

def add_translation(message, word):
	translation = message.text
	card = WordCard(word, translation)
	try:
		wordcard_repo.add(card)
		bot.send_message(message.from_user.id, f'Cлово "{word}" c переводом "{translation}" успешно занесено в карточку!')
	except BaseException:
		bot.send_message(message.from_user.id, "Произошла ошибка :(")

	bot.register_next_step_handler(message, get_start_messages)

bot.polling(none_stop=True, interval=0)