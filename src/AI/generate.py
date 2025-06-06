from openai import AsyncOpenAI
import numpy as np
from pydub import AudioSegment
import os
import io
import whisper

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("API_TOKEN"),
)

openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate(messages: list):
    try:
        completion = await client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=messages
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Ошибка при генерации ответа: {str(e)}")
        return "Извините, произошла ошибка при обработке запроса"


def speech_to_text():
    audio = AudioSegment.from_file("audio.ogg", format="ogg")
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

    samples = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0 

    model = whisper.load_model("base")
    result = model.transcribe(audio=samples)
    return result["text"]
    
