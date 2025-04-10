import gspread
import telebot
from oauth2client.service_account import ServiceAccountCredentials
import time
import sqlite3
from telebot import types


CREDENTIALS_FILE = 'mypython-451516-60099cd00f2d.json'


SPREADSHEET_ID = "1aqf8Emr6R0q2eiJrPp0x3gNfH3M3o25M5OHV_yiOcxM"


scope = [
    "https://spreadsheets.google.com/feeds",
    'https://www.googleapis.com/auth/drive'
]


creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)

try:
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Запись на СГ")
except gspread.SpreadsheetNotFound:
    print(f"Ошибка: Таблица с ID '{SPREADSHEET_ID}' не найдена.")
    exit()
except gspread.WorksheetNotFound:
    print("Ошибка: Лист 'Запись на СГ' не найден в таблице.")
    exit()
except Exception as e:
    print(f"Ошибка при открытии таблицы: {e}")
    exit()


bot = telebot.TeleBot('7748261656:AAGWXBoQdDjoiEh_Hy0nzGB5buqDh8HsgP8')


user_states = {}



def create_table():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_name TEXT,
            user_role TEXT
        )
    ''')
    conn.commit()
    conn.close()

create_table()

def get_slot_status(slot):
    return f"❌ *{slot[0]}*" if slot and slot[0] else '✅ _Слот свободен_'

def format_slots(slots, roles, slot_numbers, slot_nomer):
    return [f"{slot_nomer}: 👤 *{slot_number}* : {role[0]} -  {get_slot_status(slot)}" for slot, role, slot_number, slot_nomer in zip(slots, roles, slot_numbers,slot_nomer)]


def get_friday_1_slots_info():
    

    data = sheet.get_values('I4:N31')  
    date_value = data[0][0:2]  # I4:J4
    side_value = data[1][0:2]  # I5:J5
    tip_value = data[1][3:5]   # T5:V5
    name_value = data[0][3:5]  # T4:V4
    maps_value = data[2][3:5]  # T6:V6

    
    
    
    date_output = ''.join([str(date) for date in date_value[0]])

    
    side_output = ''.join([str(side) for side in side_value[0]])

    
    tip_output = ''.join([str(tip) for tip in tip_value[0]])

    
    name_output = ''.join([str(name) for name in name_value[0]])

    
    maps_output = ''.join([str(maps) for maps in maps_value[0]])

    
    if "Синие" in side_output:
        side_emoji = "🔵"
    elif "Красные" in side_output:
        side_emoji = "🔴"
    elif "Зелёные" in side_output:
        side_emoji = "🟢"
    else:
        side_emoji = ""

    slots = [row[0:2] for row in data[3:11]]  
    roles = [row[2:5] for row in data[3:11]]  
    
    slot_numbers = [data[i][5] for i in range(3, len(data))]   

    slot_nomer = sheet.col_values(8)[6:]
    
    if len(slots) < 8:
        slots += [[] for _ in range(8 - len(slots))]
        roles += [[] for _ in range(8 - len(roles))]
        slot_numbers += [str(i + 1) for i in range(len(slot_numbers), 8)]

    formatted_slots = format_slots(slots[:8], roles[:8], slot_numbers[:8],slot_nomer[:8])

    
    reserve_slots = [row[0:2] for row in data[11:28]]  # Q15:R31 (дополнительные слоты)
    reserve_roles = [row[2:5] for row in data[11:28]]  # S15:U31 (роли для дополнительных слотов)
    reserve_slot_numbers = sheet.col_values(8)[14:]  # Номера запасных слотов

    reserve_text = ""
    
    for i, (slot, role, slot_number) in enumerate(zip(reserve_slots, reserve_roles, reserve_slot_numbers)):
        if slot and slot[0]:  
            if role and role[0]:  
                reserve_text += f"👤 *Запасной слот {slot_number}* : {role[0]} - ❌ *{slot[0]}*\n"
            else:
                reserve_text += f"👤 *Запасной слот {slot_number}* : - ❌ *{slot[0]}*\n"
        
        
        if not slot and not role:
            break

    if reserve_text:
        reserve_text = "\n\n*Дополнительные слоты:*\n" + reserve_text

    text = f"*Пятница (первая игра)*\n*Дата:* **{date_output}**\n*Сторона:* **{side_output} {side_emoji}**\n*Тип:* **{tip_output}**\n*Название:* **{name_output}**\n*Карта:* **{maps_output}**\n" + "\n".join(formatted_slots) + reserve_text

    return text, slots


def get_friday_2_slots_info():
    # Получаем данные из таблицы


    data = sheet.get_values('Q4:V31') 
    date_value = data[0][0:2]  # I4:J4
    side_value = data[1][0:2]  # I5:J5
    tip_value = data[1][3:5]   # T5:V5
    name_value = data[0][3:5]  # T4:V4
    maps_value = data[2][3:5]  # T6:V6

    
    date_output = ''.join([str(date) for date in date_value[0]])

    
    side_output = ''.join([str(side) for side in side_value[0]])

    
    tip_output = ''.join([str(tip) for tip in tip_value[0]])

    
    name_output = ''.join([str(name) for name in name_value[0]])

    
    maps_output = ''.join([str(maps) for maps in maps_value[0]])

    
    if "Синие" in side_output:
        side_emoji = "🔵"
    elif "Красные" in side_output:
        side_emoji = "🔴"
    elif "Зелёные" in side_output:
        side_emoji = "🟢"
    else:
        side_emoji = ""
    slots = [row[0:2] for row in data[3:11]]  # Q7:R14 
    roles = [row[2:5] for row in data[3:11]]  # S7:U14 
    
    slot_numbers = [data[i][5] for i in range(3, len(data))]   
    slot_nomer = sheet.col_values(8)[6:]
    
    if len(slots) < 8:
        slots += [[] for _ in range(8 - len(slots))]
        roles += [[] for _ in range(8 - len(roles))]
        slot_numbers += [str(i + 1) for i in range(len(slot_numbers), 8)]

    formatted_slots = format_slots(slots[:8], roles[:8], slot_numbers[:8], slot_nomer[:8])

    
    reserve_slots = [row[0:2] for row in data[11:28]]  # Q15:R31 (дополнительные слоты)
    reserve_roles = [row[2:5] for row in data[11:28]]  # S15:U31 (роли для дополнительных слотов)
    reserve_slot_numbers = sheet.col_values(8)[14:]  

    reserve_text = ""
    
    for i, (slot, role, slot_number) in enumerate(zip(reserve_slots, reserve_roles, reserve_slot_numbers)):
        if slot and slot[0]:  
            if role and role[0]:  
                reserve_text += f"👤 *Запасной слот {slot_number}* : {role[0]} - ❌ *{slot[0]}*\n"
            else:
                reserve_text += f"👤 *Запасной слот {slot_number}* : - ❌ *{slot[0]}*\n"
        
        
        if not slot and not role:
            break

    if reserve_text:
        reserve_text = "\n\n*Дополнительные слоты:*\n" + reserve_text

    text = f"*Пятница (вторая игра)*\n*Дата:* **{date_output}**\n*Сторона:* **{side_output} {side_emoji}**\n*Тип:* **{tip_output}**\n*Название:* **{name_output}**\n*Карта:* **{maps_output}**\n" + "\n".join(formatted_slots) + reserve_text

    return text, slots




def get_saturday_1_slots_info():
    

    
    data = sheet.get_values('I41:N68') 
    date_value = data[0][0:2]  # I4:J4
    side_value = data[1][0:2]  # I5:J5
    tip_value = data[1][3:5]   # T5:V5
    name_value = data[0][3:5]  # T4:V4
    maps_value = data[2][3:5]  # T6:V6






    
    date_output = ''.join([str(date) for date in date_value[0]])

    
    side_output = ''.join([str(side) for side in side_value[0]])

    
    tip_output = ''.join([str(tip) for tip in tip_value[0]])

    
    name_output = ''.join([str(name) for name in name_value[0]])

    
    maps_output = ''.join([str(maps) for maps in maps_value[0]])

    
    if "Синие" in side_output:
        side_emoji = "🔵"
    elif "Красные" in side_output:
        side_emoji = "🔴"
    elif "Зелёные" in side_output:
        side_emoji = "🟢"
    else:
        side_emoji = ""

    slots = [row[0:2] for row in data[3:11]]  
    roles = [row[2:5] for row in data[3:11]]  
    
    slot_numbers = [data[i][5] for i in range(3, len(data))]   
    slot_nomer = sheet.col_values(8)[6:]

    
    if len(slots) < 8:
        slots += [[] for _ in range(8 - len(slots))]
        roles += [[] for _ in range(8 - len(roles))]
        slot_numbers += [str(i + 1) for i in range(len(slot_numbers), 8)]

    formatted_slots = format_slots(slots[:8], roles[:8], slot_numbers[:8], slot_nomer)

    
    reserve_slots = [row[0:2] for row in data[11:28]]  
    reserve_roles = [row[2:5] for row in data[11:28]] 
    reserve_slot_numbers = sheet.col_values(8)[14:]  

    reserve_text = ""
    
    for i, (slot, role, slot_number) in enumerate(zip(reserve_slots, reserve_roles, reserve_slot_numbers)):
        if slot and slot[0]: 
            if role and role[0]:  
                reserve_text += f"👤 *Запасной слот {slot_number}* : {role[0]} - ❌ *{slot[0]}*\n"
            else:
                reserve_text += f"👤 *Запасной слот {slot_number}* : - ❌ *{slot[0]}*\n"
        
        
        if not slot and not role:
            break

    if reserve_text:
        reserve_text = "\n\n*Дополнительные слоты:*\n" + reserve_text

    text = f"*Суббота (первая игра)*\n*Дата:* **{date_output}**\n*Сторона:* **{side_output} {side_emoji}**\n*Тип:* **{tip_output}**\n*Название:* **{name_output}**\n*Карта:* **{maps_output}**\n" + "\n".join(formatted_slots) + reserve_text

    return text, slots


def get_saturday_2_slots_info():
   

    
    data = sheet.get_values('Q41:V68')  
    date_value = data[0][0:2]  # I4:J4
    side_value = data[1][0:2]  # I5:J5
    tip_value = data[1][3:5]   # T5:V5
    name_value = data[0][3:5]  # T4:V4
    maps_value = data[2][3:5]  # T6:V6


    
    date_output = ''.join([str(date) for date in date_value[0]])

    
    side_output = ''.join([str(side) for side in side_value[0]])

    
    tip_output = ''.join([str(tip) for tip in tip_value[0]])

    
    name_output = ''.join([str(name) for name in name_value[0]])

    
    maps_output = ''.join([str(maps) for maps in maps_value[0]])

    
    if "Синие" in side_output:
        side_emoji = "🔵"
    elif "Красные" in side_output:
        side_emoji = "🔴"
    elif "Зелёные" in side_output:
        side_emoji = "🟢"
    else:
        side_emoji = ""

    slots = [row[0:2] for row in data[3:11]]  # Q7:R14 
    roles = [row[2:5] for row in data[3:11]]  # S7:U14 
    
    slot_numbers = [data[i][5] for i in range(3, len(data))]  
    slot_nomer = sheet.col_values(8)[6:]

    
    if len(slots) < 8:
        slots += [[] for _ in range(8 - len(slots))]
        roles += [[] for _ in range(8 - len(roles))]
        slot_numbers += [str(i + 1) for i in range(len(slot_numbers), 8)]

    formatted_slots = format_slots(slots[:8], roles[:8], slot_numbers[:8], slot_nomer)

   
    reserve_slots = [row[0:2] for row in data[11:28]]  # Q15:R31 
    reserve_roles = [row[2:5] for row in data[11:28]]  # S15:U31 
    reserve_slot_numbers = sheet.col_values(8)[14:]  

    reserve_text = ""
    
    for i, (slot, role, slot_number) in enumerate(zip(reserve_slots, reserve_roles, reserve_slot_numbers)):
        if slot and slot[0]:  
            if role and role[0]:  
                reserve_text += f"👤 *Запасной слот {slot_number}* : {role[0]} - ❌ *{slot[0]}*\n"
            else:
                reserve_text += f"👤 *Запасной слот {slot_number}* : - ❌ *{slot[0]}*\n"
        
        
        if not slot and not role:
            break

    if reserve_text:
        reserve_text = "\n\n*Дополнительные слоты:*\n" + reserve_text

    text = f"*Суббота (вторая игра)*\n*Дата:* **{date_output}**\n*Сторона:* **{side_output} {side_emoji}**\n*Тип:* **{tip_output}**\n*Название:* **{name_output}**\n*Карта:* **{maps_output}**\n" + "\n".join(formatted_slots) + reserve_text

    return text, slots


@bot.message_handler(commands=['saturday_1'])
def handle_saturday_1(message):
    start_time = time.time()
    bot.send_message(message.chat.id, 'Подожди немного, я делаю запрос...')

    text, slots = get_saturday_1_slots_info()

    
    markup = types.InlineKeyboardMarkup()
    buttons = []

    all_slots_filled = True

    roles = sheet.get('K44:M51')  
    slot_numbers = sheet.col_values(8)[43:51]  

    for i, (slot, role, slot_number) in enumerate(zip(slots[:8], roles[:8], slot_numbers[:8])):
        if not slot or not slot[0]:
            all_slots_filled = False
            button = types.InlineKeyboardButton(text=f"Слот {slot_number}", callback_data=f"sat_slot_1_{i+1}")
            buttons.append(button)

            if len(buttons) == 3:
                markup.row(*buttons)
                buttons = []

    if buttons:
        markup.row(*buttons)

    if all_slots_filled and len(slots) >= 8:
        markup.add(types.InlineKeyboardButton(text="Записаться на дополнительный слот", callback_data="sat_reserve_slot_1"))

    markup.add(types.InlineKeyboardButton(text="Удалить запись 🗑", callback_data="sat_remove_slot_1"))
    markup.add(types.InlineKeyboardButton(text="Форма 🪖", callback_data="outfit_3"))

    global message3
    message3 = bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

    

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Время выполнения запроса: {elapsed_time:.2f} секунд")
    global keyboard3
    keyboard3 = markup

@bot.message_handler(commands=['saturday_2'])
def handle_saturday_2(message):
    start_time = time.time()
    bot.send_message(message.chat.id, 'Подожди немного, я делаю запрос...')

    text, slots = get_saturday_2_slots_info()

    
    markup = types.InlineKeyboardMarkup()
    buttons = []

    all_slots_filled = True

    roles = sheet.get('S44:U51') 
    slot_numbers = sheet.col_values(16)[43:51]  

    for i, (slot, role, slot_number) in enumerate(zip(slots[:8], roles[:8], slot_numbers[:8])):
        if not slot or not slot[0]:
            all_slots_filled = False
            button = types.InlineKeyboardButton(text=f"Cлот {slot_number}", callback_data=f"sat_slot_2_{i+1}")
            buttons.append(button)

            if len(buttons) == 3:
                markup.row(*buttons)
                buttons = []

    if buttons:
        markup.row(*buttons)

    if all_slots_filled and len(slots) >= 8:
        markup.add(types.InlineKeyboardButton(text="Записаться на дополнительный слот", callback_data="sat_reserve_slot_2"))

    markup.add(types.InlineKeyboardButton(text="Удалить запись 🗑", callback_data="sat_remove_slot_2"))

    markup.add(types.InlineKeyboardButton(text="Форма 🪖", callback_data="outfit_4"))

    global message4
    message4 = bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Время выполнения запроса: {elapsed_time:.2f} секунд")
    global keyboard4
    keyboard4 = markup


@bot.callback_query_handler(func=lambda call: call.data.startswith("sat_slot_1_"))
def handle_sat_slot_1(call):
    slot_number = int(call.data.split("_")[3])

    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_name, user_role FROM users WHERE user_id = ?', (call.from_user.id,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        user_name, user_role = user_data
        full_name = f"{user_name} ({user_role})"

        
        slots = sheet.get('I44:J51')  
        reserve_slots = sheet.get('I52:J')  

        for slot in slots + reserve_slots:
            if slot and slot[0] == full_name:
                bot.answer_callback_query(call.id, text="Вы уже записаны на другой слот")
                return

        
        sheet.update_cell(44 + slot_number - 1, 9, full_name)  

        text, slots = get_saturday_1_slots_info()
        bot.answer_callback_query(call.id, text=f"Вы записались на слот {slot_number}")
        bot.send_message(call.message.chat.id, f"Вы успешно записались на слот {slot_number}")
        bot.edit_message_text(chat_id=message3.chat.id, message_id=message3.id, text=text,
                              parse_mode='Markdown', reply_markup=keyboard3)

    else:
        bot.answer_callback_query(call.id, text="Вы не зарегистрированы")


@bot.callback_query_handler(func=lambda call: call.data.startswith("sat_slot_2_"))
def handle_sat_slot_2(call):
    slot_number = int(call.data.split("_")[3])

    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_name, user_role FROM users WHERE user_id = ?', (call.from_user.id,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        user_name, user_role = user_data
        full_name = f"{user_name} ({user_role})"

       
        slots = sheet.get('Q44:R51')  
        reserve_slots = sheet.get('Q52:R')  

        for slot in slots + reserve_slots:
            if slot and slot[0] == full_name:
                bot.answer_callback_query(call.id, text="Вы уже записаны на другой слот")
                return

        
        sheet.update_cell(44 + slot_number - 1, 17, full_name) 

        text, slots = get_saturday_2_slots_info()
        bot.answer_callback_query(call.id, text=f"Вы записались на слот {slot_number}")
        bot.send_message(call.message.chat.id, f"Вы успешно записались на слот {slot_number}")
        bot.edit_message_text(chat_id=message4.chat.id, message_id=message4.id, text=text,
                              parse_mode='Markdown', reply_markup=keyboard4)

    else:
        bot.answer_callback_query(call.id, text="Вы не зарегистрированы")


@bot.callback_query_handler(func=lambda call: call.data == "sat_remove_slot_1")
def remove_slot_sat_1(call):
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_name, user_role FROM users WHERE user_id = ?', (call.from_user.id,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        user_name, user_role = user_data
        full_name = f"{user_name} ({user_role})"

        
        slots = sheet.get('I44:J51')
        for i, slot in enumerate(slots):
            if slot and slot[0] == full_name:
                
                sheet.update_cell(44 + i, 9, '')  
                bot.answer_callback_query(call.id, text="Ваша запись удалена")
                text, slots = get_saturday_1_slots_info()
                bot.edit_message_text(chat_id=message3.chat.id, message_id=message3.id, text=text,
                                      parse_mode='Markdown', reply_markup=keyboard3)
                return

        
        reserve_slots = sheet.get('I52:J')
        for i, slot in enumerate(reserve_slots):
            if slot and slot[0] == full_name:
                
                sheet.update_cell(52 + i, 9, '')  
                bot.answer_callback_query(call.id, text="Ваша запись удалена")
                text, slots = get_saturday_1_slots_info()
                bot.edit_message_text(chat_id=message3.chat.id, message_id=message3.id, text=text,
                                      parse_mode='Markdown', reply_markup=keyboard3)
                return

        bot.answer_callback_query(call.id, text="Вы не записаны на этот день")
    else:
        bot.answer_callback_query(call.id, text="Вы не зарегистрированы")

@bot.callback_query_handler(func=lambda call: call.data == "sat_remove_slot_2")
def remove_slot_sat_2(call):
    
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_name, user_role FROM users WHERE user_id = ?', (call.from_user.id,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        user_name, user_role = user_data
        full_name = f"{user_name} ({user_role})"

        
        slots = sheet.get('Q44:R51')
        for i, slot in enumerate(slots):
            if slot and slot[0] == full_name:
                
                sheet.update_cell(44 + i, 17, '') 
                bot.answer_callback_query(call.id, text="Ваша запись удалена")
                text, slots = get_saturday_2_slots_info()
                bot.edit_message_text(chat_id=message4.chat.id, message_id=message4.id, text=text,
                                      parse_mode='Markdown', reply_markup=keyboard4)
                return

        
        reserve_slots = sheet.get('Q52:R')
        for i, slot in enumerate(reserve_slots):
            if slot and slot[0] == full_name:
                
                sheet.update_cell(52 + i, 17, '')  
                bot.answer_callback_query(call.id, text="Ваша запись удалена")
                text, slots = get_saturday_2_slots_info()
                bot.edit_message_text(chat_id=message4.chat.id, message_id=message4.id, text=text,
                                      parse_mode='Markdown', reply_markup=keyboard4)
                return

        bot.answer_callback_query(call.id, text="Вы не записаны на этот день")
    else:
        bot.answer_callback_query(call.id, text="Вы не зарегистрированы")



@bot.message_handler(commands=['friday_2']) 
def handle_friday_2(message):
    

    
    start_time = time.time()
    bot.send_message(message.chat.id, 'Подожди немного, я делаю запрос...')

    text, slots = get_friday_2_slots_info()

    
    markup = types.InlineKeyboardMarkup()
    buttons = []

    all_slots_filled = True  

    roles = sheet.get('S7:U14')
    slot_numbers = sheet.col_values(16)[6:]

    for i, (slot, role, slot_number) in enumerate(zip(slots[:8], roles[:8], slot_numbers[:8])):
        if not slot or not slot[0]:  
            all_slots_filled = False  
            button = types.InlineKeyboardButton(text=f"Cлот {slot_number}", callback_data=f"slot_2_{i+1}")
            buttons.append(button)

            if len(buttons) == 3:  
                markup.row(*buttons)
                buttons = []

    if buttons:
        markup.row(*buttons)

    if all_slots_filled and len(slots) >= 8:  
        markup.add(types.InlineKeyboardButton(text="Записаться на дополнительный слот", callback_data="reserve_slot_2"))

    markup.add(types.InlineKeyboardButton(text="Удалить запись 🗑", callback_data="remove_slot_2"))

    markup.add(types.InlineKeyboardButton(text="Форма 🪖", callback_data="outfit_2"))

    global message1
    message1 = bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup) 
    
    end_time = time.time()  
    elapsed_time = end_time - start_time  
    print(f"Время выполнения запроса: {elapsed_time:.2f} секунд")  
    global keyboard
    keyboard = markup

@bot.message_handler(commands=['friday_1'])
def handle_friday_1(message):
    start_time = time.time()
    bot.send_message(message.chat.id, 'Подожди немного, я делаю запрос...')

    text, slots = get_friday_1_slots_info()

    
    markup = types.InlineKeyboardMarkup()
    buttons = []

    all_slots_filled = True

    roles = sheet.get('K7:M14')
    slot_numbers = sheet.col_values(8)[6:]

    for i, (slot, role, slot_number) in enumerate(zip(slots[:8], roles[:8], slot_numbers[:8])):
        if not slot or not slot[0]:
            all_slots_filled = False
            button = types.InlineKeyboardButton(text=f"Слот {slot_number}", callback_data=f"slot_1_{i+1}")
            buttons.append(button)

            if len(buttons) == 3:
                markup.row(*buttons)
                buttons = []

    if buttons:
        markup.row(*buttons)

    if all_slots_filled and len(slots) >= 8:
        markup.add(types.InlineKeyboardButton(text="Записаться на дополнительный слот", callback_data="reserve_slot_1"))

    markup.add(types.InlineKeyboardButton(text="Удалить запись 🗑", callback_data="remove_slot_1"))

    markup.add(types.InlineKeyboardButton(text="Форма 🪖", callback_data="outfit_1"))

    global message2
    message2 = bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Время выполнения запроса: {elapsed_time:.2f} секунд")
    global keyboard2
    keyboard2 = markup

@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (message.from_user.id,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton('Пятница 1')
        btn2 = types.KeyboardButton('Пятница 2')
        btn3 = types.KeyboardButton('Суббота 1')
        btn4 = types.KeyboardButton('Суббота 2')
        markup.add(btn1, btn2, btn3, btn4)
        
        bot.send_message(message.chat.id, 'Ты уже зарегистрировался, выбери игру:', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Привет! Меня зовут Анастасия. Можно просто Настя. Меня создал Глинополк, чтобы помогать членам отряда TAF.')
        time.sleep(4)
        bot.send_message(message.chat.id, 'Давай познакомимся поближе. Как тебя зовут?')
        
        
        user_states[message.from_user.id] = 'wait_name'

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == 'Пятница 1':
        bot.send_message(message.chat.id, "Загружаю информацию по первой игре в пятницу...")
        handle_friday_1(message)
    elif message.text == 'Пятница 2':
        bot.send_message(message.chat.id, "Загружаю информацию по второй игре в пятницу...")
        handle_friday_2(message)
    elif message.text == 'Суббота 1':
        bot.send_message(message.chat.id, "Загружаю информацию по первой игре в субботу...")
        handle_saturday_1(message)
    elif message.text == 'Суббота 2':
        bot.send_message(message.chat.id, "Загружаю информацию по второй игре в субботу...")
        handle_saturday_2(message)
    
    if message.from_user.id in user_states and user_states[message.from_user.id] == 'wait_name':
        allowed_names = ['lolfastik','Swift','Tynec','Argonak','Kamchatka','Glinopolk','Steppe','Storm','Barmaley','Club','PEBHOCTb','Ukrainec','Ugol','Kondra','Rulka','PAHTERA','Wekman','Ultio','4apaev','Losc','Tapok','Dubas','Andreika','Crauch','Strangekyy']
        user_name = message.text
        if user_name in allowed_names:
            roles = {
                'lolfastik': 'Командир отряда',
                'Swift': 'Заместитель Командира отряда',
                'Tynec': 'Заместитель Командира отряда',
                'Argonak': 'Заместитель Командира отряда',
                'Kamchatka': 'Штабист',
                'Glinopolk': 'Штабист',
                'Steppe': 'Штабист',
                'Storm': 'Штабист',
                'Barmaley': 'Боец отряда',
                'Club': 'Боец отряда',
                'PEBHOCTb': 'Боец отряда',
                'Ukrainec': 'Боец отряда',
                'Ugol': 'Курсант отряда',
                'Kondra': 'Курсант отряда',
                'Rulka': 'Курсант отряда',
                'Strangekyy': 'Курсант отряда',
                'Crauch': 'Курсант отряда',
                'Ultio': 'Боец запаса',
                '4apaev': 'Боец запаса',
                'Losc': 'Боец запаса',
                'Tapok': 'Боец запаса',
                'Dubas': 'Боец запаса',
                'Andreika': 'Боец запаса',
                
            }
            
            conn = sqlite3.connect('bot.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (user_id, user_name, user_role) VALUES (?, ?, ?)',
                           (message.from_user.id, user_name, roles[user_name]))
            conn.commit()
            conn.close()
            
            bot.send_message(message.chat.id, f'Привет, {user_name}! Теперь ты сможешь использовать мой функционал на 100%')



            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton('Пятница 1')
            btn2 = types.KeyboardButton('Пятница 2')
            btn3 = types.KeyboardButton('Суббота 1')
            btn4 = types.KeyboardButton('Суббота 2')
            markup.add(btn1, btn2, btn3, btn4)
        
            bot.send_message(message.chat.id, 'Можешь выбирать игру:', reply_markup=markup)
            
            del user_states[message.from_user.id]
        else:
            bot.send_message(message.chat.id, 'Хм, я не нашла тебя в своей Базе Данных, может ты ошибся?.')







@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    
    if call.data.startswith("slot_1_"):
        slot_number = int(call.data.split("_")[2])

        
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_name, user_role FROM users WHERE user_id = ?', (call.from_user.id,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            user_name, user_role = user_data
            full_name = f"{user_name} ({user_role})"

            
            slots = sheet.get('I7:J14')  
            reserve_slots = sheet.get('I15:J22')  

            for slot in slots + reserve_slots:
                if slot and slot[0] == full_name:
                    bot.answer_callback_query(call.id, text="Вы уже записаны на другой слот")
                    return

            
            sheet.update_cell(7 + slot_number - 1, 9, full_name) 

            text, slots = get_friday_1_slots_info()

            bot.answer_callback_query(call.id, text=f"Вы записались на слот {slot_number}")
            bot.send_message(call.message.chat.id, f"Вы успешно записались на слот {slot_number}")
            bot.edit_message_text(chat_id=message2.chat.id, message_id=message2.id, text=text,
                                  parse_mode='Markdown', reply_markup=keyboard2)

        else:
            bot.answer_callback_query(call.id, text="Вы не зарегистрированы")

    elif call.data == "reserve_slot_1":
        
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_name, user_role FROM users WHERE user_id = ?', (call.from_user.id,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            
            user_name, user_role = user_data
            full_name = f"{user_name} ({user_role})"

            
            slots = sheet.get('I7:J14')  
            reserve_slots = sheet.get('I15:J22')  

            for slot in slots + reserve_slots:
                if slot and slot[0] == full_name:
                    bot.answer_callback_query(call.id, text="Вы уже записаны на другой слот")
                    return

           
            reserve_slots = sheet.get('I15:J22')  
            for i, slot in enumerate(reserve_slots):
                
                if not slot or not slot[0]:  
                    
                   
                    sheet.update_cell(15 + i, 9, full_name)  

                    bot.answer_callback_query(call.id, text=f"Вы записались на дополнительный слот 9")
                    bot.send_message(call.message.chat.id, f"Вы успешно записались на дополнительный слот 9")
                    
                    
                    break

                elif len(reserve_slots) == 1:  
                    
                    sheet.update_cell(15 + i+1, 9, full_name)  

                    bot.answer_callback_query(call.id, text=f"Вы записались на дополнительный слот 10")
                    bot.send_message(call.message.chat.id, f"Вы успешно записались на дополнительный слот 10")
                    break
                
                elif len(reserve_slots) == 2:  
                    
                    sheet.update_cell(15 + i+2, 9, full_name) 

                    bot.answer_callback_query(call.id, text=f"Вы записались на дополнительный слот 11")
                    bot.send_message(call.message.chat.id, f"Вы успешно записались на дополнительный слот 11")
                    break
                elif len(reserve_slots) == 3:  
                    
                    sheet.update_cell(15 + i+3, 9, full_name)  

                    bot.answer_callback_query(call.id, text=f"Вы записались на дополнительный слот 12")
                    bot.send_message(call.message.chat.id, f"Вы успешно записались на дополнительный слот 12")
                    break
                elif len(reserve_slots) == 4:  
                    
                    sheet.update_cell(15 + i+4, 9, full_name)  

                    bot.answer_callback_query(call.id, text=f"Вы записались на дополнительный слот 13")
                    bot.send_message(call.message.chat.id, f"Вы успешно записались на дополнительный слот 13")
                    break
                
            else:
                bot.answer_callback_query(call.id, text="Нет доступных дополнительных слотов")
        else:
            bot.answer_callback_query(call.id, text="Вы не зарегистрированы")

    elif call.data == "remove_slot_1":
      
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_name, user_role FROM users WHERE user_id = ?', (call.from_user.id,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            user_name, user_role = user_data
            full_name = f"{user_name} ({user_role})"

            
            slots = sheet.get('I7:J14')
            for i, slot in enumerate(slots):
                if slot and slot[0] == full_name:
                    sheet.update_cell(7 + i, 9, "")  
                    text, slots = get_friday_1_slots_info()
                    bot.answer_callback_query(call.id, text=f"Ваша запись на слот {i + 1} удалена")
                    bot.send_message(call.message.chat.id, f"Ваша запись на слот {i + 1} успешно удалена")
                    bot.edit_message_text(chat_id=message2.chat.id, message_id=message2.id, text=text,
                                          parse_mode='Markdown', reply_markup=keyboard2)
                    
                    return

            
            reserve_slots = sheet.get('I15:J22')
            for i, slot in enumerate(reserve_slots):
                if slot and slot[0] == full_name:
                    sheet.update_cell(15 + i, 9, "")  

                    bot.answer_callback_query(call.id, text=f"Ваша запись на дополнительный слот {i + 1} удалена")
                    bot.send_message(call.message.chat.id, f"Ваша запись на дополнительный слот {i + 1} успешно удалена")
                    return

            bot.answer_callback_query(call.id, text="У вас нет записей для удаления")
        else:
            bot.answer_callback_query(call.id, text="Вы не зарегистрированы")



    elif call.data == "outfit_1":
        bot.send_message(call.message.chat.id, f"Мы:")
        outfit_1 = sheet.get_values('K979:K984')  
        for i in range(0,len(outfit_1)):
            bot.send_message(call.message.chat.id, outfit_1[i])
        bot.send_message(call.message.chat.id, f"Враг:")
        outfit_1_enemy = sheet.get_values('K985:K990')  
        for i in range(0,len(outfit_1_enemy)):
            bot.send_message(call.message.chat.id, outfit_1_enemy[i])

    elif call.data == "outfit_2":
        bot.send_message(call.message.chat.id, f"Мы:")
        outfit_1 = sheet.get_values('L979:L984')  
        for i in range(0,len(outfit_1)):
            bot.send_message(call.message.chat.id, outfit_1[i])
        bot.send_message(call.message.chat.id, f"Враг:")
        outfit_1_enemy = sheet.get_values('L985:L990')  
        for i in range(0,len(outfit_1_enemy)):
            bot.send_message(call.message.chat.id, outfit_1_enemy[i])

    
    elif call.data == "outfit_3":
        bot.send_message(call.message.chat.id, f"Мы:")
        outfit_1 = sheet.get_values('M979:M984')  
        for i in range(0,len(outfit_1)):
            bot.send_message(call.message.chat.id, outfit_1[i])
        bot.send_message(call.message.chat.id, f"Враг:")
        outfit_1_enemy = sheet.get_values('M985:M990')  
        for i in range(0,len(outfit_1_enemy)):
            bot.send_message(call.message.chat.id, outfit_1_enemy[i])

    elif call.data == "outfit_4":
        bot.send_message(call.message.chat.id, f"Мы:")
        outfit_1 = sheet.get_values('N979:N984')  
        for i in range(0,len(outfit_1)):
            bot.send_message(call.message.chat.id, outfit_1[i])
        bot.send_message(call.message.chat.id, f"Враг:")
        outfit_1_enemy = sheet.get_values('N985:N990')  
        for i in range(0,len(outfit_1_enemy)):
            bot.send_message(call.message.chat.id, outfit_1_enemy[i])

    

     
    if call.data.startswith("slot_2_"):
        slot_number = int(call.data.split("_")[2])
        
        
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_name, user_role FROM users WHERE user_id = ?', (call.from_user.id,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            user_name, user_role = user_data
            full_name = f"{user_name} ({user_role})"
            
            
            slots = sheet.get('Q7:R14')  
            reserve_slots = sheet.get('Q15:R22')  
            
            for slot in slots + reserve_slots:
                if slot and slot[0] == full_name:
                    bot.answer_callback_query(call.id, text="Вы уже записаны на другой слот")
                    return
            
           
            sheet.update_cell(7 + slot_number - 1, 17, full_name)  


            text, slots = get_friday_2_slots_info()

                                                                                 


            
            bot.answer_callback_query(call.id, text=f"Вы записались на слот {slot_number}")
            bot.send_message(call.message.chat.id, f"Вы успешно записались на слот {slot_number}")
            bot.edit_message_text(chat_id = message1.chat.id, message_id = message1.id, text = text, parse_mode='Markdown',reply_markup=keyboard)





            
        else:
            bot.answer_callback_query(call.id, text="Вы не зарегистрированы")
            
    
    elif call.data == "reserve_slot_2":
        
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_name, user_role FROM users WHERE user_id = ?', (call.from_user.id,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            
            user_name, user_role = user_data
            full_name = f"{user_name} ({user_role})"

            
            slots = sheet.get('Q7:R14')  
            reserve_slots = sheet.get('Q15:R22')  

            for slot in slots + reserve_slots:
                if slot and slot[0] == full_name:
                    bot.answer_callback_query(call.id, text="Вы уже записаны на другой слот")
                    return

            
            reserve_slots = sheet.get('Q15:R22')  
            
            for i, slot in enumerate(reserve_slots):
                
                if not slot or not slot[0]:  
                    
                    
                    sheet.update_cell(15 + i, 17, full_name)  

                    bot.answer_callback_query(call.id, text=f"Вы записались на дополнительный слот 9")
                    bot.send_message(call.message.chat.id, f"Вы успешно записались на дополнительный слот 9")
                    
                    
                    break

                elif len(reserve_slots) == 1:  
                    
                    sheet.update_cell(15 + i+1, 17, full_name)  

                    bot.answer_callback_query(call.id, text=f"Вы записались на дополнительный слот 10")
                    bot.send_message(call.message.chat.id, f"Вы успешно записались на дополнительный слот 10")
                    break
                
                elif len(reserve_slots) == 2:  
                    
                    sheet.update_cell(15 + i+2, 17, full_name)  

                    bot.answer_callback_query(call.id, text=f"Вы записались на дополнительный слот 11")
                    bot.send_message(call.message.chat.id, f"Вы успешно записались на дополнительный слот 11")
                    break
                elif len(reserve_slots) == 3:  
                    
                    sheet.update_cell(15 + i+3, 17, full_name) 

                    bot.answer_callback_query(call.id, text=f"Вы записались на дополнительный слот 12")
                    bot.send_message(call.message.chat.id, f"Вы успешно записались на дополнительный слот 12")
                    break
                elif len(reserve_slots) == 4:  
                    
                    sheet.update_cell(15 + i+4, 17, full_name)  

                    bot.answer_callback_query(call.id, text=f"Вы записались на дополнительный слот 13")
                    bot.send_message(call.message.chat.id, f"Вы успешно записались на дополнительный слот 13")
                    break
                
            else:
                bot.answer_callback_query(call.id, text="Нет доступных дополнительных слотов")
        else:
            bot.answer_callback_query(call.id, text="Вы не зарегистрированы")
    
        
            
    elif call.data == "remove_slot_2":
        
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_name, user_role FROM users WHERE user_id = ?', (call.from_user.id,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            user_name, user_role = user_data
            full_name = f"{user_name} ({user_role})"
            
            
            slots = sheet.get('Q7:R14')
            for i, slot in enumerate(slots):
                if slot and slot[0] == full_name:
                    sheet.update_cell(7 + i, 17, "")  
                    text, slots = get_friday_2_slots_info()
                    bot.answer_callback_query(call.id, text=f"Ваша запись на слот {i+1} удалена")    
                    bot.send_message(call.message.chat.id, f"Ваша запись на слот {i+1} успешно удалена")
                    bot.edit_message_text(chat_id = message1.chat.id, message_id = message1.id, text = text, parse_mode='Markdown',reply_markup=keyboard)
                    
                    return
            
            
            reserve_slots = sheet.get('Q15:R22')
            for i, slot in enumerate(reserve_slots):
                if slot and slot[0] == full_name:
                    sheet.update_cell(15 + i, 17, "")  
                    
                    bot.answer_callback_query(call.id, text=f"Ваша запись на дополнительный слот {i+1} удалена")
                    bot.send_message(call.message.chat.id, f"Ваша запись на дополнительный слот {i+1} успешно удалена")
                    return
            
            bot.answer_callback_query(call.id, text="У вас нет записей для удаления")
        else:
            bot.answer_callback_query(call.id, text="Вы не зарегистрированы")


    
    elif call.data == "sat_reserve_slot_1":
        
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_name, user_role FROM users WHERE user_id = ?', (call.from_user.id,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            
            user_name, user_role = user_data
            full_name = f"{user_name} ({user_role})"

            
            slots = sheet.get('I44:J51')  
            reserve_slots = sheet.get('I52:J58')  

            for slot in slots + reserve_slots:
                if slot and slot[0] == full_name:
                    bot.answer_callback_query(call.id, text="Вы уже записаны на другой слот")
                    return

            
            reserve_slots = sheet.get('I52:J58')  
            
            for i, slot in enumerate(reserve_slots):
                
                if not slot or not slot[0]: 
                    
                   
                    sheet.update_cell(52 + i, 9, full_name) 

                    bot.answer_callback_query(call.id, text=f"Вы записались на дополнительный слот 9")
                    bot.send_message(call.message.chat.id, f"Вы успешно записались на дополнительный слот 9")
                    
                    
                    break

                elif len(reserve_slots) == 1:  
                    
                    sheet.update_cell(52 + i+1, 9, full_name)  

                    bot.answer_callback_query(call.id, text=f"Вы записались на дополнительный слот 10")
                    bot.send_message(call.message.chat.id, f"Вы успешно записались на дополнительный слот 10")
                    break
                
                elif len(reserve_slots) == 2:  
                    
                    sheet.update_cell(52 + i+2, 9, full_name)  

                    bot.answer_callback_query(call.id, text=f"Вы записались на дополнительный слот 11")
                    bot.send_message(call.message.chat.id, f"Вы успешно записались на дополнительный слот 11")
                    break
                elif len(reserve_slots) == 3:  
                    
                    sheet.update_cell(52 + i+3, 9, full_name)  

                    bot.answer_callback_query(call.id, text=f"Вы записались на дополнительный слот 12")
                    bot.send_message(call.message.chat.id, f"Вы успешно записались на дополнительный слот 12")
                    break
                elif len(reserve_slots) == 4:  
                    
                    sheet.update_cell(52 + i+4, 9, full_name)  

                    bot.answer_callback_query(call.id, text=f"Вы записались на дополнительный слот 13")
                    bot.send_message(call.message.chat.id, f"Вы успешно записались на дополнительный слот 13")
                    break
                
            else:
                bot.answer_callback_query(call.id, text="Нет доступных дополнительных слотов")
        else:
            bot.answer_callback_query(call.id, text="Вы не зарегистрированы")

    elif call.data == "sat_reserve_slot_2":
        
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_name, user_role FROM users WHERE user_id = ?', (call.from_user.id,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            
            user_name, user_role = user_data
            full_name = f"{user_name} ({user_role})"

            
            slots = sheet.get('Q44:R51')  
            reserve_slots = sheet.get('Q52:R58')  

            for slot in slots + reserve_slots:
                if slot and slot[0] == full_name:
                    bot.answer_callback_query(call.id, text="Вы уже записаны на другой слот")
                    return

            
            reserve_slots = sheet.get('Q52:R58')  
            
            for i, slot in enumerate(reserve_slots):
                
                if not slot or not slot[0]:  
                    
                    
                    sheet.update_cell(52 + i, 17, full_name) 

                    bot.answer_callback_query(call.id, text=f"Вы записались на дополнительный слот 9")
                    bot.send_message(call.message.chat.id, f"Вы успешно записались на дополнительный слот 9")
                    
                    
                    break

                elif len(reserve_slots) == 1:  
                    
                    sheet.update_cell(52 + i+1, 17, full_name)  

                    bot.answer_callback_query(call.id, text=f"Вы записались на дополнительный слот 10")
                    bot.send_message(call.message.chat.id, f"Вы успешно записались на дополнительный слот 10")
                    break
                
                elif len(reserve_slots) == 2:  
                    
                    sheet.update_cell(52 + i+2, 17, full_name)  

                    bot.answer_callback_query(call.id, text=f"Вы записались на дополнительный слот 11")
                    bot.send_message(call.message.chat.id, f"Вы успешно записались на дополнительный слот 11")
                    break
                elif len(reserve_slots) == 3:  
                    
                    sheet.update_cell(52 + i+3, 17, full_name)  

                    bot.answer_callback_query(call.id, text=f"Вы записались на дополнительный слот 12")
                    bot.send_message(call.message.chat.id, f"Вы успешно записались на дополнительный слот 12")
                    break
                elif len(reserve_slots) == 4:  
                    
                    sheet.update_cell(52 + i+4, 17, full_name)  

                    bot.answer_callback_query(call.id, text=f"Вы записались на дополнительный слот 13")
                    bot.send_message(call.message.chat.id, f"Вы успешно записались на дополнительный слот 13")
                    break
                
            else:
                bot.answer_callback_query(call.id, text="Нет доступных дополнительных слотов")
        else:
            bot.answer_callback_query(call.id, text="Вы не зарегистрированы")



        

bot.infinity_polling()
