from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import time
import json

BOT_TOKEN = "7571489564:AAGT8d5Y09nebpg738iilyhzplWq3LhMbuY"
ADMIN_CHAT_ID = "8168610115"

# Reminder function
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = "-4655617300"  # Replace with your bot's chat ID or group ID
    print("Sending reminder message...")  # Log the event
    await context.bot.send_message(chat_id, "⏰ Reminder: Please check in for today!")

# Leaderboard update function
async def update_leaderboard(context: ContextTypes.DEFAULT_TYPE):
    leaderboard = (
        "🌟 Updated Leaderboard 🌟\n"
        "1️⃣ Alice - 200 pts\n"
        "2️⃣ Bob - 150 pts\n"
        "3️⃣ Charlie - 100 pts"
    )
    await context.bot.send_message(context.job.chat_id, leaderboard)

# Notify admins function
async def notify_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(ADMIN_CHAT_ID, f"🚨 New leave request from {update.message.chat.username}!")
    await update.message.reply_text("Your leave request has been forwarded to the admin.")

# Task persistence
def load_tasks():
    try:
        with open("tasks.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_tasks(tasks):
    with open("tasks.json", "w") as file:
        json.dump(tasks, file)

tasks = load_tasks()

async def taskstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_id = context.args[0] if context.args else None
    status = context.args[1] if len(context.args) > 1 else None

    if task_id and status:
        tasks[task_id] = status
        save_tasks(tasks)
        await update.message.reply_text(f"✅ Task {task_id} updated to '{status}'.")
    else:
        await update.message.reply_text("Usage: /taskstatus <task_id> <status>")

# Command Handlers
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
    await notify_admin(update, context)

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 Team Leaderboard 🌟\n1️⃣ Alice - 200 pts\n2️⃣ Bob - 150 pts\n3️⃣ Charlie - 100 pts\nKeep up the great work! 🚀"
    )

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 Need help? Contact your admin team:\n- Email: admin@persistventures.com\n- Telegram: @adminsupport"
    )

async def default_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤔 I didn’t understand that. Type /help to see what I can do for you!")

# Main function
def main():
    try:
        print("Starting the bot...")
        application = Application.builder().token(BOT_TOKEN).build()

        # Add Command Handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("checkin", checkin))
        application.add_handler(CommandHandler("checkout", checkout))
        application.add_handler(CommandHandler("leave", leave))
        application.add_handler(CommandHandler("leaderboard", leaderboard))
        application.add_handler(CommandHandler("taskstatus", taskstatus))
        application.add_handler(CommandHandler("contact", contact))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, default_fallback))

        # Schedule reminders using JobQueue
        if not application.job_queue:
            raise RuntimeError("JobQueue not initialized. Ensure you have installed `python-telegram-bot[job-queue]`.")
        job_queue = application.job_queue
        # job_queue.run_repeating(send_reminder, interval=60, first=10)  # Sends every 60 seconds
        job_queue.run_daily(update_leaderboard, time=time(9, 0), days=(0, 1, 2, 3, 4, 5, 6))  # Daily at 9:00 AM

        print("Bot is now polling for updates...")
        application.run_polling()
    except KeyboardInterrupt:
        print("\nBot stopped gracefully. Goodbye!")

if __name__ == "__main__":
    main()
