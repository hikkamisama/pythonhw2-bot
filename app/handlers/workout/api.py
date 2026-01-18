import aiohttp

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
        ninja_err = ""
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