import aiohttp
import asyncio
import base64
import time
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()

client_id = os.getenv('fatsectretid')
client_secret = os.getenv('fatsectretapi')

proxy = os.getenv('proxy')
proxy_user = os.getenv('proxyuser')
proxy_password = os.getenv('proxypassword')

token_url = os.getenv('tokenurl')
api_url = os.getenv('apiurl')

ninjas_url = os.getenv('ninjasurl')
ninjas_api = os.getenv('ninjasapi')

class OAuthToken:

    def __init__(self, client_id, client_secret, token_url):
        self.TOKEN_URL = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.expires_at = 0

    async def fetch(self):
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "client_credentials",
            "scope": "basic",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.TOKEN_URL, headers=headers, data=data) as resp:
                if resp.status != 200:
                    raise Exception(f"Failed to get token, status: {resp.status}, text: {await resp.text()}")
                resp_json = await resp.json()
                self.access_token = resp_json['access_token']
                self.expires_at = time.time() + int(resp_json['expires_in'])
                return self.access_token

    def is_expired(self):
        return not self.access_token or time.time() >= self.expires_at

    async def get(self):
        if self.is_expired():
            await self.fetch()
        return self.access_token

class FatSecretApi:

    def __init__(self, client_id, client_secret, token_url, api_url, proxy, proxy_user, proxy_password):
        self.API_URL = api_url
        self.access_token = OAuthToken(client_id, client_secret, token_url)
        self.PROXY = proxy
        self.PROXY_USER = proxy_user
        self.PROXY_PASSWORD = proxy_password

    async def search(self, search_expression):
        headers = {
            "Authorization": f"Bearer {await self.access_token.get()}",
            "Content-Type": "application/json"
        }
        data = {
            "method": "foods.search",
            "search_expression": search_expression,
            "format": "json"
        }
        async with aiohttp.ClientSession() as session:
            proxy_auth = aiohttp.BasicAuth(self.PROXY_USER, self.PROXY_PASSWORD)
            async with session.post(
                self.API_URL,
                headers=headers,
                params=data,
                proxy=self.PROXY,
                proxy_auth=proxy_auth
            ) as resp:
                result = await resp.text()
                print(result)
        
                data = json.loads(result)
                desc = data['foods']['food'][0]['food_description']

                match = re.search(r'Per\s+(\d+)g\s*-\s*Calories:\s*(\d+)kcal', desc)
                if match:
                    grams = int(match.group(1))
                    calories = int(match.group(2))
                    calories_per_100g = (calories / grams) * 100
                    return (round(calories_per_100g, 2))
                else:
                    return ("Could not parse the description.")

class NinjasApi:

    def __init__(self, api_url, api_key):
        self.API_URL = api_url
        self.API_KEY = api_key
    
    async def search(self, activity, duration, weight):
        headers = {
            "X-Api-Key": self.API_KEY
        }
        params = {
            "activity": activity,
            "duration": duration,
            "weight": weight
        }
        total_cal = None
        ninja_err = None
        async with aiohttp.ClientSession() as session:
            async with session.get(self.API_URL, headers=headers, params=params) as resp:
                if resp.status != 200:
                    ninja_err += await resp.text()
                else:
                    resp_json = await resp.json()
                    try:
                        total_cal = resp_json[0]['total_calories']
                    except Exception as e:
                        ninja_err += f"Something wrong with response json: {str(e)}"
                return total_cal, ninja_err


async def main():
    api = NinjasApi(ninjas_url, ninjas_api)
    print(await api.search('swimming', 40, 65))

    # api = FatSecretApi(client_id, client_secret, token_url, api_url, proxy, proxy_user, proxy_password)
    # print(await api.search("apple"))

    # this works
    # async with aiohttp.ClientSession() as session:
    #     proxy_auth = aiohttp.BasicAuth(proxy_user, proxy_password)
    #     async with session.get("http://python.org",
    #                         proxy=proxy,
    #                         proxy_auth=proxy_auth) as resp:
    #         print(await resp.text())

if __name__ == "__main__":
    asyncio.run(main())