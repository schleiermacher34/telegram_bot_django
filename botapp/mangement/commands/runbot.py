from django.core.management.base import BaseCommand
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler,
)
from botapp.models import UserData
from django.conf import settings
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define conversation states
SERIAL_NUMBER, VIDEO_LINK, ADD_ANOTHER_LINK = range(3)

class Command(BaseCommand):
    help = 'Runs the Telegram bot'

    def handle(self, *args, **options):
        TOKEN = '7475654881:AAE5F-BsDJaos-L1qb2_EgEZcOgoMTWQNG0'
        if not TOKEN:
            self.stdout.write(self.style.ERROR('7475654881:AAE5F-BsDJaos-L1qb2_EgEZcOgoMTWQNG0'))
            return

        updater = Updater(TOKEN)
        dispatcher = updater.dispatcher

        # Handlers
  # In the handle() method inside the Command class

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                SERIAL_NUMBER: [MessageHandler(Filters.text & ~Filters.command, self.serial_number)],
                VIDEO_LINK: [MessageHandler(Filters.text & ~Filters.command, self.video_link)],
                ADD_ANOTHER_LINK: [MessageHandler(Filters.text & ~Filters.command, self.add_another_link)],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )


        dispatcher.add_handler(conv_handler)

        # Start the bot
        updater.start_polling()
        logger.info("Bot started. Press Ctrl+C to stop.")
        updater.idle()

    # Handler methods
def start(self, update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    chat_id = update.message.chat_id
    context.user_data['telegram_username'] = user.username
    context.user_data['chat_id'] = chat_id

    # Check if the user already exists
    if UserData.objects.filter(chat_id=chat_id).exists():
        update.message.reply_text(
            'You have already registered your serial number. '
            'Would you like to add a new video link? (yes/no)'
        )
        return ADD_ANOTHER_LINK
    else:
        update.message.reply_text(
            'Hello! Please enter your product serial number:'
        )
        return SERIAL_NUMBER

def add_another_link(self, update: Update, context: CallbackContext) -> int:
    response = update.message.text.strip().lower()
    if response in ['yes', 'y']:
        update.message.reply_text('Please send me the new video link:')
        return VIDEO_LINK
    elif response in ['no', 'n']:
        update.message.reply_text('Okay, let me know if you need anything else.')
        return ConversationHandler.END
    else:
        update.message.reply_text('Please reply with "yes" or "no".')
        return ADD_ANOTHER_LINK


def serial_number(self, update: Update, context: CallbackContext) -> int:
    serial_number = update.message.text.strip()
    context.user_data['serial_number'] = serial_number

    # Check if the serial number is already registered
    if UserData.objects.filter(serial_number=serial_number).exists():
        update.message.reply_text(
            'This serial number is already registered. Please enter a valid serial number:'
        )
        return SERIAL_NUMBER

    # Save the new user data
    user_data = UserData(
        telegram_username=context.user_data.get('telegram_username'),
        chat_id=context.user_data.get('chat_id'),
        serial_number=serial_number
    )
    user_data.save()

    update.message.reply_text(
        'Serial number registered successfully! Please send me the video link:'
    )
    return VIDEO_LINK

def video_link(self, update: Update, context: CallbackContext) -> int:
    video_link = update.message.text.strip()
    context.user_data['video_link'] = video_link
    chat_id = context.user_data.get('chat_id')

    # Retrieve the user data
    user_data = UserData.objects.get(chat_id=chat_id)

    # Check if the video link has already been provided
    if VideoLink.objects.filter(user=user_data, video_link=video_link).exists():
        update.message.reply_text('You have already provided this video link. Please send a new one:')
        return VIDEO_LINK

    # Save the new video link
    video_entry = VideoLink(
        user=user_data,
        video_link=video_link
    )
    video_entry.save()

    update.message.reply_text('Thank you! Your video link has been saved.')
    update.message.reply_text('Would you like to add another video link? (yes/no)')
    return ADD_ANOTHER_LINK


    def cancel(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text('Operation canceled.')
        return ConversationHandler.END
