from channels.generic.websocket import AsyncWebsocketConsumer
import json
import httpx
from mistletoe import markdown

from matematics.settings import AI_API_KEY, AI_MODEL


class AI(AsyncWebsocketConsumer):
    API_KEY = AI_API_KEY
    MODEL = AI_MODEL

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        def process_content(content):
            return content.replace('<think>', '').replace('</think>', '')

        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.MODEL,
            "messages": [{"role": "user", "content": message}],
            "stream": True
        }

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status_code != 200:
                    print("Ошибка API:", response.status_code)
                    return

                full_response = []

                async for chunk in response.aiter_lines():
                    if chunk:
                        chunk_str = chunk.replace('data: ', '')
                        try:
                            chunk_json = json.loads(chunk_str)
                            if "choices" in chunk_json:
                                content = chunk_json["choices"][0]["delta"].get("content", "")
                                if content:
                                    cleaned = process_content(content)
                                    full_response.append(cleaned)
                                    await self.send(text_data=json.dumps({
                                        'message': markdown(''.join(full_response)),
                                    }))
                        except json.JSONDecodeError:
                            pass
            