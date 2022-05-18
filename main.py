from dotenv import load_dotenv
from telebot import types
from db_manager import xlst_db
from db_manager import psql_db
from db_manager import psql_product_model
from db_manager import psql_purchase_model
import os
import telebot
import logging
import re

load_dotenv()

api_key = os.environ.get('API_KEY')

bot = telebot.TeleBot(api_key)
logging.basicConfig(filename='logfile.log', 
                    level=logging.INFO | logging.DEBUG | logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='w')
logger = logging.getLogger()

db = xlst_db.XLSX_DB('db_manager/db_source/db.xlsx')
MAX_RECORDS = 2

db_manager = psql_db.Database(logger)
purchase_class = psql_purchase_model.Purchase(logger)
product_class = psql_product_model.Product(logger)

message_ids = {}
current_pages = {}
cart = {}

@bot.message_handler(commands=['start', 'menu'])
def send_startup_options(message):
    try:
        save_current_page(message.chat.id, 0)
        bot.clear_step_handler_by_chat_id(message.chat.id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        buttons = []
        buttons.append(types.InlineKeyboardButton('📦 Productos', callback_data='productos'))
        buttons.append(types.InlineKeyboardButton('🛒 Carrito de compras', callback_data='carrito'))
        buttons.append(types.InlineKeyboardButton('📞 Atención personalizada', callback_data='atencion'))
        buttons.append(types.InlineKeyboardButton('Imprimir ids', callback_data='testids'))
        markup.add(*buttons) 
        msg = bot.send_message(message.chat.id, "Escoge una opción: ", reply_markup=markup)
        save_message_id(msg)
    except Exception as e:
        logger.error(e + '\n Usuario: ' + str(message.from_user.username) + 
                     '\n Chat ID: ' + str(message.chat.id))
        send_error_message(message)

@bot.callback_query_handler(lambda query: query.data == "productos")
def products(query):
    try:
        delete_previous_message(query.message)
        bot.clear_step_handler_by_chat_id(query.message.chat.id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        buttons = []
        buttons.append(types.InlineKeyboardButton('Listar todos los productos', callback_data='listar'))
        buttons.append(types.InlineKeyboardButton('Listar por categoría', callback_data='catnombre'))
        buttons.append(types.InlineKeyboardButton('Buscar producto por código', callback_data='bcodigo'))
        buttons.append(types.InlineKeyboardButton('Menú principal', callback_data='backmenu'))
        markup.add(*buttons)
        msg = bot.send_message(query.message.chat.id, "Escoja una opción: ", reply_markup=markup)  
        save_message_id(msg)
    except Exception as e:
        logger.error(e + '\n Usuario: ' + str(query.message.from_user.username) + 
                     '\n Chat ID: ' + str(query.message.chat.id))
        send_error_message(query.message)
        
        
@bot.callback_query_handler(lambda query: query.data == "backmenu")
def backmenu(query):
    delete_previous_message(query.message)
    send_startup_options(query.message)

@bot.callback_query_handler(lambda query: query.data == "listar")
def list_all(query, page = 1):
    try:
        save_current_page(query.message.chat.id, page)
        bot.clear_step_handler_by_chat_id(query.message.chat.id)
        results = product_class.get_products(page, connectiondb)
        records = format_output(results)
        bot.send_message(query.message.chat.id, 'Listado de productos: \n' + str(records.iloc[begin:end, 1:4]))
        markup = types.InlineKeyboardMarkup(row_width=1)
        buttons = []
        buttons.append(types.InlineKeyboardButton('Añadir producto al carrito de compras', callback_data='addcart'))
        buttons.append(types.InlineKeyboardButton('Procesar compra', callback_data='process'))
        buttons.append(types.InlineKeyboardButton('Quitar producto del carrito de compras', callback_data='deleteproduct'))
        if verify_next_records(records, page):
            buttons.append(types.InlineKeyboardButton('Mostrar más productos', callback_data='showmore'))
        buttons.append(types.InlineKeyboardButton('Cancelar', callback_data='cancel'))
        markup.add(*buttons)
        msg = bot.send_message(query.message.chat.id, "Escoja una opción: ", reply_markup=markup)
        save_message_id(msg) 
    except Exception as e:
        logger.error(e + '\n Usuario: ' + str(query.message.from_user.username) + 
                     '\n Chat ID: ' + str(query.message.chat.id))
        send_error_message(query.message)

@bot.callback_query_handler(lambda query: query.data == "addcart")
def add_to_cart(query):
    try:
        delete_previous_message(query.message)
        msg = bot.send_message(query.message.chat.id, 'Escriba el código del producto seguido '+ 
                               'de la cantidad requerida separados por un punto y coma: (Ejemplo: ABCD;5)')
        bot.register_next_step_handler(msg, add_to_cart_step)
    except Exception as e:
        logger.error(e + '\n Usuario: ' + str(query.message.from_user.username) + 
                     '\n Chat ID: ' + str(query.message.chat.id))
        send_error_message(query.message)

def add_to_cart_step(message):
    try:
        data = message.text.split(';')
        quant = data[1].strip()
        if not quant.isDigit():
            msg = bot.send_message(message, 'La cantidad debe ser un número. Ingrese nuevamente: (Ejemplo: ABCD;5)')
            bot.register_next_step_handler(msg, add_to_cart_step)
            return
        quant = int(quant)
        code = str(data[0]).strip()        
        result = db.get_record_by_param('Productos', 'Código', code)
        record = result[0]
        if(len(record) == 0):
            bot.send_message(message.chat.id, "El código no existe. Ingrese uno válido: (Ejemplo: ABCD;5)")
            bot.register_next_step_handler(message, add_to_cart_step)
            return
        record = record.iloc[0]
        total = record['Precio'] * quant
        purchase = (record['Código'], quant, total)
        remember_product(message.chat.id, purchase)
        bot.send_message(message.chat.id, 'Producto agregado al carrito de compras')
    except Exception as e:
        logger.error(e + '\n Usuario: ' + str(message.from_user.username) + 
                     '\n Chat ID: ' + str(message.chat.id))
        send_error_message(message)

def save_purchase(dni, message):
    try:        
        if(len(cart[message.chat.id]) == 0):
            bot.send_message(message.chat.id, 'No hay productos en el carrito de compras')
            return
        pedidos = db.get_all_records('Pedidos')
        detalle_columns = ['Pedido','Producto', 'Cantidad', 'Total']
        if len(pedidos) == 0:
            last_id = 'F000'
            last_value = 1
        else:
            last_id = pedidos.tail(1).iloc[0]['Pedido']
            last_value = pedidos.tail(1).iloc[0]['#'] + 1     
        id = generate_id_purchase(last_id)
        total = 0
        #Formateo de registros (#, Pedido, Producto, Cantidad, Total)
        purchases = []
        for purchase in cart[message.chat.id]:
            total += purchase[2]
            last_value += 1
            purchases.append((id, purchase[0], purchase[1], purchase[2]))
        summary_purchase = (last_value, id, dni, total, "Pendiente")
        bot.send_message(message.chat.id, 'Compra realizada con éxito')
        delete_purchases(message.chat.id)
    except Exception as e:
        logger.error(e + '\n Usuario: ' + str(message.from_user.username) + 
                     '\n Chat ID: ' + str(message.chat.id))
        send_error_message(message)

def format_output(products):
    out_str = ''
    for product in products:
        product['Precio'] = '$' + str(product['Precio'])

def save_message_id(message):
    try:
        message_ids[message.chat.id].append(message.message_id)
    except Exception as e:
        message_ids[message.chat.id] = [message.message_id]
       
def delete_previous_message(message):
    try:
        for id in message_ids[message.chat.id]:
            bot.delete_message(message.chat.id, message_ids[id])
    except Exception as e:
        print(e)

def verify_next_records(records, page):
    size = len(records)
    max_pages = round(size / MAX_RECORDS)
    return page < max_pages

def save_current_page(chat_id, page):
    current_pages[chat_id] = page

def send_error_message(message):
    bot.send_message(message.chat.id, 'Oooops. Hubo un error al procesar la solicitud. '+ 
                     'Inténtelo de nuevo más tarde.')
    
def remember_product(id, record):
    try:
        cart[id].append(record)
    except Exception as e:
        cart[id] = [record]

def generate_id_purchase(last_id):
    match = re.match(r"([a-z]+)([0-9]+)", last_id, re.I)
    items = match.groups()
    nid = int(items[1]) + 1
    return items[0] + ("0" * (9-len(str(nid)))) + str(nid)
    

if db_manager.init_db():
    connectiondb = db_manager.get_connection()
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()

    bot.infinity_polling()
else:
    logger.error('No se pudo inicializar la base de datos')

