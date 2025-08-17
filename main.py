import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

# .env 파일 로드
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

if not token:
    raise ValueError("토큰이 설정되지 않았습니다! .env 파일을 확인하세요.")

# 인텐트 설정
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

async def main():
    async with bot:
        # ✅ 티켓 Cog 확장 로드
        await bot.load_extension("ticket")  # ticket.py가 main.py와 같은 폴더에 있어야 합니다
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
