#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import re
import logging

from setup import PROXY, TOKEN
from telegram import Bot, Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

log_actions = []


def log_action(func):
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        update = args[0]
        if update and hasattr(update, 'message') and hasattr(update, 'effective_user'):
            d = {'username': (update.effective_user.first_name,), 'funcname': (func.__name__,),
                 'message': update.message.text}
            log_actions.append(d)
            # Writing logged data into file while removing ),(,' and ,

            with open('log.txt', 'a') as handle:
                print(
                    'username: ' + re.sub(r',\(\)\'', '', str(d.get('username'))) + '\n' +
                    'funcname: ' + re.sub(r'\(\)\'', '', str(d.get('funcname'))) + '\n' +
                    'message: ' + re.sub(r'\(\)\'', '', str(d.get('message'))), file=handle)

    return inner


@log_action
def chat_history(update: Update, context: CallbackContext):
    with open('log.txt', 'r') as reader:
        i = 0
        while i < 5:  # last 5 actions 
            i += 1
            update.message.reply_text("Action number " + str(i) + " is:" + '\n')
            update.message.reply_text(str(reader.readline()))
            update.message.reply_text(str(reader.readline()))
            update.message.reply_text(str(reader.readline()))


@log_action
def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    update.message.reply_text(f'Привет, {update.effective_user.first_name}!')


@log_action
def chat_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Введи команду /start для начала. ')


@log_action
def echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')


def main():
    bot = Bot(
        token=TOKEN,
        base_url=PROXY,  # delete it if connection via VPN
    )
    updater = Updater(bot=bot, use_context=True)

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', chat_help))
    updater.dispatcher.add_handler(CommandHandler('history', chat_history))

    # on noncommand i.e message - echo the message on Telegram
    updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    logger.info('Start Bot')
    main()
