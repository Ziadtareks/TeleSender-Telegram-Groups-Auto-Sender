from telethon import TelegramClient, errors
from telethon.sessions import StringSession
import asyncio
import os
import json
from dotenv import load_dotenv
import random
import logging
import gc

load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

if not api_id or not api_hash:
    raise ValueError("API_ID and API_HASH must be set in .env file. See .env.example")
api_id = int(api_id)
STRING_SESSION_FILE = "string_session.txt"
LAST_IDS_FILE = "last_sent_ids.json"

logging.basicConfig(
    filename='telegram_bot.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.getLogger('telethon').setLevel(logging.CRITICAL)

DELAY = 8
REPEAT_EVERY = 2 * 60 * 60

if os.path.exists(STRING_SESSION_FILE):
    with open(STRING_SESSION_FILE, "r") as f:
        saved_string = f.read().strip()
    client_init = StringSession(saved_string)
else:
    client_init = StringSession()


def load_last_ids():
    if os.path.exists(LAST_IDS_FILE):
        try:
            with open(LAST_IDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_last_ids(ids):
    with open(LAST_IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(ids, f, ensure_ascii=False)


async def delete_previous_messages(client, last_sent_ids, available_groups):
    for group_key, msg_id in list(last_sent_ids.items()):
        entity = available_groups.get(group_key)
        if entity and msg_id:
            try:
                await client.delete_messages(entity, msg_id)
                await asyncio.sleep(4)
            except errors.FloodWaitError as e:
                await asyncio.sleep(e.seconds + 5)
            except Exception:
                pass
    if os.path.exists(LAST_IDS_FILE):
        os.remove(LAST_IDS_FILE)


async def send_messages(client, message, target_groups, available_groups):
    new_ids = {}
    for group in target_groups:
        key = group.lower()
        entity = available_groups.get(group) or available_groups.get(key)
        if not entity:
            continue
        try:
            sent = await client.send_message(entity, message)
            new_ids[str(group)] = sent.id
            await asyncio.sleep(DELAY + random.uniform(1, 5))
        except errors.FloodWaitError as e:
            logging.warning(f"FloodWait for {group}: waiting {e.seconds}s")
            await asyncio.sleep(e.seconds + 10)
            try:
                sent = await client.send_message(entity, message)
                new_ids[str(group)] = sent.id
                await asyncio.sleep(DELAY + random.uniform(1, 5))
            except Exception as e2:
                logging.warning(f"Retry failed for {group}: {e2}")
        except (errors.ChatWriteForbiddenError, errors.UserBannedInChannelError):
            logging.warning(f"No permission to send in {group}, skipping")
        except Exception as e:
            logging.warning(f"Failed to send to {group}: {e}")
    save_last_ids(new_ids)


async def main():
    async with TelegramClient(
        client_init,
        api_id,
        api_hash,
        receive_updates=False,
        connection_retries=5,
        retry_delay=10,
    ) as client:
        await client.start()

        if not os.path.exists(STRING_SESSION_FILE):
            with open(STRING_SESSION_FILE, "w") as f:
                f.write(client.session.save())

        with open("message.txt", "r", encoding="utf-8") as f:
            message = f.read().strip()
        with open("groups.txt", "r", encoding="utf-8") as f:
            target_groups = [g.strip() for g in f.readlines() if g.strip()]

        available_groups = {}
        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                entity = dialog.entity
                chat_id = str(dialog.id)
                available_groups[chat_id] = entity
                if getattr(entity, 'username', None):
                    available_groups[entity.username.lower()] = entity

        while True:
            try:
                gc.collect()
                last_sent_ids = load_last_ids()

                if last_sent_ids:
                    await delete_previous_messages(client, last_sent_ids, available_groups)

                await send_messages(client, message, target_groups, available_groups)

                await asyncio.sleep(REPEAT_EVERY)

            except errors.FloodWaitError as e:
                logging.warning(f"Global FloodWait: {e.seconds}s")
                await asyncio.sleep(e.seconds + 30)
            except Exception as e:
                logging.warning(f"Loop error: {e}")
                await asyncio.sleep(15)


if __name__ == "__main__":
    asyncio.run(main())