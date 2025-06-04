from vector_store import search_relevant_docs
import os
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

async def rag_workflow(query):
    # 1. ค้นหาข้อมูลที่เกี่ยวข้องจาก vector store
    docs = search_relevant_docs(query)
    context = "\n".join(docs) if docs else ""
    # 2. สร้าง prompt สำหรับส่งไปหา GPT
    prompt = f"Context:\n{context}\n\nUser:\n{query}\n\nAnswer in Thai language:"
    # 3. เรียก OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "ตอบคำถามโดยใช้ข้อมูลใน Context ด้านบนเท่านั้น"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=512,
    )
    return response.choices[0].message.content.strip()