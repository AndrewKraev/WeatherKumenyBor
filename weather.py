#!/usr/bin/python3

import config

import telebot
from telebot import types

import requests
import datetime

# Формируем кнопки
def show_btn():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_kumeny = types.KeyboardButton(text='Кумены')
    btn_kirov = types.KeyboardButton(text='Киров')
    keyboard.add(btn_kumeny,btn_kirov)
    return keyboard
    
def show_ibtn(i_city):
    i_keyboard = types.InlineKeyboardMarkup(row_width=1)
    ibtn_3d = types.InlineKeyboardButton('Прогноз', callback_data=i_city)
    i_keyboard.add(ibtn_3d)
    return i_keyboard

# Запрос к yandex погода
def get_yandex(lat, lon):
    res = requests.get(
        'https://api.weather.yandex.ru/v2/informers',
        params={'lat':lat,'lon':lon,'lang':'ru_RU'},
        headers={'X-Yandex-API-Key':'e3c8dd6f-0234-4527-a29c-6fb8b1fa31df'},
    )
    res_all = res.json()
    return res_all

# Собираем log
def bot_log(mes):
    f = open('bot_log', 'a')
    try:
        dt_now = datetime.datetime.now()
        f.write(str(dt_now)+' '+str(mes.chat.id)+' '+str(mes.chat.first_name)+' '+str(mes.chat.last_name)+' '+str(mes.text)+'\n')
    finally:
        f.close()
#  Формирование текста погода сейчас       
def weather_now(name_city):
        res = get_yandex(config.city.get(name_city)[1],config.city.get(name_city)[2])
    
        temp0 = 'Сейчас в '+ config.city.get(name_city)[0]
        temp2 = 'Температура \t'+str(res['fact']['temp'])+' (°C)'
        temp3 = 'Ощущается как \t'+str(res['fact']['feels_like'])+' (°C)'
        temp4 = 'Скорость ветра \t'+ str(res['fact']['wind_speed'])+' (м/с)'
        temp5 = 'Порывы \t'+ str(res['fact']['wind_gust'])+' (м/с)'         
        temp6 = 'Ветер дует с '+ config.dict_wind_dir.get(res['fact']['wind_dir'])
        temp7 = 'Давление \t'+ str(res['fact']['pressure_mm'])+' в мм рт.ст.'
        temp8 = config.dict_cond.get(res['fact']['condition'])
 #       temp9 = res['fact']['prec_type']
        temp = temp0+'\n'+temp2+'\n'+temp3+'\n'+temp4+'\n'+temp5+'\n'+temp6+'\n'+temp7+'\n'+temp8
        
        return temp
        
def weather_3d(name_city_3d):
        tmp_out = []
        tmp = ''              
        res_3d = get_yandex(config.city.get(name_city_3d)[1],config.city.get(name_city_3d)[2])
         
        for data_3d in res_3d['forecast']['parts']:
            if data_3d['part_name'] == 'day': 
                tmp = 'Днем в '+ config.city.get(name_city_3d)[0]+'\nТемпература  '+str(data_3d['temp_avg'])+'(°C)\n'+'Давление '+str(data_3d['pressure_mm'])+' мм рт.ст.\n'+config.dict_cond.get(data_3d['condition']) 
            elif data_3d['part_name'] == 'night':
                tmp = 'Ночью в '+ config.city.get(name_city_3d)[0]+'\nТемпература  '+str(data_3d['temp_avg'])+'(°C)\n'+'Давление '+str(data_3d['pressure_mm'])+' мм рт.ст.\n'+config.dict_cond.get(data_3d['condition'])
            elif data_3d['part_name'] == 'morning':
                tmp = 'Утром в '+ config.city.get(name_city_3d)[0]+'\nТемпература  '+str(data_3d['temp_avg'])+'(°C)\n'+'Давление '+str(data_3d['pressure_mm'])+' мм рт.ст.\n'+config.dict_cond.get(data_3d['condition'])
            elif data_3d['part_name'] == 'evening':
                tmp = 'Вечером в '+ config.city.get(name_city_3d)[0]+'\nТемпература '++str(data_3d['temp_avg'])+'(°C)\n'+'Давление '+str(data_3d['pressure_mm'])+' мм рт.ст.\n'+config.dict_cond.get(data_3d['condition']) 
            else:
                tmp = 'op'

            tmp_out.append(tmp)
       
        return tmp_out

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['start','help'])
def start(message):
        bot.send_message(message.chat.id, 'Привет '+message.chat.first_name, reply_markup=show_btn())
        
@bot.message_handler(content_types='text')
def send_welcome(message):
        if message.text == 'Киров':
            text_out = weather_now(message.text)    
            bot_log(message)
            bot.send_message(message.chat.id, text = text_out, reply_markup=show_ibtn(message.text))
        elif message.text == 'Кумены':
            text_out = weather_now(message.text)    
            bot_log(message)
            bot.send_message(message.chat.id, text = text_out, reply_markup=show_ibtn(message.text))
        else:
            bot.send_message(message.chat.id, text = 'Жми на кнопку-узнаешь погоду', reply_markup=show_btn())

@bot.callback_query_handler(func=lambda call:True)
def callback(call):

    if call.message:
        if call.data == 'Кумены':
            bot.answer_callback_query(call.id)
            tt = weather_3d(call.data)
            bot.send_message(call.message.chat.id, tt[0])
            bot.send_message(call.message.chat.id, tt[1])
#            bot.send_message(call.message.chat.id, weather_3d(call.data)[2])
        elif call.data == 'Киров':
            bot.answer_callback_query(call.id)
            ttk = weather_3d(call.data)
            bot.send_message(call.message.chat.id, ttk[0])
            bot.send_message(call.message.chat.id, ttk[1])
   #         bot.send_message(call.message.chat.id, weather_3d(call.data)[2])
        else:
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, 'Тут пока ничего нет')        
        
bot.infinity_polling()


