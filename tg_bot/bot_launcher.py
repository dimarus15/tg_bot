import telebot

from tg_bot.repository.sqlite_repository import SQLiteRepository
from tg_bot.models.desired_film import DesiredFilm
from tg_bot.models.watched_film import WatchedFilm

API_token = '6093284104:AAEaVsWdq-0UmuKA2myzfI_reVCc41kAEJM'

bot = telebot.TeleBot(API_token)

DB_FILE = 'database.db'
FILE_PATH = 'C:\\Users\\Russkin Dmitry\\Documents\\python\\tg_bot\\repository\\'

text = []
text.append('Привет! Я бот для хранения списков желаемых к просмотру фильмов\n\n')
text.append('Я умею:\n')
text.append('- добавлять фильм в соответствующий список\n')
text.append('- ранжировать список фильмов по приоритету просмотра\n')
text.append('- удалять из списка просмотренные фильмы\n')
text.append('- сохранять список просмотренных и оцененных вами фильмов\n')

HelpMessage = ''
for msg in text:
	HelpMessage = HelpMessage + msg

SQLiteRepository.bind_and_map(DB_FILE)
desired_film_repo = {}
watched_film_repo = {}

@bot.message_handler(commands=['start'])
def send_start_message(message):
	start_message = 'Привет! Я бот для хранения списков желаемых'
	start_message = start_message + ' к просмотру и просмотренных фильмов. '
	start_message = start_message + 'Для получения информации о моей работе напишите /help'
	bot.reply_to(message, start_message) 

buts = []
buts.append(telebot.types.InlineKeyboardButton('Добавить фильм в список ожидания', callback_data = 'add_des'))
buts.append(telebot.types.InlineKeyboardButton('Удалить фильм из списка ожидания', callback_data = 'del_des'))
buts.append(telebot.types.InlineKeyboardButton('Посмотреть список ожидания', callback_data = 'show_des'))
buts.append(telebot.types.InlineKeyboardButton('Добавить фильм в список просмотренных', callback_data = 'add_wat'))
buts.append(telebot.types.InlineKeyboardButton('Удалить фильм из списка просмотренных', callback_data = 'del_wat'))
buts.append(telebot.types.InlineKeyboardButton('Посмотреть список просмотренных фильмов', callback_data = 'show_wat'))

main_keyb =  telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
for but in buts:
	main_keyb.add(but)

@bot.message_handler(content_types=['text'])
def get_commands(message):

	user_name = message.from_user.username
	desired_film_repo[user_name] = SQLiteRepository[user_name](DesiredFilm, DesiredFilm.__name__)
	watched_film_repo[user_name] = SQLiteRepository[user_name](WatchedFilm, WatchedFilm.__name__)

	if message.text == '/help':
		bot.send_message(message.from_user.id, HelpMessage, reply_markup = main_keyb)
	elif message.text == 'Добавить фильм в список ожидания':
		bot.send_message(message.from_user.id, 'Напишите название фильма, который хотите посмотреть')
		bot.register_next_step_handler(message, add_des_title)
	elif message.text == 'Удалить фильм из списка ожидания':
		bot.send_message(message.from_user.id, 'Напишите название фильма, который хотите удалить из списка ожидания')
		bot.register_next_step_handler(message, del_des_film)
	elif message.text == 'Посмотреть список ожидания':
		des_film_lst = desired_film_repo[user_name].get_all()
		des_film_lst.sort(key = lambda x: x.priority, reverse = True)
		film_lst_info = 'Список фильмов, которые вы хотите посмотреть, в порядке убывания приоритета:\n\n'
		for film in des_film_lst:
			film_lst_info = film_lst_info + f'{film.title} ({film.release_year})  -  {film.priority}\n'
		bot.send_message(message.from_user.id, film_lst_info, reply_markup = main_keyb)
	elif message.text == 'Добавить фильм в список просмотренных':
		bot.send_message(message.from_user.id, 'Напишите название фильма, который вы посмотрели')
		bot.register_next_step_handler(message, add_wat_title)
	elif message.text == 'Удалить фильм из списка просмотренных':
		bot.send_message(message.from_user.id, 'Напишите название фильма, который хотите удалить из списка просмотренных')
		bot.register_next_step_handler(message, del_wat_film)
	elif message.text == 'Посмотреть список просмотренных фильмов':
		wat_film_lst = watched_film_repo[user_name].get_all()
		wat_film_lst.sort(key = lambda x: x.rate, reverse = True)
		film_lst_info = 'Список фильмов, которые вы посмотрели, в порядке убывания оценки:\n\n'
		for film in wat_film_lst:
			film_lst_info = film_lst_info + f'{film.title} ({film.release_year})  -  {film.rate}\n'
			if len(film.comment) > 0:
				film_lst_info = film_lst_info + f'	Ваш комментарий: "{film.comment}"\n'
		bot.send_message(message.from_user.id, film_lst_info, reply_markup = main_keyb)
	else:
		bot.send_message(message.from_user.id, "Я вас не понимаю :(\nНапишите /help для отображения информации обо мне", reply_markup = main_keyb)

