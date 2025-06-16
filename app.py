import os
import threading
import json
import requests
import paho.mqtt.client as mqtt
from linebot import LineBotApi
from linebot.models import TextSendMessage
from flask import Flask

# 初始化 Flask（Render 需要 Web server 才會保持活著）
app = Flask(__name__)

@app.route("/")
def index():
    return "✅ MQTT + LINE Bot 服務啟動中"

# ===== LINE Bot 設定 =====
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
user_id = os.getenv("LINE_USER_ID")  # 要接收訊息的使用者 ID

# ===== MQTT 設定 =====
MQTT_BROKER = "broker.emqx.io"  # 可改為其他 broker
MQTT_PORT = 1883
MQTT_TOPIC = "chatbotjohnisluckbot"

# ===== MQTT 回呼函式 =====
def on_connect(client, userdata, flags, rc):
    print("✅ MQTT 已連線，訂閱主題：", MQTT_TOPIC)
    client.subscribe(MQTT_TOPIC)

import json
import requests

def on_message(client, userdata, msg):
    print("📥 MQTT 收到：", msg.payload)

    try:
        payload = json.loads(msg.payload.decode())
        people = payload.get("people")
        values = payload.get("values", [])
        if not values:
            return

        value = values[0]

        if value == 1:
            line_bot_api.push_message(user_id, TextSendMessage(text="⚠️ 可能有人"))

        elif value == 2:
            # 模擬 LINE 使用者傳送 "人臉辨識"
            webhook_url = os.getenv("https://mqtt-vwcn.onrender.com/callback")  # 例如：https://你的專案.onrender.com/callback

            # 模擬 LINE 傳來的 webhook JSON 結構
            fake_event = {
                "events": [{
                    "type": "message",
                    "message": {
                        "type": "text",
                        "text": "人臉辨識"
                    },
                    "source": {
                        "type": "user",
                        "userId": user_id
                    },
                    "replyToken": "00000000000000000000000000000000"  # 假的 token，會被忽略
                }]
            }

            try:
                res = requests.post(webhook_url, json=fake_event, timeout=5)
                if res.status_code == 200:
                    print("✅ 模擬 webhook 傳送成功")
                else:
                    print("❌ webhook 回應錯誤：", res.status_code, res.text)
            except Exception as e:
                print("❌ 模擬 webhook 錯誤：", str(e))

    except Exception as e:
        print("❌ JSON 處理錯誤：", str(e))
        line_bot_api.push_message(user_id, TextSendMessage(text=f"⚠️ 訊息處理失敗：{str(e)}"))

# ===== 啟動 MQTT =====
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# 用子執行緒保持 MQTT 心跳不中斷
threading.Thread(target=mqtt_client.loop_forever, daemon=True).start()

# ===== 啟動 Web server =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
