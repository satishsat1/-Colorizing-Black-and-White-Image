import telebot
import pickle
from PIL import Image
import io
import subprocess

botToken = '7091070745:AAFpMcvkh5X6gFDfMPxPxALZhofdcBdtTSE'
bot = telebot.TeleBot(botToken, parse_mode=None)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Please send me a black and white image to colorize.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        # Download the photo
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Save the photo to a temporary file
        with open('temp_image.jpg', 'wb') as new_file:
            new_file.write(downloaded_file)

        # Call your image processing script here, ensure it saves the colorized image to a pickle file
        # For example, subprocess.run(['python', 'yt_project.py', '--image', 'temp_image.jpg'])
        # Make sure to adjust the command according to how your script accepts arguments
        subprocess.run(['python', 'yt_project.py', '--image', 'temp_image.jpg'])
        
        # Assuming your script has saved the colorized image to 'colorized_image.pickle'
        with open('colorized_image.pickle', 'rb') as f:
            colorized_image = pickle.load(f)

        # Convert the colorized image to a format that can be sent by Telegram
        img_byte_arr = io.BytesIO()
        colorized_image = Image.fromarray(colorized_image)
        colorized_image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        # Send the colorized image back to the user
        bot.send_photo(message.chat.id, photo=img_byte_arr)
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")

if __name__ == '__main__':
    bot.polling()
