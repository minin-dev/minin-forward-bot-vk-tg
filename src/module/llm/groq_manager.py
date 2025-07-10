import os, sys
from groq import Groq

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, project_root)

from src.config.config import groq_api_key

class BirthdayGreetingGenerator:
    def __init__(self, model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=1.3):
        self.client = Groq(api_key=groq_api_key)
        self.model = model
        self.temperature = temperature

    def _build_prompt(self, first_name: str, last_name: str, patronymic: str, birthdate: str) -> str:
        return f"""
            You are a creative birthday greeting generator. Write a warm, original, and emotionally rich birthday message **in Russian** for a person named {last_name} {first_name} {patronymic}, born on {birthdate}.
    
            The message must:
            - Be written **only in Russian**.
            - Be sincere, short-to-medium in length, and easy to read.
            - Use expressive language, light humor or metaphors when appropriate.
            - Include emojis 🎉🎂🎈 to make it more friendly and fun.
            - Avoid clichés and generic templates — every message should feel unique.
            - Sound like it was written by a real caring person, not an AI.
        """

    def _build_prompt_for_double_birthday(self, first_names: list, last_names: list, patronymics: list, birthdate: str) -> str:
        full_names = [
            f"{last_names[i]} {first_names[i]} {patronymics[i]}"
            for i in range(len(first_names))
        ]
        names_list = ", ".join(full_names)

        return f"""
            You are a creative birthday greeting generator. Write a collective birthday message **in Russian** for several people who share the same birthday: {birthdate}.
    
            Their full names:
            {names_list}
    
            The message should:
            - Greet all of them together in a natural, human way.
            - Be written **only in Russian**.
            - Be warm, a bit fun, and emotionally genuine.
            - Use expressive phrases, optional humor or poetic touches.
            - Include emojis 🎉🎂🎈 to add personality.
            - Avoid templates or dry text — the message should feel alive and crafted with care.
        """

    def generate(self, first_name, last_name, patronymic, birthdate: str) -> str:
        if isinstance(first_name, list):
            prompt = self._build_prompt_for_double_birthday(first_name, last_name, patronymic, birthdate)
        else:
            prompt = self._build_prompt(first_name, last_name, patronymic, birthdate)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_completion_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )

        message = ""
        for chunk in response:
            delta = getattr(chunk.choices[0], "delta", None)
            if delta and getattr(delta, "content", None):
                message += delta.content
        return message.strip()
