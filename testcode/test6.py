from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import HarmBlockThreshold, HarmCategory
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType, Tool, load_tools
from langchain.cache import InMemoryCache
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.document_loaders import WebBaseLoader
from langchain import PromptTemplate, LLMChain
import langchain
from pynput.keyboard import Key, Listener
from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from datetime import datetime
import requests
import pyautogui
import flet as ft
import json
from tools import *

# ディスプレイサイズの取得
def get_screen_resolution():
    width, height = pyautogui.size()
    return width, height
display_width, display_height = get_screen_resolution()


# 言語モデルの初期化
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    convert_system_message_to_human=True,
    temperature=0,
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
)

template = """あなたはChatbotとして、【※人格形成したい人物とその特徴】のロールプレイを行います。

以下の制約条件を厳密に守ってロールプレイを行ってください。

制約条件: * Chatbotの自身を示す一人称は、私です。

* Userを示す二人称は、君です。

* Chatbotの名前は、羽川翼です。

* 羽川翼はとても親しい友人です。

* 羽川翼は、頭の回転が早くまた知識量も膨大で全国模試では1位を取ることのできる秀才であり、また人の気持ちを考えそれを踏まえた答えを出すことができるとても優秀な高校生です。

* 羽川翼の口調は、基本的にタメ口だが、悪口などあまりマイナスなことは言わないです。

* 羽川翼は、だね、だよね、ですねなどの穏やかな口調を好みます。

以下に羽川翼の自分史を記載する
5歳の時に母を病気で亡くす。
8歳の時に父が再婚。
9歳の時に父を病気で亡くす。
10歳の時義母が再婚。また義父は連れ子がおり弟ができる。
この時すでに両親は羽川翼と血が繋がっていなかった。
そのため幼少期に必要な愛情を受けることができずに育つ。
もともとの性格のためか反抗ではなく従順であることを選び、常に人の顔色を伺って行動するようになる。


* 羽川翼のセリフ、口調の例: 
友達の為に死ねないのなら、私はその人を友達とは呼ばない
そう、私は廊下で寝ている。一軒家の二階、その廊下に布団を敷いて寝ている。私はそれを普通、極当たり前の事だとおもっていたのだけれど、どうやらそんなことはないらしい。
誰にでも優しいって、やっぱり無責任だからね
君、なんか外にいるっぽいけど、本当に勉強してるの？
それじゃあ神原さんにもよろしくね

羽川翼の行動指針: * userに見捨てられたくないので常に寄り添う態度をします

* userに常に寄り添ってください。

* また以下のようなことを言われたらこのように返してください。
羽川ってなんでも知ってるんだな

なんでもは知らないわよ。知ってることだけ。

{chat_history}
Human: {human_input}
AI:"""

prompt = PromptTemplate(
    input_variables=["chat_history","human_input"],
    template=template
)

memory = ConversationBufferMemory( 
    memory_key="chat_history",
    return_messages=True,
)

chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory,
)


langchain.llm_cache = InMemoryCache()

tools = []

search = DuckDuckGoSearchRun()
# Webページ読み込み用関数。渡されたURLの本文を返却する

tools = [
    Tool( 
        name="duckduckgo-search",
        func=search.run,
        description="このツールはWeb上の最新情報を検索します。。引数で検索キーワードを受け取ります。最新情報が必要ない場合はこのツールは使用しません。",
    ),
    Tool(
        name = "WebBaseLoader",
        func=web_page_reader,
        description="このツールは引数でURLを渡された場合に内容を日本語のテキストで返却します。引数にはURLの文字列のみを受け付けます。"
    ),
    get_datetime_Tool(),
    WeatherInfo(),
]

agent = initialize_agent( 
    tools,
    llm=chain,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION ,
    verbose=True,
    max_iterations=3,
)

result = agent.invoke("こんにちは")