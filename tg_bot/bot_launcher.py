import telebot

from tg_bot.repository.sqlite_repository import SQLiteRepository
from tg_bot.models.desired_film import DesiredFilm
from tg_bot.models.watched_film import WatchedFilm

import markdown
from aiogram.utils.markdown import link
from bs4 import BeautifulSoup
import requests

import re
from re import sub
from decimal import Decimal
import io
from datetime import datetime
import pandas as pd
import lxml

API_token = '6093284104:AAEaVsWdq-0UmuKA2myzfI_reVCc41kAEJM'
kinopoisk_search_url = 'https://www.kinopoisk.ru/index.php?kp_query='
kinopoisk_url = 'https://www.kinopoisk.ru'

bot = telebot.TeleBot(API_token)

DB_FILE = 'database.db'
FILE_PATH = 'C:\\Users\\Russkin Dmitry\\Documents\\python\\tg_bot\\repository\\'

text = []
text.append('Привет! Я бот для хранения списков ***желаемых*** к просмотру и ***просмотренных*** фильмов\n\n')
text.append('Я умею:\n')
text.append('- ***добавлять*** _фильм в соответствующий список_\n')
text.append('- ***ранжировать*** _список фильмов по приоритету просмотра или по оценке_\n')
text.append('- ***удалять*** _из списка просмотренные фильмы_\n')
text.append('- ***сохранять*** _список просмотренных и оцененных вами фильмов_\n\n')
text.append('Для выхода в главное меню вы всегда можете написать слово "Отмена"')

HelpMessage = ''
for msg in text:
	HelpMessage = HelpMessage + msg

SQLiteRepository.bind_and_map(DB_FILE)
desired_film_repo = SQLiteRepository[DesiredFilm](DesiredFilm, DesiredFilm.__name__)
watched_film_repo = SQLiteRepository[WatchedFilm](WatchedFilm, WatchedFilm.__name__)

@bot.message_handler(commands=['start'])
def send_start_message(message):
	start_message = 'Привет! Я бот для хранения списков желаемых'
	start_message = start_message + ' к просмотру и просмотренных фильмов. '
	start_message = start_message + 'Для получения информации о моей работе напишите /help'
	bot.reply_to(message, start_message) 

buts = []
buts.append(telebot.types.InlineKeyboardButton('Добавить фильм в список ожидания', callback_data = 'add_des'))
buts.append(telebot.types.InlineKeyboardButton('Добавить фильм в просмотренноe', callback_data = 'add_wat'))
buts.append(telebot.types.InlineKeyboardButton('Удалить фильм из списка ожидания', callback_data = 'del_des'))
buts.append(telebot.types.InlineKeyboardButton('Удалить фильм из просмотренного', callback_data = 'del_wat'))
buts.append(telebot.types.InlineKeyboardButton('Список ожидания просмотра', callback_data = 'show_des'))
buts.append(telebot.types.InlineKeyboardButton('Список просмотренного', callback_data = 'show_wat'))

main_keyb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
main_keyb.add(*buts)

cancel_keyb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
cancel_key = telebot.types.InlineKeyboardButton('Отмена', callback_data = 'cancel')
cancel_keyb.add(cancel_key)

written_title_dict = {}
list_type = {}
title_dict = {}
year_dict = {}
url_dict = {}
priority_dict = {}
rate_dict = {}
comment_dict = {}

