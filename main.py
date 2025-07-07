import os
import json
import asyncio
import feedparser
from telethon import TelegramClient
from dotenv import load_dotenv

# Cargar entorno
load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
HISTORIAL_PATH = "videos_enviados.json"

# Mapeo de canales RSS a sus THREAD_ID
CANAL_YOUTUBE = {
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCW-Yh_ztswU47cGifGa9kLg": 721,
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCLjSq1FapG5OgvHsDKinHdA": 721,
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCnXR8InTTbgEmFli424rw0w": 722,
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCOMiYF2tSLOLw5KK7AIY2MA": 721,
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCQeHviVL1ylLV4nK3Mv4jmA": 721,
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCRL3JcKAZLNbqDx1qrYGZdw": 721,
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC3IiGGIgyHtaF_naQ0cOhxA": 721

}

client = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Historial de publicaciones
def cargar_historial():
    if os.path.exists(HISTORIAL_PATH):
        with open(HISTORIAL_PATH, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def guardar_historial(video_ids):
    with open(HISTORIAL_PATH, "w", encoding="utf-8") as f:
        json.dump(list(video_ids), f, indent=2)

posted_videos = cargar_historial()

# Función para monitorear un canal específico
async def monitorear_canal(rss_url, thread_id):
    while True:
        try:
            feed = feedparser.parse(rss_url)
            if feed.entries:
                latest = feed.entries[0]
                video_id = latest.id
                title = latest.title
                link = latest.link

                if video_id not in posted_videos:
                    msg = f"🎬 **Nuevo video**\n📺 *{title}*\n🔗 {link}"
                    await client.get_entity(CHAT_ID)
                    await client.send_message(
                        entity=CHAT_ID,
                        message=msg,
                        reply_to=thread_id
                    )
                    print(f"✅ Publicado: {title}")
                    posted_videos.add(video_id)
                    guardar_historial(posted_videos)
        except Exception as e:
            print(f"❌ Error al monitorear {rss_url}: {e}")
        await asyncio.sleep(3600)

# Lanzar múltiples tareas
async def main():
    tareas = [
        monitorear_canal(rss_url, thread_id)
        for rss_url, thread_id in CANAL_YOUTUBE.items()
    ]
    await asyncio.gather(*tareas)

with client:
    client.loop.run_until_complete(main())
