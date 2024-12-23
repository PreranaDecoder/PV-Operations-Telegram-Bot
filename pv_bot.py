from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import time, datetime
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# Persistent storage for configuration
config = {
    "reminder_interval": 60,  # Default 60 seconds
    "leaderboard_time": "09:00"  # Default 9:00 AM
}

# Save and load configuration
def load_config():
    try:
        with open("config.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return config

def save_config():
    with open("config.json", "w") as file:
        json.dump(config, file)

config = load_config()

# Reminder function
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    try:
        logger.info("Sending reminder message...")
        await context.bot.send_message(chat_id, "⏰ Reminder: Please check in for today!")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

# Leaderboard update function
async def update_leaderboard(context: ContextTypes.DEFAULT_TYPE):
    leaderboard = (
        "🌟 Updated Leaderboard 🌟\n"
        "1️⃣ Alice - 200 pts\n"
        "2️⃣ Bob - 150 pts\n"
        "3️⃣ Charlie - 100 pts"
    )
    try:
        logger.info("Updating leaderboard...")
        await context.bot.send_message(context.job.data, leaderboard)
    except Exception as e:
        logger.error(f"An error occurred while updating leaderboard: {e}")

# Notify admins function
async def notify_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(ADMIN_CHAT_ID, f"🚨 New leave request from {update.message.chat.username}!")
        await update.message.reply_text("Your leave request has been forwarded to the admin.")
    except Exception as e:
        logger.error(f"An error occurred while notifying admin: {e}")

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

# Custom Commands
async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) != ADMIN_CHAT_ID:
        logger.warning(f"Unauthorized attempt to set reminders by {update.message.from_user.username} ({user_id})")
        await update.message.reply_text("🚫 You do not have permission to set reminders. Please contact the admin.")
        return

    try:
        interval = int(context.args[0])
        if interval <= 0:
            raise ValueError("Interval must be a positive integer.")
        config["reminder_interval"] = interval
        save_config()
        await update.message.reply_text(f"✅ Reminder interval set to {interval} seconds.")
        logger.info(f"Reminder interval updated to {interval} seconds by admin.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /set_reminder <positive_interval_in_seconds>")

async def set_leaderboard_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if str(user_id) != ADMIN_CHAT_ID:
        logger.warning(f"Unauthorized attempt to set leaderboard time by {update.message.from_user.username} ({user_id})")
        await update.message.reply_text("🚫 You do not have permission to set leaderboard time. Please contact the admin.")
        return

    try:
        new_time = context.args[0]
        datetime.strptime(new_time, "%H:%M")  # Validate time format
        config["leaderboard_time"] = new_time
        save_config()
        await update.message.reply_text(f"✅ Leaderboard update time set to {new_time}.")
        logger.info(f"Leaderboard time updated to {new_time} by admin.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /set_leaderboard_time <HH:MM>")

async def leaderboard_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    feedback = " ".join(context.args) if context.args else "No feedback provided."
    await update.message.reply_text(f"Thank you for your feedback: {feedback}")
    logger.info(f"Leaderboard feedback received: {feedback}")

async def taskstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = context.args[0]
        task_id = context.args[1]
        status = context.args[2]

        if user not in tasks:
            tasks[user] = {}
        tasks[user][task_id] = status
        save_tasks(tasks)

        await update.message.reply_text(f"✅ Task {task_id} for {user} updated to '{status}'.")
    except IndexError:
        await update.message.reply_text("Usage: /taskstatus <user> <task_id> <status>")

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
        "/leaderboard_feedback - Provide feedback on the leaderboard\n"
        "/set_reminder - Set the reminder interval (Admin only)\n"
        "/set_leaderboard_time - Set the leaderboard update time (Admin only)\n"
        "/taskstatus - Update or view task progress"
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
        logger.info("Starting the bot...")
        application = Application.builder().token(BOT_TOKEN).build()

        # Add Command Handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("checkin", checkin))
        application.add_handler(CommandHandler("checkout", checkout))
        application.add_handler(CommandHandler("leave", leave))
        application.add_handler(CommandHandler("leaderboard", leaderboard))
        application.add_handler(CommandHandler("leaderboard_feedback", leaderboard_feedback))
        application.add_handler(CommandHandler("set_reminder", set_reminder))
        application.add_handler(CommandHandler("set_leaderboard_time", set_leaderboard_time))
        application.add_handler(CommandHandler("taskstatus", taskstatus))
        application.add_handler(CommandHandler("contact", contact))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, default_fallback))

        # Schedule reminders using JobQueue
        if not application.job_queue:
            raise RuntimeError("JobQueue not initialized. Ensure you have installed `python-telegram-bot[job-queue]`.")

        job_queue = application.job_queue
        job_queue.run_repeating(send_reminder, interval=config["reminder_interval"], first=10, data="-4655617300")
        leaderboard_time = datetime.strptime(config["leaderboard_time"], "%H:%M").time()
        job_queue.run_daily(update_leaderboard, time=leaderboard_time, days=(0, 1, 2, 3, 4, 5, 6), data="-4655617300")

        logger.info("Bot is now polling for updates...")
        application.run_polling()
    except KeyboardInterrupt:
        logger.info("\nBot stopped gracefully. Goodbye!")

if __name__ == "__main__":
    main()
