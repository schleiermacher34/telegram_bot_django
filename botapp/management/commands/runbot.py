# botapp/management/commands/runbot.py

from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler,
)
from botapp.models import UserData, VideoLink
import logging
from urllib.parse import urlparse

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define conversation states
SERIAL_NUMBER = range(1)

class Command(BaseCommand):
    help = 'Runs the Telegram bot'

    def handle(self, *args, **options):
        TOKEN = '7694697246:AAEh9x7IO4i44Y7KOn618DP2WRp8BJQiIX8'
        if not TOKEN:
            self.stdout.write(self.style.ERROR('TELEGRAM_BOT_TOKEN not set in settings'))
            return

        updater = Updater(TOKEN)
        dispatcher = updater.dispatcher

        # Conversation handler for registration
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                SERIAL_NUMBER: [MessageHandler(Filters.text & ~Filters.command, self.serial_number)],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )

        # Add handlers to dispatcher
        dispatcher.add_handler(conv_handler)
        dispatcher.add_handler(CommandHandler('help', self.help_command))
        dispatcher.add_handler(CommandHandler('finish', self.finish_command))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_message))

        # Start the bot
        updater.start_polling()
        logger.info("Bot started. Press Ctrl+C to stop.")
        updater.idle()

    # Start command handler
    def start(self, update: Update, context: CallbackContext) -> int:
        user = update.message.from_user
        chat_id = update.message.chat_id
        context.user_data['telegram_username'] = user.username
        context.user_data['chat_id'] = chat_id

        # Check if the user already exists
        if UserData.objects.filter(chat_id=chat_id).exists():
            update.message.reply_text(
                'You are already registered. You can send me video links at any time.'
            )
            return ConversationHandler.END
        else:
            update.message.reply_text(
                'Welcome! Please enter your product serial number to register:'
            )
            return SERIAL_NUMBER

    # Serial number handler
    def serial_number(self, update: Update, context: CallbackContext) -> int:
        serial_number = update.message.text.strip()
        context.user_data['serial_number'] = serial_number
        chat_id = context.user_data.get('chat_id')

        # Check if the serial number is already registered
        if UserData.objects.filter(serial_number=serial_number).exists():
            update.message.reply_text(
                'This serial number is already registered. Please enter a valid serial number:'
            )
            return SERIAL_NUMBER

        # Save the new user data
        user_data = UserData(
            telegram_username=context.user_data.get('telegram_username'),
            chat_id=chat_id,
            serial_number=serial_number
        )
        user_data.save()

        update.message.reply_text(
            'Registration successful! You can now send me video links at any time.'
        )
        return ConversationHandler.END

    # Help command handler
    def help_command(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text(
            'Welcome to the bot! Here are some commands you can use:\n'
            '/start - Register yourself.\n'
            '/finish - Get a summary of your submissions.\n'
            '/cancel - Cancel the current operation.\n'
            '/help - Display this help message.\n\n'
            'You can send video links at any time. Each valid video link you send will be saved and assigned a unique lottery ticket number.'
        )

    # Finish command handler
    def finish_command(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.message.chat_id

        # Check if the user is registered
        if not UserData.objects.filter(chat_id=chat_id).exists():
            update.message.reply_text(
                'You are not registered yet. Please send /start to begin.'
            )
            return

        user_data = UserData.objects.get(chat_id=chat_id)
        total_links = VideoLink.objects.filter(user=user_data).count()

        update.message.reply_text(
            f"Thank you for participating! You have submitted {total_links} video link(s). Each one has its own lottery ticket number."
        )

    # Cancel command handler
    def cancel(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text('Operation canceled.')
        return ConversationHandler.END

    # Message handler for processing video links
    def handle_message(self, update: Update, context: CallbackContext) -> None:
        message_text = update.message.text.strip()
        chat_id = update.message.chat_id

        # Check if the user is registered
        if not UserData.objects.filter(chat_id=chat_id).exists():
            update.message.reply_text(
                'Hello! It looks like you have not registered yet. Please send /start to begin.'
            )
            return

        user_data = UserData.objects.get(chat_id=chat_id)

        # Check if the message is a valid video link
        if self.is_valid_video_link(message_text):
            video_link = message_text

            # Check if the video link has already been provided
            if VideoLink.objects.filter(user=user_data, video_link=video_link).exists():
                update.message.reply_text('You have already submitted this video link.')
                return

            # Save the new video link
            video_entry = VideoLink.objects.create(user=user_data, video_link=video_link)

            # Send the lottery ticket number (VideoLink id)
            lottery_ticket_number = video_entry.id  # VideoLink primary key
            update.message.reply_text(
                f"Thank you! Your video link has been saved. Your lottery ticket number is {lottery_ticket_number}."
            )

        else:
            update.message.reply_text('Please send a valid video link or use /help for commands.')

    # Method to validate video links
    def is_valid_video_link(self, text: str) -> bool:
        # Simple URL validation (you can enhance this with regex for specific platforms)
        parsed = urlparse(text)
        return all([parsed.scheme, parsed.netloc])

