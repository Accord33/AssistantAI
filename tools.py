from langchain.document_loaders import WebBaseLoader
from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from datetime import datetime
import requests
import flet as ft
import json
import requests

def web_page_reader(url: str) -> str:
    loader = WebBaseLoader(url)
    content = loader.load()[0].page_content
    return content

# 気象データの取得関数
def get_weather_info(latitude_and_longitude):
    latitude, longitude = latitude_and_longitude.split(":")
    base_url = "https://api.open-meteo.com/v1/forecast"
    parameters = {
        "latitude": latitude,
        "longitude": longitude,
        #        "current_weather": "true",
        # "hourly": "temperature_2m,relativehumidity_2m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_mean",
        "forecast_days": "3",
        "timezone": "Asia/Tokyo"
    }
    response = requests.get(base_url, params=parameters)
    if response.status_code == 200:
        data = response.json()
        return json.dumps(data)
    else:
        return None
    
class WeatherInfoInput(BaseModel):
  latitude_and_longitude: str = Field(descption = "latitude:longitude")

class WeatherInfo(BaseTool):
  name = 'get_weather_info'
  description = "天気予報を知りたいときに便利です。latitude_and_longitudeに緯度:経度の形式で入力してください。"
  args_schema: Type[BaseModel] = WeatherInfoInput
  def _run(self, latitude_and_longitude: str):
    return get_weather_info(latitude_and_longitude)
  def _arun(self, ticker: str):
    raise NotImplementedError("get_stock_performance does not support async")


# 現在の日時を取得するツール
class get_datetime_Tool(BaseTool):
    """このツールは現在の日時を取得します。このツールは引数は不要です。"""

    name = "get_datetime_Tool"
    description = (
        "このツールはpythonのdatetimeモジュールを使用して現在の日時を取得します。"
        "Input should be empty."
    )

    def _run(self, any=None) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async def _arun(self, name: str = None) -> str:
        """Use the HelloTool asynchronously."""
        return self._run(name)
    
class door_state(BaseTool):
    "このツールはドアの鍵の状態を確認したり、変更したりします。"
    name = "door_state"
    description = (
        "このツールはドアの鍵の状態を取得したり変更したりします。"
        "引数controlは、stateまたはopenまたはcloseを取ります"
        "引数のstateは、ドアの鍵の状態を取得します。戻り値がopenの場合ドアの鍵が開いています。closedの場合ドアの鍵が閉まっています。"
        "引数のopenは、ドアの鍵を開けます。"
        "引数のcloseは、ドアの鍵を閉めます。"
    )
    def _run(self, control):
        host = "192.168.135.110"
        if control == "state":
            return requests.get(f"http://{host}:5000/state").text
        elif control == "open":
            return requests.get(f"http://{host}:5000/open").text
        elif control == "close":
            return requests.get(f"http://{host}:5000/close").text
        else:
            return "Invalid control"
        
    async def _arun(self, name: str = None) -> str:
        """Use the HelloTool asynchronously."""
        return self._run(name)