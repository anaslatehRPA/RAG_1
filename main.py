import os
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import chromadb

# LINE Bot setup
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# OpenAI setup
openai.api_key = os.getenv("OPENAI_API_KEY")

# ChromaDB setup
client = chromadb.Client()
collection = client.get_or_create_collection("docs")

def search_context(query_text, top_k=3):
    """ค้นหา context ที่เกี่ยวข้องมากที่สุดจาก ChromaDB"""
    results = collection.query(query_texts=[query_text], n_results=top_k)
    docs = [doc for doc in results["documents"][0]]
    return "\n".join(docs)

def ask_openai(question, context):
    """ถาม OpenAI พร้อม context ที่ได้จาก ChromaDB"""
    prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"].strip()

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    context = search_context(user_message)
    answer = ask_openai(user_message, context)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=answer)
    )

app = FastAPI()

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers["X-Line-Signature"]
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), signature)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return "OK"