@bot.message_handler(content_types=['text'])
def get_commands(message):

	user_name = message.from_user.username
	list_type[user_name] = 'des'

	if message.text == '/help':
		bot.send_message(message.from_user.id, HelpMessage, parse_mode='Markdown', reply_markup = main_keyb)
	elif message.text == 'Добавить фильм в список ожидания':
		list_type[user_name] = 'des'
		bot.send_message(message.from_user.id, 'Напишите название фильма, который хотите посмотреть', reply_markup = cancel_keyb)
		bot.register_next_step_handler(message, add_title)
	elif message.text == 'Удалить фильм из списка ожидания':
		bot.send_message(message.from_user.id, 'Напишите название фильма, который хотите удалить из списка ожидания', reply_markup = cancel_keyb)
		bot.register_next_step_handler(message, del_des_film)
	elif message.text == 'Список ожидания просмотра':
		des_film_lst = desired_film_repo.get_all({'username': user_name})
		if len(des_film_lst) == 0:
			film_lst_info = 'Ваш список ожидания пуст\n\n_Вы можете добавить в него фильмы, которые хотите посмотреть_'
		else:
			des_film_lst.sort(key = lambda x: x.priority, reverse = True)
			film_lst_info = 'Список фильмов, которые вы хотите посмотреть, в порядке убывания приоритета:\n\n'
			for film in des_film_lst:
				if film.url == '':
					film_lst_info = film_lst_info + f'{film.title} ({film.release_year})  -  {film.priority}\n'
				else:
					film_link = link(f'{film.title}', f'{film.url}')
					film_lst_info = film_lst_info + film_link +  f' ({film.release_year})  -  {film.priority}\n'
		bot.send_message(message.from_user.id, film_lst_info, parse_mode='Markdown', reply_markup = main_keyb, disable_web_page_preview=True)
	elif message.text == 'Добавить фильм в просмотренноe':
		list_type[user_name] = 'wat'
		bot.send_message(message.from_user.id, 'Напишите название фильма, который вы посмотрели', reply_markup = cancel_keyb)
		bot.register_next_step_handler(message, add_title)
	elif message.text == 'Удалить фильм из просмотренного':
		bot.send_message(message.from_user.id, 'Напишите название фильма, который хотите удалить из списка просмотренных', reply_markup = cancel_keyb)
		bot.register_next_step_handler(message, del_wat_film)
	elif message.text == 'Список просмотренного':
		wat_film_lst = watched_film_repo.get_all({'username': user_name})
		if len(wat_film_lst) == 0:
			film_lst_info = 'Ваш список просмотренных фильмов пуст\n\n_Вы можете добавить в него фильмы, которые вы посмотрели_'
		else:
			wat_film_lst.sort(key = lambda x: x.rate, reverse = True)
			film_lst_info = 'Список фильмов, которые вы посмотрели, в порядке убывания оценки:\n\n'
			for film in wat_film_lst:
				if film.url == '':
					film_lst_info = film_lst_info + f'{film.title} ({film.release_year})  -  {film.rate}\n'
				else:
					film_link = link(f'{film.title}', f'{film.url}')
					film_lst_info = film_lst_info + film_link +  f' ({film.release_year})  -  {film.rate}\n'
				if len(film.comment) > 0:
					film_lst_info = film_lst_info + f'	Ваш комментарий: "_{film.comment}_"\n\n'
				else:
					film_lst_info = film_lst_info + '\n'
		bot.send_message(message.from_user.id, film_lst_info, parse_mode='Markdown', reply_markup = main_keyb, disable_web_page_preview=True)
	elif message.text == 'Отмена':
		bot.send_message(message.from_user.id, 'Выберите действие', reply_markup=main_keyb)
		bot.register_next_step_handler(message, get_commands)
	else:
		bot.send_message(message.from_user.id, "Я вас не понимаю :(\nНапишите /help для отображения информации обо мне", reply_markup = main_keyb)

def find_film_on_kinopoisk(film_title):
	html_text = requests.get(kinopoisk_search_url+film_title+'&').text
	soup = BeautifulSoup(html_text, 'lxml')
	search_result = soup.find('div', class_ = 'element most_wanted')
	if search_result is None:
		return None, None, None
	else:
		search_result = search_result.find('p', class_ = 'name')
		name_place = search_result.find('a', class_ = 'js-serp-metrika')
		url = kinopoisk_url + name_place['data-url']
		name = name_place.text
		year = search_result.find('span', class_ = 'year').text
		return url, name, year

def find_similar_films_on_kinopoisk(film_title):
	html_text = requests.get(kinopoisk_search_url+film_title).text
	soup = BeautifulSoup(html_text, 'lxml')
	search_results = soup.find_all('div', class_ = 'search_results')
	film_info = search_results[1].find_all('p', class_ = 'name')
	url_lst = []
	name_lst = []
	year_lst = []
	num = len(film_info)
	if num > 10:
		num = 10
	for i in range(num):
		name_place = film_info[i].find('a', class_ = 'js-serp-metrika')
		url_lst.append(kinopoisk_url + name_place['data-url'])
		name_lst.append(name_place.text)
		if film_info[i].find('span', class_ = 'year') is None:
			year_lst.append('нннн')
		else:
			year_lst.append(film_info[i].find('span', class_ = 'year').text)
	return url_lst, name_lst, year_lst

