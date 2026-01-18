import aiohttp
import base64
import time
import json
import re

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
        calories_per_100g = None
        api_error = []
        try:
            async with aiohttp.ClientSession() as session:
                proxy_auth = aiohttp.BasicAuth(self.PROXY_USER, self.PROXY_PASSWORD)
                try:
                    async with session.post(
                        self.API_URL,
                        headers=headers,
                        params=data,
                        proxy=self.PROXY,
                        proxy_auth=proxy_auth
                    ) as resp:
                        if resp.status != 200:
                            api_error.append(f"HTTP error: {resp.status}")
                            result = await resp.text()
                            api_error.append(f"Response body: {result}")
                        else:
                            result = await resp.text()
                            try:
                                data = json.loads(result)
                                desc = data['foods']['food'][0]['food_description']
                                match = re.search(r'Per\s+(\d+)g\s*-\s*Calories:\s*(\d+)kcal', desc)
                                if match:
                                    grams = int(match.group(1))
                                    calories = int(match.group(2))
                                    calories_per_100g = round((calories / grams) * 100)
                                else:
                                    api_error.append("Could not parse the food description with regex.")
                            except Exception as e:
                                api_error.append(f"JSON or parsing error: {str(e)}")
                except Exception as e:
                    api_error.append(f"Network or session error: {str(e)}")
        except Exception as e:
            api_error.append(f"ClientSession error: {str(e)}")

        return (calories_per_100g, api_error)
