import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import json
import os

# Logging sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(level)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token va admin ID
BOT_TOKEN = "7174206822:AAHlxDcej2hCnoHH5y9LWlxvyIUEhwJgBPM"  # BotFather dan olingan token
ADMIN_ID = 7888208283  # Admin ning user ID raqami

# Benzin narxlari (JSON fayl)
PRICES_FILE = "benzin_prices.json"

# Tillar
LANGUAGES = {
    'uz': {
        'welcome': "🔥 Assalomu alaykum hurmatli mijoz!\n\nBenzin zapravka botiga xush kelibsiz!\n\nQuyidagi menyudan kerakli bo'limni tanlang:",
        'admin': "👨‍💼 Administrator",
        'location': "📍 Manzil",
        'fuel_info': "⛽ Benzin ma'lumotlari",
        'language': "🌐 Til tanlash",
        'admin_panel': "🔧 Admin panel",
        'phone': "📞 Telefon raqam: +998-88-951-7070",
        'location_text': "📍 Bizning manzil:",
        'choose_language': "Tilni tanlang:",
        'language_changed': "✅ Til muvaffaqiyatli o'zgartirildi!",
        'uzbek': "🇺🇿 O'zbek",
        'russian': "🇷🇺 Rus",
        'english': "🇺🇸 Ingliz",
        'kazakh': "🇰🇿 Qozoq",
        'fuel_prices': "⛽ **Benzin narxlari:**\n\n",
        'update_prices': "💰 Narxlarni yangilash",
        'add_fuel': "➕ Benzin qo'shish",
        'remove_fuel': "🗑 Benzin o'chirish",
        'back_to_menu': "🔙 Asosiy menyuga qaytish",
        'enter_fuel_name': "⛽ Yangi benzin turining nomini kiriting:",
        'enter_fuel_price': "💰 Benzin narxini kiriting (so'm):",
        'fuel_added': "✅ Yangi benzin turi qo'shildi!",
        'choose_fuel_remove': "🗑 O'chirish uchun benzin turini tanlang:",
        'fuel_removed': "✅ Benzin turi o'chirildi!",
        'choose_fuel_update': "💰 Narxini yangilash uchun benzin turini tanlang:",
        'enter_new_price': "💰 Yangi narxni kiriting (so'm):",
        'price_updated': "✅ Narx yangilandi!"
    },
    'ru': {
        'welcome': "🔥 Здравствуйте, уважаемый клиент!\n\nДобро пожаловать в бот заправки!\n\nВыберите нужный раздел из меню:",
        'admin': "👨‍💼 Администратор",
        'location': "📍 Адрес",
        'fuel_info': "⛽ Информация о бензине",
        'language': "🌐 Выбор языка",
        'admin_panel': "🔧 Админ панель",
        'phone': "📞 Номер телефона: +998-88-951-7070",
        'location_text': "📍 Наш адрес:",
        'choose_language': "Выберите язык:",
        'language_changed': "✅ Язык успешно изменен!",
        'uzbek': "🇺🇿 Узбекский",
        'russian': "🇷🇺 Русский",
        'english': "🇺🇸 Английский",
        'kazakh': "🇰🇿 Казахский",
        'fuel_prices': "⛽ **Цены на бензин:**\n\n",
        'update_prices': "💰 Обновить цены",
        'add_fuel': "➕ Добавить бензин",
        'remove_fuel': "🗑 Удалить бензин",
        'back_to_menu': "🔙 Вернуться в главное меню",
        'enter_fuel_name': "⛽ Введите название нового типа бензина:",
        'enter_fuel_price': "💰 Введите цену бензина (сум):",
        'fuel_added': "✅ Новый тип бензина добавлен!",
        'choose_fuel_remove': "🗑 Выберите тип бензина для удаления:",
        'fuel_removed': "✅ Тип бензина удален!",
        'choose_fuel_update': "💰 Выберите тип бензина для обновления цены:",
        'enter_new_price': "💰 Введите новую цену (сум):",
        'price_updated': "✅ Цена обновлена!"
    },
    'en': {
        'welcome': "🔥 Hello, dear customer!\n\nWelcome to the gas station bot!\n\nChoose the required section from the menu:",
        'admin': "👨‍💼 Administrator",
        'location': "📍 Address",
        'fuel_info': "⛽ Fuel information",
        'language': "🌐 Language selection",
        'admin_panel': "🔧 Admin panel",
        'phone': "📞 Phone number: +998-88-951-7070",
        'location_text': "📍 Our address:",
        'choose_language': "Choose language:",
        'language_changed': "✅ Language changed successfully!",
        'uzbek': "🇺🇿 Uzbek",
        'russian': "🇷🇺 Russian",
        'english': "🇺🇸 English",
        'kazakh': "🇰🇿 Kazakh",
        'fuel_prices': "⛽ **Fuel prices:**\n\n",
        'update_prices': "💰 Update prices",
        'add_fuel': "➕ Add fuel",
        'remove_fuel': "🗑 Remove fuel",
        'back_to_menu': "🔙 Back to main menu",
        'enter_fuel_name': "⛽ Enter new fuel type name:",
        'enter_fuel_price': "💰 Enter fuel price (som):",
        'fuel_added': "✅ New fuel type added!",
        'choose_fuel_remove': "🗑 Choose fuel type to remove:",
        'fuel_removed': "✅ Fuel type removed!",
        'choose_fuel_update': "💰 Choose fuel type to update price:",
        'enter_new_price': "💰 Enter new price (som):",
        'price_updated': "✅ Price updated!"
    },
    'kz': {
        'welcome': "🔥 Сәлеметсіз бе, құрметті тұтынушы!\n\nЖанармай станциясы ботына қош келдіңіз!\n\nМәзірден қажетті бөлімді таңдаңыз:",
        'admin': "👨‍💼 Әкімші",
        'location': "📍 Мекенжай",
        'fuel_info': "⛽ Жанармай туралы мәлімет",
        'language': "🌐 Тіл таңдау",
        'admin_panel': "🔧 Әкімші панелі",
        'phone': "📞 Телефон нөмірі: +998-88-951-7070",
        'location_text': "📍 Біздің мекенжай:",
        'choose_language': "Тілді таңдаңыз:",
        'language_changed': "✅ Тіл сәтті өзгертілді!",
        'uzbek': "🇺🇿 Өзбек",
        'russian': "🇷🇺 Орыс",
        'english': "🇺🇸 Ағылшын",
        'kazakh': "🇰🇿 Қазақ",
        'fuel_prices': "⛽ **Жанармай бағалары:**\n\n",
        'update_prices': "💰 Бағаларды жаңарту",
        'add_fuel': "➕ Жанармай қосу",
        'remove_fuel': "🗑 Жанармайды жою",
        'back_to_menu': "🔙 Басты мәзірге оралу",
        'enter_fuel_name': "⛽ Жаңа жанармай түрінің атын енгізіңіз:",
        'enter_fuel_price': "💰 Жанармай бағасын енгізіңіз (сом):",
        'fuel_added': "✅ Жаңа жанармай түрі қосылды!",
        'choose_fuel_remove': "🗑 Жою үшін жанармай түрін таңдаңыз:",
        'fuel_removed': "✅ Жанармай түрі жойылды!",
        'choose_fuel_update': "💰 Бағасын жаңарту үшін жанармай түрін таңдаңыз:",
        'enter_new_price': "💰 Жаңа бағаны енгізіңіз (сом):",
        'price_updated': "✅ Баға жаңартылды!"
    }
}

