import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Создаем или подключаемся к базе данных SQLite
conn = sqlite3.connect('articles.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        url TEXT UNIQUE
    )
''')
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = (
        "Привет! Я бот, который поможет не забыть прочитать статьи, найденные тобой в интернете :)\n"
        "Чтобы я запомнил статью, достаточно передать мне ссылку на нее. К примеру https://example.com.\n"
        "Чтобы получить случайную статью, достаточно передать мне команду /get_article.\n"
        "Но помни! Отдавая статью тебе на прочтение, я удаляю её из своей базы. Так что тебе точно нужно ее изучить!"
    )
    await update.message.reply_text(welcome_message)

async def add_article(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text  # Получаем текст сообщения
    user_id = update.message.from_user.id  # Получаем ID пользователя
    if url.startswith("http://") or url.startswith("https://"):
        try:
            # Вставляем URL в базу данных
            cursor.execute("INSERT INTO articles (user_id, url) VALUES (?, ?)", (user_id, url))
            conn.commit()  # Сохраняем изменения в базе данных
            await update.message.reply_text(f"Ссылка добавлена: {url}")
        except sqlite3.IntegrityError:
            await update.message.reply_text("Эта ссылка уже добавлена.")
    else:
        await update.message.reply_text("Пожалуйста, укажите корректный URL.")


async def get_article(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    cursor.execute('SELECT url FROM articles WHERE user_id = ? ORDER BY RANDOM() LIMIT 1', (user_id,))
    article = cursor.fetchone()
    if article:
        await update.message.reply_text(f"Вот случайная статья: {article[0]}")
        cursor.execute('DELETE FROM articles WHERE url = ? AND user_id = ?', (article[0], user_id))
        conn.commit()
    else:
        await update.message.reply_text("Статей нет.")

def main() -> None:
    application = ApplicationBuilder().token("7372639776:AAF5GoLix2NOqyQtybYIk467A8CXNDm2qgk").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("get_article", get_article))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_article))  # Добавлен обработчик для команды
    application.run_polling()

if __name__ == '__main__':
    main()