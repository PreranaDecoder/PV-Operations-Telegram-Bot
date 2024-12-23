from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "7571489564:AAGT8d5Y09nebpg738iilyhzplWq3LhMbuY"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎉 Welcome to PV Operations Bot! I'm here to assist with updates and team management. Type /help to explore my features!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📜 Available Commands:\n"
        "/start - Start the bot and see the welcome message\n"
        "/help - View the list of available commands\n"
        "/checkin - Mark your daily check-in\n"
        "/checkout - Mark your daily check-out\n"
        "/leave - Request leave for a specific day\n"
        "/leaderboard - View the team leaderboard\n"
        "/taskstatus - Update or view task progress\n"
        "/contact - Get support from the admin team"
    )

async def checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Your check-in has been recorded successfully. Have a productive day!")

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Your check-out has been recorded. See you tomorrow!")

async def leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📅 Please provide the following details for your leave request:\n- Date(s)\n- Reason\nOnce submitted, your manager will review it."
    )

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 Team Leaderboard 🌟\n1️⃣ [Name] - 120 points\n2️⃣ [Name] - 105 points\n3️⃣ [Name] - 98 points\nKeep up the great work! 🚀"
    )

async def taskstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📝 Please enter the task ID and the updated status (e.g., In Progress, Completed, Blocked).\nExample: \nTask ID: #1234\nStatus: Completed"
    )

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 Need help? Contact your admin team:\n- Email: admin@persistventures.com\n- Telegram: @adminsupport"
    )

async def default_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤔 I didn’t understand that. Type /help to see what I can do for you!")

def main():
    print("Starting the bot...")  # Print message for bot startup
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("checkin", checkin))
    application.add_handler(CommandHandler("checkout", checkout))
    application.add_handler(CommandHandler("leave", leave))
    application.add_handler(CommandHandler("leaderboard", leaderboard))
    application.add_handler(CommandHandler("taskstatus", taskstatus))
    application.add_handler(CommandHandler("contact", contact))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, default_fallback))

    print("Bot is now polling for updates...")  # Print message when polling starts
    application.run_polling()

if __name__ == "__main__":
    main()
