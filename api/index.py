import os
import subprocess
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Directories setup
HOSTING_DIR = "my_hosting_server"
SCRIPTS_DIR = "live_scripts"

for folder in [HOSTING_DIR, SCRIPTS_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Running processes ko track karne ke liye dictionary
running_processes = {}

# 🔒 SECURITY: Aapka Telegram User ID set kar diya gaya hai
ADMIN_USER_ID = 8372837217

def is_admin(user_id):
    return user_id == ADMIN_USER_ID

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Aapko is bot ko use karne ki anumati (permission) nahi hai.")
        return

    await update.message.reply_text(
        "👋 **Welcome to your Telegram Hosting Bot!**\n\n"
        "**Available Commands:**\n"
        "📁 `/create <name>` - Naya hosting folder/project banayein\n"
        "📂 `/list` - Sabhi projects ki list dekhein\n"
        "🛑 `/stop <filename.py>` - Chal rahi Python script ko band karein\n\n"
        "💡 *Aap seedha koi bhi `.py` file bhej kar use live kar sakte ہیں!*"
    )

# /create command: Naya folder/website banane ke liye
async def create_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text("⚠️ Kripya project ka naam dein. Example: `/create mywebsite`")
        return

    project_name = context.args[0]
    project_path = os.path.join(HOSTING_DIR, project_name)

    try:
        if not os.path.exists(project_path):
            os.makedirs(project_path)
            
            # Default index.php file
            index_file = os.path.join(project_path, "index.php")
            with open(index_file, "w") as f:
                f.write("<?php echo 'Hello from Telegram Hosting Bot!'; ?>")

            await update.message.reply_text(
                f"✅ Success! Project **'{project_name}'** create ho gaya hai.\n"
                f"📁 Folder path: `{project_path}`"
            )
        else:
            await update.message.reply_text(f"⚠️ Project **'{project_name}'** pehle se exist karta hai!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error aaya: {str(e)}")

# /list command: Saare projects dekhne ke liye
async def list_projects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    try:
        projects = os.listdir(HOSTING_DIR)
        if not projects:
            await update.message.reply_text("📁 Aapke hosting server par abhi koi project nahi hai.")
            return
        
        project_list = "\n".join([f"🔹 {p}" for p in projects])
        await update.message.reply_text(f"📂 **Aapke Hosted Projects:**\n\n{project_list}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# File Upload Handler: .py file aate hi run karna
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Aap authorized nahi hain.")
        return

    document = update.message.document
    
    if not document.file_name.endswith('.py'):
        await update.message.reply_text("❌ Kripya sirf valid `.py` file upload karein!")
        return

    try:
        file = await context.bot.get_file(document.file_id)
        file_path = os.path.join(SCRIPTS_DIR, document.file_name)
        await file.download_to_drive(file_path)

        # Agar pehle se same naam ki script chal rahi hai toh use pehle rok dein
        if document.file_name in running_processes:
            try:
                running_processes[document.file_name].terminate()
            except:
                pass

        # Script ko background mein run karna
        process = subprocess.Popen(['python3', file_path])
        running_processes[document.file_name] = process
        
        await update.message.reply_text(
            f"🚀 Success! Script **{document.file_name}** live ho gayi hai.\n"
            f"💻 Process ID (PID): `{process.pid}`"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Script run karne mein error: {str(e)}")

# /stop command: Script band karne ke liye
async def stop_script(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text("⚠️ Kripya file ka naam dein. Example: `/stop script.py`")
        return

    filename = context.args[0]
    
    if filename in running_processes:
        try:
            process = running_processes[filename]
            process.terminate()  # Process rokna
            del running_processes[filename]
            await update.message.reply_text(f"🛑 Script **{filename}** ko successfully band kar diya gaya hai.")
        except Exception as e:
            await update.message.reply_text(f"❌ Rokne mein error aaya: {str(e)}")
    else:
        await update.message.reply_text(f"❌ '{filename}' naam ki koi active script run nahi ho rahi hai.")

if __name__ == '__main__':
    # Aapka Bot Token yahan daal diya gaya hai
    TOKEN = "8868389563:AAEK2-SWGgmt5B88oR6Ny3KbdmcpHLvb-0U"
    
    application = ApplicationBuilder().token(TOKEN).build()

    # Handlers register kar rahe hain
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('create', create_project))
    application.add_handler(CommandHandler('list', list_projects))
    application.add_handler(CommandHandler('stop', stop_script))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    print("🤖 Hosting Bot successfully start ho gaya hai...")
    application.run_polling()
