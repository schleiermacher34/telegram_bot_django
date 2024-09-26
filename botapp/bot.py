import os
import sys
# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telegram_bot.settings')

import django
django.setup()

import logging
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler,
)
import os
TOKEN = "7694697246:AAEh9x7IO4i44Y7KOn618DP2WRp8BJQiIX8"
print(f"TOKEN: {TOKEN}")  # Debugging statement

if not TOKEN:
    print("Error: TELEGRAM_BOT_TOKEN environment variable is not set.")
    exit(1)

updater = Updater(TOKEN)




from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base

from sqlalchemy.orm import sessionmaker

# Enable logging for debugging purposes
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define conversation states
SERIAL_NUMBER, VIDEO_LINK = range(2)

# Set up the database using SQLAlchemy
Base = declarative_base()

class UserData(Base):
    __tablename__ = 'user_data'
    id = Column(Integer, primary_key=True)
    telegram_username = Column(String)
    chat_id = Column(Integer)
    serial_number = Column(String)
    video_link = Column(String)

engine = create_engine('sqlite:///user_data.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    context.user_data['telegram_username'] = user.username
    context.user_data['chat_id'] = update.message.chat_id

    update.message.reply_text(
        'Hello! Please enter your product serial number:'
    )
    return SERIAL_NUMBER

def serial_number(update: Update, context: CallbackContext) -> int:
    context.user_data['serial_number'] = update.message.text

    update.message.reply_text(
        'Got it! Now, please send me the video link:'
    )
    return VIDEO_LINK

def video_link(update: Update, context: CallbackContext) -> int:
    context.user_data['video_link'] = update.message.text

    # Save data to the database
    session = Session()
    user_data = UserData(
        telegram_username=context.user_data['telegram_username'],
        chat_id=context.user_data['chat_id'],
        serial_number=context.user_data['serial_number'],
        video_link=context.user_data['video_link']
    )
    session.add(user_data)
    session.commit()
    session.close()

    update.message.reply_text('Thank you! Your information has been saved.')
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Operation canceled.')
    return ConversationHandler.END

def main() -> None:
    # Insert your bot's API token here
    updater = Updater("7475654881:AAE5F-BsDJaos-L1qb2_EgEZcOgoMTWQNG0")

    dispatcher = updater.dispatcher

    # Set up the ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SERIAL_NUMBER: [MessageHandler(Filters.text & ~Filters.command, serial_number)],
            VIDEO_LINK: [MessageHandler(Filters.text & ~Filters.command, video_link)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the bot
    updater.start_polling()
    logger.info("Bot started. Press Ctrl+C to stop.")
    updater.idle()

if __name__ == '__main__':
    main()
