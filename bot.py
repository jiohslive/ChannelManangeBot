import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

BOT TOKEN = "8334244759:AAHGhLAyLYR5mEGVuy7T5Y7POttML3NvM3A"

# Thumbnail store
user_thumb = {}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send photo to set thumbnail\nSend video to apply thumbnail")

# Save thumbnail
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    thumb_path = f"thumb_{user_id}.jpg"
    await file.download_to_drive(thumb_path)
    
    user_thumb[user_id] = thumb_path
    
    await update.message.reply_text("Thumbnail saved ✅")

# Handle video
async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.channel_post or update.message
    
    if message.video:
        user_id = message.from_user.id if message.from_user else 0
        
        file = await context.bot.get_file(message.video.file_id)
        video_path = "video.mp4"
        await file.download_to_drive(video_path)

        thumb_path = user_thumb.get(user_id)

        caption = message.caption if message.caption else ""
        
        await context.bot.send_video(
            chat_id=message.chat_id,
            video=open(video_path, "rb"),
            caption=caption,
            thumbnail=open(thumb_path, "rb") if thumb_path else None,
            supports_streaming=True
        )

        os.remove(video_path)

# Rename command
async def rename(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        new_name = " ".join(context.args)
        context.user_data["rename"] = new_name
        await update.message.reply_text(f"Next video name: {new_name}")
    else:
        await update.message.reply_text("Use: /rename filename")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("rename", rename))
app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
app.add_handler(MessageHandler(filters.VIDEO, video_handler))

print("Bot Running...")
app.run_polling()
