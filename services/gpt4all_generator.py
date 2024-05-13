from gpt4all import GPT4All

model = GPT4All("mistral-7b-openorca.gguf2.Q4_0.gguf")


async def generate_answer(sometext: str) -> list:
    with model.chat_session():
        while True:
            prompt = sometext
            if prompt.lower() == 'хватит':
                break

            response = model.generate(prompt=prompt, temp=0)
            return list(response)
