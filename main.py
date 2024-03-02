from aiogram import Bot, Dispatcher, types
import asyncio
from datetime import datetime, timedelta
import emoji
from easydict import EasyDict
from googleapiclient.discovery import build
from typing import Optional
import yaml
import logging
from datetime import datetime


config = EasyDict()
logging.basicConfig(
    format='%(asctime)s %(name)s %(levelname)s: %(message)s',
    level=logging.INFO)


with open("config.yaml", "r") as config:
    config = EasyDict(yaml.load(config, Loader=yaml.FullLoader))


bot = Bot(token=config.secret.token_tg)
dp = Dispatcher(bot)
started_at = datetime.now() + timedelta(seconds=30)
last_value_count_views = 0




class CounterViews:

    last_value_count_views: int = 0

    def get_video_views_step(self, video_id) -> Optional[int]:
        """
        Return "step" between last and current views
        :return:
        """
        logging.info(f"Check get_video_views_step")
        youtube = build("youtube", "v3", developerKey=config.secret.token_youtube)
        request = youtube.videos().list(part="statistics", id=video_id)
        response = request.execute()
        result = None
        if "items" in response:
            video = response["items"][0]
            view_count = video["statistics"]["viewCount"]
            if (int(view_count) - self.last_value_count_views) > config.delta_views:
                result = int(view_count)
                self.last_value_count_views = int(view_count)
        return result


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message) -> None:
    await message.reply("Welcome")


async def main():
    logging.info("Run tg bot")
    counter_views = CounterViews()
    while True:
        if count_views := counter_views.get_video_views_step(config.video_id):
            logging.info(f"Send reply {str(count_views)}")
            await bot.send_message(config.secret.chat_id, str(count_views))
        await asyncio.sleep(config.check_timeout)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