def agr_keyb(step_for_agr: str):
	agr_keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
	yes_key = telebot.types.InlineKeyboardButton(text='Да', callback_data=f'{step_for_agr}|yes')
	agr_keyboard.add(yes_key)
	no_key = telebot.types.InlineKeyboardButton(text='Нет', callback_data=f'{step_for_agr}|no')
	agr_keyboard.add(no_key)
	return agr_keyboard

def add_title(message, search = True):
	user_name = message.from_user.username
	if message.text == 'Отмена':
		bot.send_message(message.from_user.id, 'Выберите действие', reply_markup=main_keyb)
		bot.register_next_step_handler(message, get_commands)
	elif search:
		written_title_dict[user_name] = message.text
		film_url, film_name, film_year = find_film_on_kinopoisk(message.text)
		if film_url is None:
			mes = 'Не нашел такой фильм на Кинопоиске. Попробуйте точнее вспомнить название или введите информацию о нем самостоятельно'
			aux_keyb = telebot.types.InlineKeyboardMarkup(row_width=1)
			key = telebot.types.InlineKeyboardButton(text='Попробую ещё раз', callback_data='new_film_again')
			aux_keyb.add(key)
			key = telebot.types.InlineKeyboardButton(text='Введу информацию о фильме сам', callback_data='new_choose|none')
			aux_keyb.add(key)
			bot.send_message(message.from_user.id, mes, reply_markup = aux_keyb)
		else:
			title_dict[user_name] = film_name
			year_dict[user_name] = film_year
			url_dict[user_name] = film_url
			film_link = link(f'{film_name}', f'{film_url}')
			question = 'Вы имеете в виду фильм ' + film_link + f' ({film_year})?'
			bot.send_message(message.from_user.id, question, parse_mode='Markdown', reply_markup=agr_keyb('new_film'))
	else:
		title_dict[user_name] = message.text
		bot.send_message(message.from_user.id, 'Напишите год, в котором вышел этот фильм')
		bot.register_next_step_handler(message, add_year)

def add_year(message):
	user_name = message.from_user.username

	if message.text == 'Отмена':
		bot.send_message(message.from_user.id, 'Выберите действие', reply_markup=main_keyb)
		bot.register_next_step_handler(message, get_commands)
	else:
		year_dict[user_name] = message.text
		bot.send_message(message.from_user.id, 'Хотите ли вы добавить url ссылку на страницу с этим фильмом?', reply_markup = agr_keyb('new_url'))
	#bot.send_message(message.from_user.id, 'Оцените ваше желание посмотреть этот фильм по шкале от 1 до 10')
	#bot.register_next_step_handler(message, add_des_priority)

def add_url(message):
	user_name = message.from_user.username

	if message.text == 'Отмена':
		bot.send_message(message.from_user.id, 'Выберите действие', reply_markup=main_keyb)
		bot.register_next_step_handler(message, get_commands)
	else:
		url_dict[user_name] = message.text

		if list_type[user_name] == 'des':
			bot.send_message(message.from_user.id, 'Оцените ваше желание посмотреть этот фильм по шкале от 1 до 10')
			bot.register_next_step_handler(message, add_des_priority)
		else:
			bot.send_message(message.from_user.id, 'Оцените этот фильм по шкале от 1 до 10')
			bot.register_next_step_handler(message, add_wat_rate)

def add_des_priority(message):
	user_name = message.from_user.username

	if message.text == 'Отмена':
		bot.send_message(message.from_user.id, 'Выберите действие', reply_markup=main_keyb)
		bot.register_next_step_handler(message, get_commands)
	else:
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
				bot.send_message(message.from_user.id, text=question, reply_markup=agr_keyb('new_des_full'))

