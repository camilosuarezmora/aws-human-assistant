from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / '.env')

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage

agent = Agent(
    'groq:llama-3.3-70b-versatile',
    instructions='Be concise, reply with one sentence.',
)

history: list[ModelMessage] = []

while True:
    prompt = input('Enter a prompt: ').strip()
    if prompt.lower() in ('exit', 'quit', 'q'):
        print('Goodbye.')
        break
    if not prompt:
        continue

    result = agent.run_sync(prompt, message_history=history)
    print(result.output)
    history += result.new_messages()
