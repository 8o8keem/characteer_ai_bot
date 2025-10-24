from flask import Flask, request
import requests
import asyncio
import nest_asyncio
from PyCharacterAI import Client

nest_asyncio.apply()

app = Flask(__name__)

# Your verify token and page access token
VERIFY_TOKEN = "my_verify_token"  # Must match Facebook dashboard exactly
PAGE_ACCESS_TOKEN = "EAA..."  # Your real page access token

# Character.AI info
CHAR_TOKEN = "135ae7a39a84b2c4081c68ca39ef8c948f112e16"
WEB_NEXT_AUTH = "Fe26.2*1*af831e6ba218ccb5ab571165bc104298df567f7dbbb72052f4a4af5560955a40*UNIkeyTN_AWg-1Z0QXK_UQ*kuNFDoelzIJGiV075DW58_5YGG4JYfqCurZ05ryO2GCqGs_YKgDXKsg9vMLCq7LwUPG_pXkk6m9y6j0Utt0RZg**8b0038b74fd8a1c0df3f2e90c5fa0a1136dba52e6fdd433e53c06829fb3f798d*vKJWmPAb3YpYdmR7liKXQ6r7i7f8DXDGVNFPtoRHQKQ~2"
CHARACTER_ID = "jT_fcQ7vMR9JBlaJIKNPtVuf9eCu7ksi2b4LmYIPSr4"

client = Client()

@app.route("/webhook", methods=["GET"])
def verify():
    token = request.args.get("hub.verify_token")
    print("🔍 Facebook sent token:", token)
    if token == VERIFY_TOKEN:
        print("✅ Token verified!")
        return request.args.get("hub.challenge")
    print("❌ Invalid token")
    return "Invalid verification token", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📩 Received message:", data)
    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):
            if "message" in messaging:
                sender_id = messaging["sender"]["id"]
                user_msg = messaging["message"].get("text", "")
                asyncio.run(handle_message(sender_id, user_msg))
    return "ok", 200

async def handle_message(sender_id, user_msg):
    await client.authenticate(CHAR_TOKEN, web_next_auth=WEB_NEXT_AUTH)
    chat, _ = await client.chat.create_chat(CHARACTER_ID)
    reply = await client.chat.send_message(CHARACTER_ID, chat.chat_id, user_msg)
    reply_text = reply.get_primary_candidate().text
    send_message(sender_id, reply_text)

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    response = requests.post(url, json=payload)
    print("📤 Sent to Facebook:", response.status_code, response.text)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