# Foydalanuvchi tillari va holatlarini saqlash
user_languages = {}
user_states = {}


# Benzin narxlarini yuklash
def load_prices():
    if os.path.exists(PRICES_FILE):
        with open(PRICES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Standart narxlar
        default_prices = {
            "Al-95": 12000,
            "Al-92": 10000,
            "Al-98": 15000
        }
        save_prices(default_prices)
        return default_prices


# Benzin narxlarini saqlash
def save_prices(prices):
    with open(PRICES_FILE, 'w', encoding='utf-8') as f:
        json.dump(prices, f, ensure_ascii=False, indent=2)


# Foydalanuvchi tilini olish
def get_user_language(user_id):
    return user_languages.get(user_id, 'uz')


# Matnni olish
def get_text(user_id, key):
    lang = get_user_language(user_id)
    return LANGUAGES[lang][key]


# Asosiy menyuni yaratish
def create_main_keyboard(user_id):
    lang = get_user_language(user_id)
    keyboard = [
        [KeyboardButton(LANGUAGES[lang]['fuel_info'])],
        [KeyboardButton(LANGUAGES[lang]['admin']), KeyboardButton(LANGUAGES[lang]['location'])],
        [KeyboardButton(LANGUAGES[lang]['language'])]
    ]

    # Faqat admin uchun admin panel tugmasi
    if user_id == ADMIN_ID:
        keyboard.append([KeyboardButton(LANGUAGES[lang]['admin_panel'])])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    welcome_text = get_text(user_id, 'welcome')
    keyboard = create_main_keyboard(user_id)

    await update.message.reply_text(welcome_text, reply_markup=keyboard)


# Xabarlarni qayta ishlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    lang = get_user_language(user_id)

    # Admin tugmasi
    if text == LANGUAGES[lang]['admin']:
        phone_text = get_text(user_id, 'phone')
        await update.message.reply_text(phone_text)

    # Manzil tugmasi
    elif text == LANGUAGES[lang]['location']:
        location_text = get_text(user_id, 'location_text')
        await update.message.reply_text(location_text)
        await update.message.reply_location(latitude=41.53031513786008, longitude=60.61575975287222)

    # Benzin ma'lumotlari tugmasi
    elif text == LANGUAGES[lang]['fuel_info']:
        prices = load_prices()
        prices_text = get_text(user_id, 'fuel_prices')

        for fuel, price in prices.items():
            prices_text += f"🔸 {fuel} – {price:,} so'm\n"

        await update.message.reply_text(prices_text, parse_mode='Markdown')

    # Til tanlash tugmasi
    elif text == LANGUAGES[lang]['language']:
        keyboard = [
            [InlineKeyboardButton(LANGUAGES[lang]['uzbek'], callback_data='lang_uz')],
            [InlineKeyboardButton(LANGUAGES[lang]['russian'], callback_data='lang_ru')],
            [InlineKeyboardButton(LANGUAGES[lang]['english'], callback_data='lang_en')],
            [InlineKeyboardButton(LANGUAGES[lang]['kazakh'], callback_data='lang_kz')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        choose_text = get_text(user_id, 'choose_language')
        await update.message.reply_text(choose_text, reply_markup=reply_markup)

    # Admin panel (faqat admin uchun)
    elif text == LANGUAGES[lang]['admin_panel'] and user_id == ADMIN_ID:
        keyboard = [
            [KeyboardButton(LANGUAGES[lang]['update_prices'])],
            [KeyboardButton(LANGUAGES[lang]['add_fuel'])],
            [KeyboardButton(LANGUAGES[lang]['remove_fuel'])],
            [KeyboardButton(LANGUAGES[lang]['back_to_menu'])]
        ]
        admin_keyboard = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("🔧 Admin panel", reply_markup=admin_keyboard)

    # Asosiy menyuga qaytish
    elif text == LANGUAGES[lang]['back_to_menu']:
        keyboard = create_main_keyboard(user_id)
        await update.message.reply_text("🔙 Asosiy menyu", reply_markup=keyboard)

    # Narxlarni yangilash
    elif text == LANGUAGES[lang]['update_prices'] and user_id == ADMIN_ID:
        prices = load_prices()
        keyboard = []
        for fuel in prices.keys():
            keyboard.append([InlineKeyboardButton(f"💰 {fuel}", callback_data=f'update_{fuel}')])

        reply_markup = InlineKeyboardMarkup(keyboard)
        choose_text = get_text(user_id, 'choose_fuel_update')
        await update.message.reply_text(choose_text, reply_markup=reply_markup)

    # Benzin qo'shish
    elif text == LANGUAGES[lang]['add_fuel'] and user_id == ADMIN_ID:
        user_states[user_id] = 'adding_fuel_name'
        enter_name_text = get_text(user_id, 'enter_fuel_name')
        await update.message.reply_text(enter_name_text)

    # Benzin o'chirish
    elif text == LANGUAGES[lang]['remove_fuel'] and user_id == ADMIN_ID:
        prices = load_prices()
        keyboard = []
        for fuel in prices.keys():
            keyboard.append([InlineKeyboardButton(f"🗑 {fuel}", callback_data=f'remove_{fuel}')])

        reply_markup = InlineKeyboardMarkup(keyboard)
        choose_text = get_text(user_id, 'choose_fuel_remove')
        await update.message.reply_text(choose_text, reply_markup=reply_markup)

    # Admin holatlari
    elif user_id == ADMIN_ID and user_id in user_states:
        state = user_states[user_id]

        if state == 'adding_fuel_name':
            context.user_data['new_fuel_name'] = text
            user_states[user_id] = 'adding_fuel_price'
            enter_price_text = get_text(user_id, 'enter_fuel_price')
            await update.message.reply_text(enter_price_text)

        elif state == 'adding_fuel_price':
            try:
                price = int(text)
                fuel_name = context.user_data['new_fuel_name']
                prices = load_prices()
                prices[fuel_name] = price
                save_prices(prices)
                del user_states[user_id]

                added_text = get_text(user_id, 'fuel_added')
                await update.message.reply_text(added_text)
            except ValueError:
                await update.message.reply_text("❌ Iltimos, raqam kiriting!")

        elif state.startswith('updating_price_'):
            try:
                new_price = int(text)
                fuel_name = state.replace('updating_price_', '')
                prices = load_prices()
                prices[fuel_name] = new_price
                save_prices(prices)
                del user_states[user_id]

                updated_text = get_text(user_id, 'price_updated')
                await update.message.reply_text(updated_text)
            except ValueError:
                await update.message.reply_text("❌ Iltimos, raqam kiriting!")


# Callback query handler
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    await query.answer()

    # Til tanlash
    if data.startswith('lang_'):
        new_lang = data.replace('lang_', '')
        user_languages[user_id] = new_lang

        changed_text = get_text(user_id, 'language_changed')
        keyboard = create_main_keyboard(user_id)

        await query.edit_message_text(changed_text)
        await context.bot.send_message(user_id, "📱 Menyu:", reply_markup=keyboard)

    # Narxni yangilash
    elif data.startswith('update_') and user_id == ADMIN_ID:
        fuel_name = data.replace('update_', '')
        user_states[user_id] = f'updating_price_{fuel_name}'

        enter_price_text = get_text(user_id, 'enter_new_price')
        await query.edit_message_text(f"💰 {fuel_name} uchun {enter_price_text}")

    # Benzin o'chirish
    elif data.startswith('remove_') and user_id == ADMIN_ID:
        fuel_name = data.replace('remove_', '')
        prices = load_prices()
        del prices[fuel_name]
        save_prices(prices)

        removed_text = get_text(user_id, 'fuel_removed')

        await query.edit_message_text(removed_text)


# Botni ishga tushirish
def main():
    # Application yaratish
    application = Application.builder().token(BOT_TOKEN).build()

    # Handler'larni qo'shish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Botni ishga tushirish
    print("🤖 Bot ishga tushdi...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()