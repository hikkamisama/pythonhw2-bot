import os
from dotenv import load_dotenv

load_dotenv()

telegram_token = os.getenv("telegramapi")

openweather_url = os.getenv("openweatherurl")
openweather_token = os.getenv("openweatherapi")

token_url = os.getenv('tokenurl')
api_url = os.getenv('apiurl')

client_id = os.getenv('fatsectretid')
client_secret = os.getenv('fatsectretapi')

admin_id = int(os.getenv("adminid"))

proxy = os.getenv('proxy')
proxy_user = os.getenv('proxyuser')
proxy_password = os.getenv('proxypassword')

ninjas_url = os.getenv('ninjasurl')
ninjas_api = os.getenv('ninjasapi')

defaults = {
    'weight': 70,
    'height': 170,
    'age': 30,
    'water_norm': 70 * 30,
    'activity_goal': 30,
    'city': 'Moscow',
    'calorie_goal': 10 * 70 + 6.25 * 170 - 5 * 30
}
