import os
import threading
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

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print("📥 MQTT 收到：", message)
    try:
        line_bot_api.push_message(user_id, TextSendMessage(text=f"📡 MQTT：{message}"))
    except Exception as e:
        print("❌ 傳送 LINE 訊息失敗：", e)

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
