from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, filters
)
import db, mealplans
from config import BOT_TOKEN, ACTIVITY

db.init_db()

def build_main_kb():
    kb = [
        [KeyboardButton("🧮 Підібрати раціон")],
        [KeyboardButton("📋 Залишити заявку")],
        [KeyboardButton("📞 Звʼязатися з менеджером")],
    ]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

SEX, AGE, HEIGHT, WEIGHT, ACTIVITY_Q, CITY, NAME, PHONE, CAL = range(9)

def bmr(sex, age, h, w):
    return 10*w + 6.25*h - 5*age + (5 if sex=="m" else -161)

def tdee(sex, age, h, w, activity):
    return bmr(sex, age, h, w) * ACTIVITY.get(activity,1.2)

def nearest_calories(val):
    options = [900,1200,1500,2000,2500,3000]
    return min(options, key=lambda x: abs(x-val))

async def start(u:Update,c:ContextTypes.DEFAULT_TYPE):
    caption = "<b>Привіт!</b> 👋\nЦе бот «Будь Здоров» для підбору раціону."
    await u.message.reply_photo(photo=open("assets/logo.png","rb"), caption=caption, parse_mode=ParseMode.HTML, reply_markup=build_main_kb())

async def menu(u:Update,c:ContextTypes.DEFAULT_TYPE):
    await u.message.reply_text("Меню:", reply_markup=build_main_kb())

# === Підібрати раціон ===
async def ration_entry(u:Update,c:ContextTypes.DEFAULT_TYPE):
    await u.message.reply_text("Вкажи свою стать (m/f):")
    return SEX

async def ration_sex(u:Update,c:ContextTypes.DEFAULT_TYPE):
    c.user_data['sex']=u.message.text.lower()
    await u.message.reply_text("Вік:")
    return AGE

async def ration_age(u:Update,c:ContextTypes.DEFAULT_TYPE):
    c.user_data['age']=int(u.message.text)
    await u.message.reply_text("Зріст (см):")
    return HEIGHT

async def ration_height(u:Update,c:ContextTypes.DEFAULT_TYPE):
    c.user_data['height']=float(u.message.text)
    await u.message.reply_text("Вага (кг):")
    return WEIGHT

async def ration_weight(u:Update,c:ContextTypes.DEFAULT_TYPE):
    c.user_data['weight']=float(u.message.text)
    await u.message.reply_text("Рівень активності (1-5):")
    return ACTIVITY_Q

async def ration_activity(u:Update,c:ContextTypes.DEFAULT_TYPE):
    sex,age,h,w=c.user_data['sex'],c.user_data['age'],c.user_data['height'],c.user_data['weight']
    act=int(u.message.text)
    kcal=tdee(sex,age,h,w,act)
    cal=nearest_calories(kcal)
    meals="\n".join(mealplans.sample(cal))
    await u.message.reply_text(f"Тобі підійде раціон ~{cal} ккал\nПриклад меню:\n{meals}", reply_markup=build_main_kb())
    return ConversationHandler.END

# === Заявка ===
async def order_entry(u:Update,c:ContextTypes.DEFAULT_TYPE):
    await u.message.reply_text("Оберіть калораж (900/1200/1500/2000/2500/3000):")
    return CAL

async def order_cal(u:Update,c:ContextTypes.DEFAULT_TYPE):
    c.user_data['cal']=int(u.message.text)
    await u.message.reply_text("Місто (Київ/Одеса):")
    return CITY

async def order_city(u:Update,c:ContextTypes.DEFAULT_TYPE):
    c.user_data['city']=u.message.text
    await u.message.reply_text("Імʼя:")
    return NAME

async def order_name(u:Update,c:ContextTypes.DEFAULT_TYPE):
    c.user_data['name']=u.message.text
    await u.message.reply_text("Телефон:")
    return PHONE

async def order_phone(u:Update,c:ContextTypes.DEFAULT_TYPE):
    uid=u.effective_user.id
    db.save_order(uid,c.user_data['name'],u.message.text,c.user_data['city'],c.user_data['cal'])
    await u.message.reply_text("✅ Заявку збережено! Наш менеджер звʼяжеться з вами.", reply_markup=build_main_kb())
    return ConversationHandler.END

# === Менеджер ===
async def contact_manager(u:Update,c:ContextTypes.DEFAULT_TYPE):
    await u.message.reply_text("📞 Зателефонуйте або напишіть у Viber/Telegram: +380660661411")

if __name__=="__main__":
    app=Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("Підібрати раціон"), ration_entry))
    app.add_handler(MessageHandler(filters.Regex("Залишити заявку"), order_entry))
    app.add_handler(MessageHandler(filters.Regex("Звʼязатися з менеджером"), contact_manager))
    conv_ration=ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("Підібрати раціон"), ration_entry)],
        states={SEX:[MessageHandler(filters.TEXT, ration_sex)],
                AGE:[MessageHandler(filters.TEXT, ration_age)],
                HEIGHT:[MessageHandler(filters.TEXT, ration_height)],
                WEIGHT:[MessageHandler(filters.TEXT, ration_weight)],
                ACTIVITY_Q:[MessageHandler(filters.TEXT, ration_activity)]},
        fallbacks=[]
    )
    conv_order=ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("Залишити заявку"), order_entry)],
        states={CAL:[MessageHandler(filters.TEXT, order_cal)],
                CITY:[MessageHandler(filters.TEXT, order_city)],
                NAME:[MessageHandler(filters.TEXT, order_name)],
                PHONE:[MessageHandler(filters.TEXT, order_phone)]},
        fallbacks=[]
    )
    app.add_handler(conv_ration)
    app.add_handler(conv_order)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu))
    print("Bot running...")
    app.run_polling()
