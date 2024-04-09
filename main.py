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

"""

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
)
memory.save_context(
    {
        "input":template
    },
    {
        "output":"わかりました。ロールプレイを開始します。"
    }
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
    door_state(),
]

agent = initialize_agent( 
    tools,
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    max_iterations=3,
)

def reset_memory():
    memory.chat_memory.messages = []
    memory.save_context(
        {
            "input":template
        },
        {
            "output":"わかりました。ロールプレイを開始します。"
        }
    )


# ウィンドウ処理
class Message():
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type
        self.timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment="start"
        self.controls=[
                ft.CircleAvatar(
                    content=ft.Text(self.get_initials(message.user_name)),
                    color=ft.colors.WHITE,
                    bgcolor=self.get_avatar_color(message.user_name),
                ),
                ft.Column(
                    [
                        ft.Row(controls=[ft.Text(message.user_name, weight="bold"),ft.Text(message.timestamp)]),
                        ft.Text(message.text, selectable=True, overflow="ellipsis", width=int(display_width/3)-100),
                    ],
                    tight=True,
                    spacing=5,
                ),
            ]

    def get_initials(self, user_name: str):
        if user_name:
            return user_name[:1].capitalize()
        else:
            return "Unknown"  # or any default value you prefer

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.colors.AMBER,
            ft.colors.BLUE,
            ft.colors.BROWN,
            ft.colors.CYAN,
            ft.colors.GREEN,
            ft.colors.INDIGO,
            ft.colors.LIME,
            ft.colors.ORANGE,
            ft.colors.PINK,
            ft.colors.PURPLE,
            ft.colors.RED,
            ft.colors.TEAL,
            ft.colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]

def main(page: ft.Page):

    # キーボード入力の監視
    input_key = {Key.shift: False, Key.space: False}
    def on_press(key):
        if key == Key.shift or key == Key.space:
            input_key[key] = True
        if input_key[Key.shift] and input_key[Key.space]:
            page.window_always_on_top = True 
            text_input.focus()
            page.update()
            x, y = pyautogui.position()
            pyautogui.moveTo(100,display_height-50)
            pyautogui.click()
            pyautogui.moveTo(x, y)
            page.window_always_on_top = False
            page.update()

    def on_release(key):
        if key == Key.shift or key == Key.space:
            input_key[key] = False

    l = Listener(
            on_press=on_press,
            on_release=on_release)
    l.start()


    def generate_text(text: str):
        try:
            res = agent.invoke(text)
            return res
        except Exception as e:
            print(e)
            return {"output":str(e)}

    def send_message_click(e):
        if text_input.value != "":
            if text_input.value == "reset":
                reset_memory()
                page.pubsub.send_all(Message("Gemini", "会話ログをリセットしました。", message_type="login_message"))
                text_input.value = ""
                text_input.focus()
                page.update()
            else:
                page.pubsub.send_all(Message("User", text_input.value, message_type="chat_message"))
                rq = text_input.value
                text_input.value = ""
                text_input.focus()
                page.update()
                res = generate_text(rq)["output"]
                # res = "hi"
                page.pubsub.send_all(Message("Gemini", res, message_type="chat_message"))

                page.update()

    def on_message(message: Message):
        if message.message_type == "chat_message":
            m = ChatMessage(message)
            chat.controls.append(m)
            page.update()
        elif message.message_type == "login_message":
            m = ft.Text(message.text, italic=True, color=ft.colors.INDIGO_ACCENT_100, size=12)
            chat.controls.append(m)
            page.update()

    page.pubsub.subscribe(on_message)

    page.window_width = int(int(display_width)/3)
    page.window_height = int(display_height)
    page.window_minimizable = False  # 最小化ボタン
    page.window_maximizable = False  # 最大化ボタン
    page.window_top = 0
    page.window_left = 0
    page.window_opacity = 0.7
    page.window_resizable = False
    page.update()

    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
        width=page.window_width, 
    )

    text_input = ft.TextField(
            hint_text="Message Gemini",
            multiline=True,
            min_lines=1,
            max_lines=3,
            expand=True,
            filled=True,
            shift_enter=True,
            on_submit=send_message_click,
    )

    button = ft.IconButton(
        icon=ft.icons.ARROW_UPWARD,
        on_click=send_message_click,
    )

    content = ft.Row(controls=[text_input, button], alignment=ft.MainAxisAlignment.END)

    page.add(
        ft.Container(
            content=chat,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        ),
        content
    )
    text_input.focus()
    page.update()

if __name__ == "__main__":
    ft.app(main)