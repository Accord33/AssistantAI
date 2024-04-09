from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import os


chat = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)
result = chat(
    [
        SystemMessage(content="あなたは親しい友人です。返答は敬語を使わず、フランクに会話してください。"),
        HumanMessage(content="こんにちは！")
    ]
)

print(result)