title_dict = {}
year_dict = {}
priority_dict = {}
rate_dict = {}
comment_dict = {}

def agr_keyb(step_for_agr: str):
	agr_keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
	yes_key = telebot.types.InlineKeyboardButton(text='Да', callback_data=f'{step_for_agr}|yes')
	agr_keyboard.add(yes_key)
	no_key = telebot.types.InlineKeyboardButton(text='Нет', callback_data=f'{step_for_agr}|no')
	agr_keyboard.add(no_key)
	return agr_keyboard

def add_des_title(message):
	user_name = message.from_user.username
	title_dict[user_name] = message.text
	bot.send_message(message.from_user.id, 'Напишите год, в котором вышел этот фильм')
	bot.register_next_step_handler(message, add_des_year)

def add_des_year(message):
	user_name = message.from_user.username
	year_dict[user_name] = message.text
	bot.send_message(message.from_user.id, 'Оцените ваше желание посмотреть этот фильм по шкале от 1 до 10')
	bot.register_next_step_handler(message, add_des_priority)

def add_des_priority(message):
	user_name = message.from_user.username
	try:
		priority_dict[user_name] = int(message.text)
	except ValueError:
		bot.send_message(message.from_user.id, 'Ваша оценка некорректна - это должно быть число от 1 до 10.\n\nПожалуйста, напишите свою оценку ещё раз')
		bot.register_next_step_handler(message, add_des_priority)
	else:
		if priority_dict[user_name] < 1 or priority_dict[user_name] > 10:
			bot.send_message(message.from_user.id, 'Ваша оценка некорректна - это должно быть число от 1 до 10.\n\nПожалуйста, напишите свою оценку ещё раз')
			bot.register_next_step_handler(message, add_des_priority)
		else:
			question = f'Вы хотите посмотреть фильм под названием "{title_dict[user_name]}", '
			question = question + f'вышедший в {year_dict[user_name]} году, со степенью желания {priority_dict[user_name]}\n\n'
			question = question + 'Все верно?'
			bot.send_message(message.from_user.id, text=question, reply_markup=agr_keyb('new_des'))

def del_des_film(message):
	user_name = message.from_user.username
	title = message.text
	film_lst = desired_film_repo[user_name].get_all({'title': title})
	if len(film_lst) == 0:
		reply_mes = 'Фильма с таким названием нет в вашем списке ожидания. '
		reply_mes = reply_mes + 'Возможно, вы ошиблись при написании названия фильма. '
		reply_mes = reply_mes + 'Посмотрите ваш список ожидания и попробуйте ещё раз'
		bot.send_message(message.from_user.id, reply_mes, reply_markup = main_keyb)
		bot.register_next_step_handler(message, get_commands)
	else:
		desired_film_repo[user_name].delete(film_lst[0].pk)
		title_dict[user_name] = film_lst[0].title
		year_dict[user_name] = film_lst[0].release_year
		reply_mes = 'Фильм удален из списка ожидания. Хотите добавить его в список просмотренных фильмов?'
		bot.send_message(message.from_user.id, reply_mes, reply_markup = agr_keyb('new_wat'))

