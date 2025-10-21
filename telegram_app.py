import pickle

from telegram import Update, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ConversationHandler, ContextTypes
from recommendation_model import RecommendationSystem

BOT_TOKEN = 'YOUR BOT TOKEN'

COMMANDS = [
    BotCommand("start", "Запуск бота"),
    BotCommand("help", "Справка")
]

gender_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Male", callback_data="male"),
        InlineKeyboardButton(text="Female", callback_data="female")],
    ]
)

exp_level_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="1", callback_data="1"),
        InlineKeyboardButton(text="2", callback_data="2"),
        InlineKeyboardButton(text="3", callback_data="3")],
    ]
)

muscle_group_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Chest", callback_data="chest"),
        InlineKeyboardButton(text="Triceps", callback_data="triceps"),
        InlineKeyboardButton(text="Biceps", callback_data="biceps"),
        InlineKeyboardButton(text="Shoulders", callback_data="shoulders")],
        [InlineKeyboardButton(text="Core", callback_data="core"),
        InlineKeyboardButton(text="Back", callback_data="back"),
        InlineKeyboardButton(text="Obliques", callback_data="obliques")],
        [InlineKeyboardButton(text="Glutes", callback_data="glutes"),
        InlineKeyboardButton(text="Quadriceps", callback_data="quadriceps"),
        InlineKeyboardButton(text="Hips", callback_data="hips"),
        InlineKeyboardButton(text="Calves", callback_data="calves")],
        [InlineKeyboardButton(text="Full Body", callback_data="full body")]
    ]
)

difficulty_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Begginer", callback_data="begginer"),
        InlineKeyboardButton(text="Intermediate", callback_data="intermediate"),
        InlineKeyboardButton(text="Advanced", callback_data="advanced")],
    ]
)

ASK_GENDER, ASK_EXP_LEVEL, ASK_MUSCLE, ASK_DIFF_LVL = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! I\'m a bot to help ypu choose the best excercises!\n\n' \
    'Specify your gender:', reply_markup=gender_kb)
    return ASK_GENDER

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = 'I\'m a bot to help you choose exercises! \n' \
    'To select optimal exercises press start command and specify your gender, physical activity, muscle group, and difficulty level of the exercise.'
    await update.message.reply_text(help_text)

async def got_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["gender"] = query.data
    await query.edit_message_text("Specify your experience level:", reply_markup=exp_level_kb)
    return ASK_EXP_LEVEL

async def got_exp_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["exp_level"] = query.data
    await query.edit_message_text("Specify target muscle group:", reply_markup=muscle_group_kb)
    return ASK_MUSCLE

async def got_muscle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["muscle_group"] = query.data
    await query.edit_message_text("Specify difficulty level:", reply_markup=difficulty_kb)
    return ASK_DIFF_LVL

async def got_diff_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["diff_level"] = query.data
    
    gender =context.user_data.get("gender")
    exp_level =context.user_data.get("exp_level")
    muscle_group =context.user_data.get("muscle_group")
    diff_level =context.user_data.get("diff_level")

    await query.edit_message_text(f'Your parametrs:\nGender: {gender}\nExperience level: {exp_level}\nTarget muscle group: {muscle_group}\nDifficulty level: {diff_level}')

    with open("./data/fitness_recommender.pkl", "rb") as model_file:
        model = pickle.load(model_file)
    excercises = model.get_recommendation(gender, exp_level, muscle_group, diff_level, 5)

    excercises_for_print = ''
    for i in range(len(excercises)):
        excercises_for_print += f'{i + 1}. {excercises[i]}\n'

    await query.message.reply_text(f'Here\'s what I can suggest:\n{excercises_for_print}')
    
    context.user_data.clear()
    return ConversationHandler.END

async def post_init(application):
    await application.bot.set_my_commands(COMMANDS)

if __name__ == '__main__':
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_GENDER: [CallbackQueryHandler(got_gender)],
            ASK_EXP_LEVEL: [CallbackQueryHandler(got_exp_level)],
            ASK_MUSCLE: [CallbackQueryHandler(got_muscle)],
            ASK_DIFF_LVL: [CallbackQueryHandler(got_diff_level)]
        },
        fallbacks=[],
    )

    application.add_handler(conv)
    application.add_handler(CommandHandler('help', help))

    application.run_polling()