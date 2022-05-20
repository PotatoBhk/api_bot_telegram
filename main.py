import os
from tabnanny import check
import telebot
import logging
from dotenv import load_dotenv
from telebot import types
from tabulate import tabulate
from db_manager import xlst_db
from db_manager import psql_db
from db_manager import psql_product_model
from db_manager import psql_purchase_model

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
PRODUCT_COLUMNS = ['Código', 'Nombre', 'Precio']
PRODUCT_COLUMNS_EXTENDED = ['Código', 'Nombre', 'Precio', 'Descripción', 'Categoría']
CART_COLUMNS = ['Código', 'Nombre', 'Cantidad', 'Total']

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
        markup.add(*buttons) 
        msg = bot.send_message(message.chat.id, "Escoge una opción: ", reply_markup=markup)
        save_message_id(msg)
    except Exception as e:
        logger.error(str(e) + '\n Usuario: ' + str(message.from_user.username) + 
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
        buttons.append(types.InlineKeyboardButton('Menú principal', callback_data='backmenu'))
        markup.add(*buttons)
        msg = bot.send_message(query.message.chat.id, "Escoja una opción: ", reply_markup=markup)  
        save_message_id(msg)
    except Exception as e:
        logger.error(str(e) + '\n Usuario: ' + str(query.message.from_user.username) + 
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
        (results, rows) = product_class.get_products(page, connectiondb)
        results = list(map(lambda x: x[1:4], results))        
        records = tabulate(results, headers=PRODUCT_COLUMNS, tablefmt='fancy_grid')
        bot.send_message(query.message.chat.id, f'<pre>Listado de productos: \n' + records + '</pre>', parse_mode='HTML')
        markup = types.InlineKeyboardMarkup(row_width=1)
        buttons = []
        buttons.append(types.InlineKeyboardButton('Añadir producto al carrito de compras', callback_data='addcart'))
        buttons.append(types.InlineKeyboardButton('Procesar compra', callback_data='process'))
        buttons.append(types.InlineKeyboardButton('Quitar producto del carrito de compras', callback_data='deleteproduct'))
        if verify_next_records(rows, page):
            buttons.append(types.InlineKeyboardButton('Mostrar más productos', callback_data='showmore'))
            current_pages[query.message.chat.id] = page + 1            
        buttons.append(types.InlineKeyboardButton('Cancelar', callback_data='cancel'))
        markup.add(*buttons)
        msg = bot.send_message(query.message.chat.id, "Escoja una opción: ", reply_markup=markup)
        save_message_id(msg) 
    except Exception as e:
        logger.error(str(e) + '\n Usuario: ' + str(query.message.from_user.username) + 
                     '\n Chat ID: ' + str(query.message.chat.id))
        send_error_message(query.message)

@bot.callback_query_handler(lambda query: query.data == "carrito")
def list_cart(query):
    if not list_cart_products(query.message):
        return
    try:
        markup = types.InlineKeyboardMarkup(row_width=1)
        buttons = []
        buttons.append(types.InlineKeyboardButton('Procesar compra', callback_data='process'))
        buttons.append(types.InlineKeyboardButton('Quitar producto del carrito de compras', callback_data='deleteproduct'))
        markup.add(*buttons)
        bot.send_message(query.message.chat.id, "Escoja una opción: ", reply_markup=markup)
    except Exception as e:
        logger.error(str(e) + '\n Usuario: ' + str(query.message.from_user.username) + 
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
        logger.error(str(e) + '\n Usuario: ' + str(query.message.from_user.username) + 
                     '\n Chat ID: ' + str(query.message.chat.id))
        send_error_message(query.message)

@bot.callback_query_handler(lambda query: query.data == "process")
def process_purchase(query):
    save_purchase(query.message.chat.id, query.message)
    
@bot.callback_query_handler(lambda query: query.data == "showmore")
def show_more(query):
    page = current_pages[query.message.chat.id]
    list_all(query, page)

@bot.callback_query_handler(lambda query: query.data == "cancel")
def cancel_purchase(query):
    forget_products(query.message.chat.id)
    bot.send_message(query.message.chat.id, 'Compra cancelada. Se ha eliminado los productos del carrito de compras.')

@bot.callback_query_handler(lambda query: query.data == "deleteproduct")
def delete_product(query):
    # TODO: Implementar
    if not list_cart_products(query.message):
        return
    try:
        msg = bot.send_message(query.message.chat.id, 'Escriba el código del producto a eliminar: ')
        bot.register_next_step_handler(msg, delete_product_step)
    except Exception as e:
        logger.error(str(e) + '\n Usuario: ' + str(query.message.from_user.username) + 
                     '\n Chat ID: ' + str(query.message.chat.id))
        send_error_message(query.message)

def add_to_cart_step(message):
    try:
        data = message.text.split(';')
        quant = data[1].strip()
        if not quant.isdigit():
            msg = bot.send_message(message, 'La cantidad debe ser un número. Ingrese nuevamente: (Ejemplo: ABCD;5)')
            bot.register_next_step_handler(msg, add_to_cart_step)
            return
        quant = int(quant)
        code = str(data[0]).strip()        
        result = product_class.get_product(code, connectiondb)
        if(result is None):
            bot.send_message(message.chat.id, "El código no existe. Ingrese uno válido: (Ejemplo: ABCD;5)")
            bot.register_next_step_handler(message, add_to_cart_step)
            return
        total = result[3] * quant
        purchase = (result[0], result[1], result[2], quant, total)
        remember_product(message.chat.id, purchase)
        bot.send_message(message.chat.id, 'Producto agregado al carrito de compras')
    except Exception as e:
        logger.error(str(e) + '\n Usuario: ' + str(message.from_user.username) + 
                     '\n Chat ID: ' + str(message.chat.id))
        send_error_message(message)

def list_cart_products(message):
    try:
        if check_cart(message):
            bot.send_message(message.chat.id, 'Carrito de compras vacío')
            return False
        products = list(map(lambda x: x[1:5], cart[message.chat.id]))
        result = tabulate(products, headers=CART_COLUMNS, tablefmt='fancy_grid')
        bot.send_message(message.chat.id, f'<pre>Listado de productos en el carrito de compras: \n' 
                         + result + '</pre>', parse_mode='HTML') 
        return True       
    except Exception as e:
        logger.error(str(e) + '\n Usuario: ' + str(message.from_user.username) + 
                     '\n Chat ID: ' + str(message.chat.id))
        send_error_message(message)
        return False

def save_purchase(user, message):
    try:        
        if check_cart(message):
            bot.send_message(message.chat.id, 'No hay productos en el carrito de compras')
            return
        total = sum(map(lambda x: x[4], cart[message.chat.id]))
        #Formateo de registros (#, Pedido, Producto, Cantidad, Total)
        next_purchase = purchase_class.get_next_id_purchase(connectiondb)
        data_purchase = (next_purchase, user, total, 'Pendiente')
        new_purchase = purchase_class.add_purchase(data_purchase, connectiondb)
        print('New Purchase: ', new_purchase)
        for detail in cart[message.chat.id]:
            detail = (new_purchase[0], detail[0], detail[3], detail[4])
            if not purchase_class.add_detail(detail, connectiondb):
                logger.error('Error al agregar detalle de compra. Usuario: ' + str(message.from_user.username) + 
                             '\n Chat ID: ' + str(message.chat.id))
                send_error_message(message)
                return
        bot.send_message(message.chat.id, 'Compra realizada con éxito. Código de comprobante: ' 
                         + str(new_purchase[1] + '. Código de usuario: ' + str(new_purchase[2])))
        forget_products(message.chat.id)
    except Exception as e:
        print('Error: ', e)
        logger.error(str(e) + '\n Usuario: ' + str(message.from_user.username) + 
                     '\n Chat ID: ' + str(message.chat.id))
        send_error_message(message)

def delete_product_step(message):
    try:
        code = message.text.strip()
        index_list = list(map(lambda x: x[1] == code, cart[message.chat.id]))
        if True not in index_list:
            bot.send_message(message.chat.id, 'El código no existe. Ingrese uno válido:')
            bot.register_next_step_handler(message, delete_product_step)
            return
        cart[message.chat.id].pop(index_list.index(True))
        bot.send_message(message.chat.id, 'Producto eliminado del carrito de compras')
    except Exception as e:
        logger.error(str(e) + '\n Usuario: ' + str(message.from_user.username) + 
                     '\n Chat ID: ' + str(message.chat.id))
        send_error_message(message)

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

def verify_next_records(rows, page):
    max_pages = round(rows[0] / MAX_RECORDS)
    return page < max_pages

def save_current_page(chat_id, page):
    current_pages[chat_id] = page

def send_error_message(message):
    bot.send_message(message.chat.id, 'Oooops. Hubo un error al procesar la solicitud. '+ 
                     'Inténtelo de nuevo más tarde.')
    
def check_cart(message):
    try:
        return (len(cart[message.chat.id]) == 0)
    except:
        return True

def remember_product(id, record):
    try:
        cart[id].append(record)
    except Exception as e:
        cart[id] = [record]    

def forget_products(id):
    try:
        cart.pop(id)
    except Exception as e:
        pass

if db_manager.init_db():
    print('Base de datos inicializada')
    connectiondb = db_manager.get_connection()
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()

    bot.infinity_polling()
else:
    logger.error('No se pudo inicializar la base de datos')

