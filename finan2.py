import requests
import logging
import sys
import ssl
from aiohttp import web
import asyncio
from aiohttp.web_request import Request
from aiohttp import web
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import CommandStart, Command, Filter, StateFilter
from aiogram.types import Message, InputFile, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaVideo, WebAppData, CallbackQuery
from aiogram.utils.markdown import hbold
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from datetime import datetime, timedelta
import random
from aiogram.enums import ParseMode
import psycopg2
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import pytz




from aiohttp.web_request import Request
from aiohttp import web
import sqlite3

bot = Bot(token="Unfound")

dp = Dispatcher()


conn = psycopg2.connect("""
#Скрыто
""")

#--------------------- DB soft block ---------------------
def update_new_cards(id_card, status,spend_amount,balance_amount,card_group_name, note):
    global conn
    cursor = conn.cursor()
    
    cursor.execute("""INSERT INTO multicards (id, status, spend_amount, balance_amount, card_group_name, note) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET spend_amount = (%s), balance_amount = (%s), card_group_name = (%s), note = (%s)""", (id_card, status,spend_amount,balance_amount,card_group_name, note,spend_amount, balance_amount, card_group_name, note))
    conn.commit()
    cursor.close()

def get_card_for_id(id_card):
    global conn
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM multicards WHERE id = (%s)", (str(id_card),))
    users_id = [row for row in cursor.fetchall()]
    # Выводим результаты
    cursor.close()
    return users_id

def delete_full():
    global conn
    cursor = conn.cursor()
    cursor.execute("DELETE FROM multicards ")
    # Выводим результаты
    cursor.close()

def get_card_for_name(card_group_name):
    global conn
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM multicards WHERE card_group_name = (%s)", (str(card_group_name),))
    cards_list = cursor.fetchall()
    

    # Выводим результаты
    cursor.close()
    return cards_list

def update_new_user(tg_id, web):
    global conn
    cursor = conn.cursor()
    
    cursor.execute("""INSERT INTO tgadminmult (tg_id, web) VALUES (%s, %s) ON CONFLICT (tg_id) DO NOTHING""", (tg_id, web))
    conn.commit()
    cursor.close()
    
def update_amount_web(tg_id, amount):
    global conn
    cursor = conn.cursor()
    
    cursor.execute("""INSERT INTO tgadminmult (tg_id) VALUES (%s) ON CONFLICT (tg_id) DO UPDATE SET amount = (%s)""", (tg_id, amount))
    conn.commit()
    cursor.close()
    
def get_tg_admin():
    global conn
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tgadminmult")
    dict_admin={}
    for row in cursor.fetchall():
        dict_admin[row[0]] = {
            "web":row[1],
            "amount": row[2]
        }
    # Выводим результаты
    cursor.close()
    return dict_admin
    

#--------------------- DB soft block ---------------------

#--------------------- FSM ---------------------

class Reg_tg_user(StatesGroup):
    web = State()
    
class Deposit_cards(StatesGroup):
    amount = State()
    
class Delete_card(StatesGroup):
    cheker = State()
#--------------------- FSM ---------------------
#--------------------- Cards ---------------------


def start_auth():

    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 YaBrowser/24.6.0.0 Safari/537.36',
    }
    json_data = {
    'email': 'unfound',
    'password': 'unfound',
    }
    response = requests.post('https://api.multicards.io/v1/auth/login', headers=headers, json=json_data)
    return response.json()['token']


headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 YaBrowser/24.6.0.0 Safari/537.36',
        'x-auth-token': start_auth()
    }


