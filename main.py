import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

myid = 0
choices = []
ids = []
ended = False

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start a poll with .args as options."""
    choices.clear()
    ids.clear()
    options = context.args
    keyboard = []
    casted = 0
    cdata = 1
    if len(options) < 3:
        await context.bot.send_message(chat_id=update.message.chat_id, text='Please give at least three options.')
    else:
        for i in options:
            keyboard.append([InlineKeyboardButton(i, callback_data=str(cdata))])
            cdata += 1
        OPTLEN = len(options)
        context.bot_data.update({'optionlen': OPTLEN, 'options': options, 'casted': casted})
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Please choose three options in descending order of preference.", reply_markup=reply_markup)

async def lenn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.message.chat_id, text=context.bot_data['optionlen'])

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.message.chat_id,
    text="Type /start and options separated by spaces after it to start a poll.\nNote that the RCV voting does not work with less than 3 options. It is not reccomended to use too many options as well.\nTo sum up the poll type /wrapup.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not ended:
        if query.from_user.id not in ids:
            ids.append(query.from_user.id)
            choices.append([int(query.data)])
        else:
            if len(choices[ids.index(query.from_user.id)]) <= 3:
                if int(query.data) not in choices[ids.index(query.from_user.id)]:
                    choices[ids.index(query.from_user.id)].append(int(query.data))





async def wrapup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    choicesr = choices.copy()
    for i in choicesr:
        if len(i) != 3:
            choicesr.remove(i)
    elected = False
    votecount = []
    OPTLEN = context.bot_data['optionlen']
    for i in range(OPTLEN):
        votecount.append(0)
    wraptext = ''
    banlist = []
    round = 1
    while not elected:

        for i in choicesr:
            for a in banlist:
                if a + 1 in i:
                    i.remove(a + 1)
        for i in choicesr:
            votecount[i[0] - 1] += 1

        if max(votecount) > len(choicesr) / 2 or len(banlist) == OPTLEN:
            wraptext += 'Results for round ' + str(round) + ':\n'
            for i in range(OPTLEN):
                if i in banlist:
                    wraptext += context.bot_data['options'][i] + ' - DQd\n'
                else:
                    wraptext += context.bot_data['options'][i] + ' - ' + str(votecount[i]) + '\n'
            wraptext += 'Voting concluded.'
            elected = True

        else:

            wraptext += 'Results for round ' + str(round) + ':\n'
            for i in range(OPTLEN):
                if i in banlist:
                    wraptext += context.bot_data['options'][i] + ' - DQd\n'
                else:
                    wraptext += context.bot_data['options'][i] + ' - ' + str(votecount[i]) + '\n'

            round += 1
            newmin = 999999
            minc = []
            for i in range(OPTLEN):
                if i not in banlist:
                    if votecount[i] < newmin:
                        newmin = votecount[i]
            for i in range(OPTLEN):
                if i not in banlist:
                    if votecount[i] == newmin:
                        minc.append(i)
            if len(minc) == OPTLEN - len(banlist):
                wraptext += 'Voting concluded.'
                break
            else:
                for i in minc:
                    banlist.append(i)

            votecount = []
            for i in range(OPTLEN):
                votecount.append(0)




    await context.bot.send_message(chat_id=update.message.chat_id, text=wraptext)





def main() -> None:
    """Run the bot."""
    application = Application.builder().token("your_token_here").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("wrapup", wrapup))
    application.add_handler(CommandHandler("l", lenn))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CallbackQueryHandler(button))



    application.run_polling()


if __name__ == "__main__":
    main()