def add_wat_title(message):
	user_name = message.from_user.username
	title_dict[user_name] = message.text
	bot.send_message(message.from_user.id, 'Напишите год, в котором вышел этот фильм')
	bot.register_next_step_handler(message, add_wat_year)

def add_wat_year(message):
	user_name = message.from_user.username
	year_dict[user_name] = message.text
	bot.send_message(message.from_user.id, 'Оцените этот фильм по шкале от 1 до 10')
	bot.register_next_step_handler(message, add_wat_rate)

def add_wat_rate(message):
	user_name = message.from_user.username
	try:
		rate_dict[user_name] = int(message.text)
	except ValueError:
		bot.send_message(message.from_user.id, 'Ваша оценка некорректна - это должно быть число от 1 до 10.\n\nПожалуйста, напишите свою оценку ещё раз')
		bot.register_next_step_handler(message, add_wat_rate)
	else:
		if rate_dict[user_name] < 1 or rate_dict[user_name] > 10:
			bot.send_message(message.from_user.id, 'Ваша оценка некорректна - это должно быть число от 1 до 10.\n\nПожалуйста, напишите свою оценку ещё раз')
			bot.register_next_step_handler(message, add_wat_rate)
		else:
			bot.send_message(message.from_user.id, 'Хотите добавить комментарий по этому фильму?', reply_markup=agr_keyb('new_wat_add_com'))

def add_wat_comment(message):
	user_name = message.from_user.username
	comment_dict[user_name] = message.text
	question = f'Вы посмотрели фильм под названием "{title_dict[user_name]}", '
	question = question + f'вышедший в {year_dict[user_name]} году, и оценили его на {rate_dict[user_name]} баллов по 10-балльной шкале. '
	question = question + f'Также вы прокомментировали данный фильм следующим образом:\n "{comment_dict[user_name]}"\n\n'
	question = question + 'Все верно?'
	bot.send_message(message.from_user.id, text=question, reply_markup=agr_keyb('new_wat_ver'))

def del_wat_film(message):
	user_name = message.from_user.username
	title = message.text
	film_lst = watched_film_repo[user_name].get_all({'title': title})
	if len(film_lst) == 0:
		reply_mes = 'Фильма с таким названием нет в вашем списке просмотренных. '
		reply_mes = reply_mes + 'Возможно, вы ошиблись при написании названия фильма. '
		reply_mes = reply_mes + 'Посмотрите ваш список просмотренных фильм и попробуйте ещё раз'
		
	else:
		watched_film_repo[user_name].delete(film_lst[0].pk)
		title_dict[user_name] = film_lst[0].title
		year_dict[user_name] = film_lst[0].release_year
		reply_mes = 'Фильм удален из списка просмотренных'

	bot.send_message(message.from_user.id, reply_mes, reply_markup = main_keyb)
	bot.register_next_step_handler(message, get_commands)