def delete_card(id, headers):
    response = requests.post(f'https://api.multicards.io/v1/card/{id}/close', headers=headers)
    data_card = response.json()
    
    id_card = data_card['id']
    status = data_card['status']
    spend_amount = data_card['spendAmount']
    balance_amount = data_card['balanceAmount']
    status = data_card['status']
    note = data_card['note']
    try:
        card_group_name = data_card['cardGroupName']
    except:
        card_group_name = ''


    global conn
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO multicards (id, status, spend_amount, balance_amount, card_group_name, note) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET spend_amount = (%s), balance_amount = (%s), card_group_name = (%s), note = (%s), status = (%s)""", (id_card, status,spend_amount,balance_amount,card_group_name, note,spend_amount, balance_amount, card_group_name, note,status))

    conn.commit()
    cursor.close()
    
    
def deposit_card(id, headers, amount):
    
    response = requests.post(f'https://api.multicards.io/v1/card/{id}/deposit', headers=headers,json={"amount":amount})
    
    data_card = response.json()
    id_card = data_card['id']
    status = data_card['status']
    spend_amount = data_card['spendAmount']
    balance_amount = data_card['balanceAmount']
    note = data_card['note']
    try:
        card_group_name = data_card['cardGroupName']
    except:
        card_group_name = ''


    global conn
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO multicards (id, status, spend_amount, balance_amount, card_group_name, note) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET spend_amount = (%s), balance_amount = (%s), card_group_name = (%s), note = (%s)""", (id_card, status,spend_amount,balance_amount,card_group_name, note,spend_amount, balance_amount, card_group_name, note))

    conn.commit()
    cursor.close()   
    
#--------------------- Cards ---------------------


def update_user_cards(headers):
    # delete_full()
    response = requests.get('http://api.multicards.io/v1/card/list', headers=headers)
    a = 0
    for i in response.json():
        if i['status'] == "ACTIVE":
            a+=1
            id_card = i['id']
            status = i['status']
            spend_amount = i['spendAmount']
            balance_amount = i['balanceAmount']
            note = i['note']
            try:
                card_group_name = i['cardGroupName']
            except:
                card_group_name = ''
            
            update_new_cards(id_card, status,spend_amount,balance_amount,card_group_name, note)
            
    
#--------------------- Reg TG User ---------------------
    
@dp.message(F.text == "/TeamOZ")
async def reg_in_bot(message: Message, state: FSMContext):
    await message.answer("Привет, пришли Ник, который тебе отписал Никита")
    # Устанавливаем пользователю состояние "выбирает название"
    await state.set_state(Reg_tg_user.web)  
    
@dp.message(Reg_tg_user.web)
async def web_name(message: Message, state: FSMContext):
    user_data = await state.get_data()
    update_new_user(message.chat.id, message.text)

    await state.clear()  
        
#--------------------- Reg TG User ---------------------

#--------------------- Start ---------------------

@dp.message(CommandStart())
async def cmd_start(message: Message):
    
    if str(message.chat.id) not in list(get_tg_admin()):
        
        
        caption = f"""
Привет, {message.chat.username}!💗 
Введи пароль для пользования ботом и потом нажми на /start

    """
        await bot.send_message(chat_id=message.chat.id, text=caption, parse_mode=ParseMode.HTML)
    
        
    else:
        key_board = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Весь список карт", callback_data="card_list")],

            ]
        )
        
        caption = f"""
Привет, {message.chat.username}!💗 
Добро пожаловать в бота по оплате аккаунтов

"""

        await bot.send_message(chat_id=message.chat.id, text=caption,  parse_mode=ParseMode.HTML, reply_markup=key_board)
    
 
@dp.callback_query(F.data == "card_list")
async def card_list(callback: CallbackQuery):
    
    await callback.answer('Переход')
    global headers
    
    update_user_cards(headers)  
    
    await callback.message.answer('Вот ваш список карт, вы можете пополнить карту и её закрыть')
    
    cards_web_list = get_card_for_name(get_tg_admin()[str(callback.message.chat.id)]['web'])
    
    for i in cards_web_list:
        if i[1] == "ACTIVE":
            key_board = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Пополнить карту", callback_data=f"amount_{i[0]}"),InlineKeyboardButton(text="Закрыть карту", callback_data=f"delete_{i[0]}")],
                ]
            )
            
            
            name_card = i[5]
            amount = i[3]
            spend = i[2]
            text = f'''
Название карты: {name_card}
Сейчас на балансе: {amount}$       
Всего потрачено с карты: {spend}$        

            '''
            await bot.send_message(chat_id=callback.message.chat.id, text=text, reply_markup=key_board,  parse_mode=ParseMode.HTML)
        
        
    
