import telebot
import pickle
import io
import subprocess
import numpy as np
from PIL import Image
import cv2  

botToken = '7091070745:AAFpMcvkh5X6gFDfMPxPxALZhofdcBdtTSE'
bot = telebot.TeleBot(botToken, parse_mode=None)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Please send me a black and white image to colorize.")
    

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)  

       
        with open('temp_image.jpg', 'wb') as new_file:
            new_file.write(downloaded_file)

        
        subprocess.run(['python', 'yt_project.py', '--image', 'temp_image.jpg'])

        
        with open('colorized_image.pickle', 'rb') as f:
            colorized_image = pickle.load(f)

        
        colorized_image = cv2.cvtColor(colorized_image, cv2.COLOR_BGR2RGB)

        
        img_byte_arr = io.BytesIO()
        colorized_img_pil = Image.fromarray(colorized_image)
        colorized_img_pil.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        
        bot.send_photo(message.chat.id, photo=img_byte_arr)
    except Exception as e:
        bot.reply_to(message, "An error occurred. Please try again.")

if __name__ == '__main__':
    
    bot.polling()