@bot.callback_query_handler(func=lambda call: True)
def reply_for_agr(call):
	user_name = call.message.chat.username
	if call.data == 'new_des|yes':
		des_film = DesiredFilm(title_dict[user_name], year_dict[user_name], priority_dict[user_name])
		desired_film_repo[user_name].add(des_film)
		bot.send_message(call.message.chat.id, 'Отлично, новый фильм добавлен в список ожидания!', reply_markup=main_keyb)
		bot.register_next_step_handler(call.message, get_commands)
	elif call.data == 'new_des|no':
		bot.send_message(call.message.chat.id, 'Ничего страшного) Если ошиблись, попробуйте ещё раз!', reply_markup=main_keyb)
		bot.register_next_step_handler(call.message, get_commands)
	elif call.data == 'new_wat|yes':
		bot.send_message(call.message.chat.id, 'Хорошо. Оцените этот фильм по шкале от 1 до 10')
		bot.register_next_step_handler(call.message, add_wat_rate)
	elif call.data == 'new_wat|no':
		bot.send_message(call.message.chat.id, 'Вам виднее) Вы можете выбрать следующее действие', reply_markup=main_keyb)
		bot.register_next_step_handler(call.message, get_commands)
	elif call.data == 'new_wat_add_com|yes':
		bot.send_message(call.message.chat.id, 'Напишите ваш комментарий')
		bot.register_next_step_handler(call.message, add_wat_comment)
	elif call.data == 'new_wat_add_com|no':
		comment_dict[user_name] = ''
		question = f'Вы посмотрели фильм под названием "{title_dict[user_name]}", '
		question = question + f'вышедший в {year_dict[user_name]} году, и оценили его на {rate_dict[user_name]} баллов по 10-балльной шкале\n\n'
		question = question + 'Все верно?'
		bot.send_message(call.message.chat.id, text=question, reply_markup=agr_keyb('new_wat_ver'))
	elif call.data == 'new_wat_ver|yes':
		watched_film = WatchedFilm(title_dict[user_name], year_dict[user_name], rate_dict[user_name], comment_dict[user_name])
		watched_film_repo[user_name].add(watched_film)
		bot.send_message(call.message.chat.id, 'Отлично, новый фильм добавлен в список просмотренного!', reply_markup=main_keyb)
		bot.register_next_step_handler(call.message, get_commands)
	elif call.data == 'new_wat_ver|no':
		bot.send_message(call.message.chat.id, 'Ничего страшного) Если ошиблись, попробуйте ещё раз!', reply_markup=main_keyb)
		bot.register_next_step_handler(call.message, get_commands)

	bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=None)
# def add_word(message):
# 	word = message.text
# 	bot.send_message(message.from_user.id, "Напиши перевод этого слова")
# 	bot.register_next_step_handler(message, add_translation, word)

# def add_translation(message, word):
# 	translation = message.text
# 	card = WordCard(word, translation)
# 	try:
# 		wordcard_repo.add(card)
# 		bot.send_message(message.from_user.id, f'Cлово "{word}" c переводом "{translation}" успешно занесено в карточку!')
# 	except BaseException:
# 		bot.send_message(message.from_user.id, "Произошла ошибка :(")

# 	bot.register_next_step_handler(message, get_start_messages)

# def add_date(message):
# 	date = message.text
# 	bot.send_message(message.from_user.id, "Напиши тему урока")
# 	bot.register_next_step_handler(message, add_theme, date)

# def add_theme(message, date):
# 	theme = message.text
# 	bot.send_message(message.from_user.id, "Напиши сложность урока")
# 	bot.register_next_step_handler(message, add_dif, date, theme)

# def add_dif(message, date, theme):
# 	dif = int(message.text)
# 	Lesson_data = Lesson(date, theme, dif)
# 	lesson_repo.add(Lesson_data)
# 	bot.send_message(message.from_user.id, f'Урок от "{date}" по теме "{theme}" с оценкой "{dif}" успешно занесен в базу!')
# 	# except BaseException:
# 	# 	bot.send_message(message.from_user.id, "Произошла ошибка :(")
# 	bot.register_next_step_handler(message, get_start_messages)

# word = "word"
# translation = "слово"
# card = WordCard(word, translation)
# wordcard_repo.add(card)

# date = "15.02.2001"
# theme = "irregular verbs 2"
# dif = 8
# Lesson_data = Lesson(date, theme, dif)
# lesson_repo.add(Lesson_data)

bot.polling(none_stop=True, interval=0)