@dp.callback_query(F.data.startswith('delete_'))
async def deletes_card(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Переход')
    await state.set_state(Delete_card.cheker)  
    await state.update_data(id_card=callback.data.split('_')[-1])

    
    
    await bot.send_message(chat_id=callback.message.chat.id, text=f'Вы уверены? Если да то отпишите в чат "Да"', parse_mode=ParseMode.HTML)    
     
     
@dp.message(Delete_card.cheker)
async def cheker(message: Message, state: FSMContext):
    
    global headers
    user_data = await state.get_data()
    if message.text == 'Да':
        cards_web_list = get_tg_admin()[str(message.chat.id)]['web']
        date = datetime.now(pytz.timezone("Europe/Moscow")).strftime('%d.%m.%Y')
        
        get_card_for_id(user_data['id_card'])
        text= f'''
#{cards_web_list}
Удалил карту, возврат средств
{get_card_for_id(user_data['id_card'])[0][3]}$
{date}         
            
'''
        await bot.send_message(chat_id=-1002154030826, text=text, parse_mode=ParseMode.HTML)
        
        

        new_amount = float(get_tg_admin()[str(message.chat.id)]['amount']) - float(get_card_for_id(user_data['id_card'])[0][3])
         
        update_amount_web(message.chat.id, new_amount)
        
        
        await message.answer(f'Карта удалена')
        delete_card(user_data['id_card'], headers)

        
        await state.clear()  
        
        
    else:
        await message.answer('Ну так уж и быть жми /start')
        await state.clear()  
        
        
    
            
            

@dp.callback_query(F.data.startswith('amount_'))
async def amount_card(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Переход')
    await state.set_state(Deposit_cards.amount)  
    await state.update_data(id_card=callback.data.split('_')[-1])
    await bot.send_message(chat_id=callback.message.chat.id, text=f'Введите сумму', parse_mode=ParseMode.HTML)
    
    
@dp.message(Deposit_cards.amount)
async def deposits_card(message: Message, state: FSMContext):

    await state.update_data(amount=message.text)
    global headers
    user_data = await state.get_data()
    
    try:
        amount = int(user_data['amount'])
        if 0 < amount <= 30:
            id_card = user_data['id_card']
            deposit_card(id_card, headers, amount)
            await message.answer('Карта пополнена!')
            await state.clear()  
            date = datetime.now(pytz.timezone("Europe/Moscow")).strftime('%d.%m.%Y')
            
            cards_web_list = get_tg_admin()[str(message.chat.id)]['web']
            try:
                new_amount = float(get_tg_admin()[str(message.chat.id)]['amount']) + amount
            except:
                new_amount = float(amount)   
            
            update_amount_web(message.chat.id, new_amount)
            text= f'''
#{cards_web_list}
{amount}$
{date}         
            
            '''
            await bot.send_message(chat_id=-1002154030826, text=text, parse_mode=ParseMode.HTML)
            
        else:
            await message.answer('Введите число от 0 до 30. Если хотите прервать пополнение то напишите "Выход"')
            await state.set_state(Deposit_cards.amount)  
            
    except:
        if user_data['amount'] == "Выход":
            await message.answer('Пока пока')
            await state.clear()  
        else:
            await message.answer('Введите число. Если хотите прервать пополнение то напишите "Выход"')
            await state.set_state(Deposit_cards.amount) 

#--------------------- Start ---------------------
 

            
print('start')
async def main():
    await dp.start_polling(bot,skip_updates=True)

if __name__ == "__main__":
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot is blocked")
print("end")