def del_des_film(message):
	user_name = message.from_user.username
	if message.text == 'Отмена':
		bot.send_message(message.from_user.id, 'Выберите действие', reply_markup=main_keyb)
		bot.register_next_step_handler(message, get_commands)
	else:
		title = message.text
		film_lst = desired_film_repo.get_all({'title': title, 'username': user_name})
		if len(film_lst) == 0:
			reply_mes = 'Фильма с таким названием нет в вашем списке ожидания. '
			reply_mes = reply_mes + 'Возможно, вы ошиблись при написании названия фильма. '
			reply_mes = reply_mes + 'Посмотрите ваш список ожидания и попробуйте ещё раз'
			bot.send_message(message.from_user.id, reply_mes, reply_markup = main_keyb)
			bot.register_next_step_handler(message, get_commands)
		else:
			desired_film_repo.delete(film_lst[0].pk)
			title_dict[user_name] = film_lst[0].title
			year_dict[user_name] = film_lst[0].release_year
			url_dict[user_name] = film_lst[0].url
			reply_mes = 'Фильм удален из списка ожидания. Хотите добавить его в список просмотренных фильмов?'
			bot.send_message(message.from_user.id, reply_mes, reply_markup = agr_keyb('new_wat'))

def add_wat_rate(message):
	user_name = message.from_user.username
	if message.text == 'Отмена':
		bot.send_message(message.from_user.id, 'Выберите действие', reply_markup=main_keyb)
		bot.register_next_step_handler(message, get_commands)
	else:
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
	if message.text == 'Отмена':
		bot.send_message(message.from_user.id, 'Выберите действие', reply_markup=main_keyb)
		bot.register_next_step_handler(message, get_commands)
	else:
		comment_dict[user_name] = message.text
		question = f'Вы посмотрели фильм под названием "{title_dict[user_name]}", '
		question = question + f'вышедший в {year_dict[user_name]} году, и оценили его на {rate_dict[user_name]} баллов по 10-балльной шкале. '
		question = question + f'Также вы прокомментировали данный фильм следующим образом:\n "_{comment_dict[user_name]}_"\n\n'
		question = question + 'Все верно?'
		bot.send_message(message.from_user.id, text=question, parse_mode="Markdown", reply_markup=agr_keyb('new_wat_ver'))

def del_wat_film(message):
	user_name = message.from_user.username
	if message.text == 'Отмена':
		bot.send_message(message.from_user.id, 'Выберите действие', reply_markup=main_keyb)
		bot.register_next_step_handler(message, get_commands)
	else:
		title = message.text
		film_lst = watched_film_repo.get_all({'title': title, 'username': user_name})
		if len(film_lst) == 0:
			reply_mes = 'Фильма с таким названием нет в вашем списке просмотренных. '
			reply_mes = reply_mes + 'Возможно, вы ошиблись при написании названия фильма. '
			reply_mes = reply_mes + 'Посмотрите ваш список просмотренных фильм и попробуйте ещё раз'
			
		else:
			watched_film_repo.delete(film_lst[0].pk)
			reply_mes = 'Фильм удален из списка просмотренных'

		bot.send_message(message.from_user.id, reply_mes, reply_markup = main_keyb)
		bot.register_next_step_handler(message, get_commands)

@bot.callback_query_handler(func=lambda call: True)
def reply_for_agr(call):
	user_name = call.message.chat.username
	if call.data == 'new_film|yes':
		if list_type[user_name] == 'des':
			bot.send_message(call.message.chat.id, 'Отлично! Оцените ваше желание посмотреть этот фильм по шкале от 1 до 10')
			bot.register_next_step_handler(call.message, add_des_priority)
		else:
			bot.send_message(call.message.chat.id, 'Отлично! Оцените этот фильм по шкале от 1 до 10')
			bot.register_next_step_handler(call.message, add_wat_rate)
	elif call.data == 'new_film|no':
		mes = 'Ладно, попробуйте найти свой фильм в списке:\n\n'
		url_lst, name_lst, year_lst = find_similar_films_on_kinopoisk(written_title_dict[user_name])
		title_dict[user_name] = name_lst
		year_dict[user_name] = year_lst
		url_dict[user_name] = url_lst
		aux_keyb = telebot.types.InlineKeyboardMarkup(row_width=1)
		for i in range(len(url_lst)):
			film_link = link(f'{name_lst[i]}', f'{url_lst[i]}')
			mes = mes + '  -  ' + film_link + f' ({year_lst[i]})\n'
			key = telebot.types.InlineKeyboardButton(text=f'"{name_lst[i]}" ({year_lst[i]})', parse_mode='Markdown', callback_data='new_choose|'+str(i))
			aux_keyb.add(key)
		key = telebot.types.InlineKeyboardButton(text='Введу информацию о фильме сам', callback_data='new_choose|none')
		aux_keyb.add(key)
		mes = mes + '\n_Выберите нужное_:'
		bot.send_message(call.message.chat.id, mes, parse_mode='Markdown', reply_markup = aux_keyb, disable_web_page_preview=True)
	elif call.data == 'new_film_again':
		bot.send_message(call.message.chat.id, 'Напишите название фильма', reply_markup = cancel_keyb)
		bot.register_next_step_handler(call.message, add_title)
	elif call.data == 'new_choose|none':
		if list_type[user_name] == 'des':
			bot.send_message(call.message.chat.id, 'Напишите правильное название фильма, который хотите посмотреть')
		else:
			bot.send_message(call.message.chat.id, 'Напишите правильное название фильма, который вы посмотрели')
		bot.register_next_step_handler(call.message, add_title, search = False)
	elif call.data.find('new_choose') >= 0:
		l = len(call.data)
		i = int(call.data[l-1])
		title_dict[user_name] = title_dict[user_name][i]
		year_dict[user_name] = year_dict[user_name][i]
		url_dict[user_name] = url_dict[user_name][i]

		if list_type[user_name] == 'des':
			bot.send_message(call.message.chat.id, 'Отлично! Оцените ваше желание посмотреть этот фильм по шкале от 1 до 10')
			bot.register_next_step_handler(call.message, add_des_priority)
		else:
			bot.send_message(call.message.chat.id, 'Отлично! Оцените этот фильм по шкале от 1 до 10')
			bot.register_next_step_handler(call.message, add_wat_rate)
	elif call.data == 'new_url|yes':
		bot.send_message(call.message.chat.id, 'Вставьте свою ссылку на данный фильм')
		bot.register_next_step_handler(call.message, add_url)
	elif call.data == 'new_url|no':
		url_dict[user_name] = ''

		if list_type[user_name] == 'des':
			bot.send_message(call.message.chat.id, 'Хорошо. Оцените ваше желание посмотреть этот фильм по шкале от 1 до 10')
			bot.register_next_step_handler(call.message, add_des_priority)
		else:
			bot.send_message(call.message.chat.id, 'Хорошо. Оцените этот фильм по шкале от 1 до 10')
			bot.register_next_step_handler(call.message, add_wat_rate)
	elif call.data == 'new_des_full|yes':
		des_film = DesiredFilm(title_dict[user_name], year_dict[user_name], url_dict[user_name], priority_dict[user_name], user_name)
		desired_film_repo.add(des_film)
		bot.send_message(call.message.chat.id, 'Отлично, новый фильм добавлен в список ожидания!', reply_markup=main_keyb)
		bot.register_next_step_handler(call.message, get_commands)
	elif call.data == 'new_des_full|no':
		bot.send_message(call.message.chat.id, 'Ничего страшного) Если ошиблись, попробуйте ещё раз!', reply_markup=main_keyb)
		bot.register_next_step_handler(call.message, get_commands)
	elif call.data == 'new_wat|yes':
		list_type[user_name] = 'wat'
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
		watched_film = WatchedFilm(title_dict[user_name], year_dict[user_name], url_dict[user_name], rate_dict[user_name], comment_dict[user_name], user_name)
		watched_film_repo.add(watched_film)
		bot.send_message(call.message.chat.id, 'Отлично, новый фильм добавлен в список просмотренного!', reply_markup=main_keyb)
		bot.register_next_step_handler(call.message, get_commands)
	elif call.data == 'new_wat_ver|no':
		bot.send_message(call.message.chat.id, 'Ничего страшного) Если ошиблись, попробуйте ещё раз!', reply_markup=main_keyb)
		bot.register_next_step_handler(call.message, get_commands)

	bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=None)

bot.polling(none_stop=True, interval=0)