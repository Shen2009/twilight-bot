import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv


# Đọc các biến trong file .env
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "Không tìm thấy DISCORD_TOKEN. "
        "Hãy kiểm tra file .env."
    )


# Slash command cơ bản không cần Message Content Intent
intents = discord.Intents.default()


class MinhBot(commands.Bot):
    async def setup_hook(self) -> None:
        """
        Hàm được chạy khi bot khởi động.
        Đồng bộ các slash command với Discord.
        """
        commands_synced = await self.tree.sync()
        print(f"Đã đồng bộ {len(commands_synced)} slash command.")


bot = MinhBot(
    command_prefix="!",
    intents=intents,
)


@bot.event
async def on_ready() -> None:
    """Được gọi khi bot đăng nhập Discord thành công."""
    if bot.user is None:
        return

    print("=" * 50)
    print(f"Bot đã đăng nhập: {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print("=" * 50)

    await bot.change_presence(
        activity=discord.Game(name="/ping")
    )


@bot.tree.command(
    name="ping",
    description="Kiểm tra bot có đang hoạt động hay không",
)
async def ping(interaction: discord.Interaction) -> None:
    latency_ms = round(bot.latency * 1000)

    await interaction.response.send_message(
        f"🏓 Pong! Độ trễ hiện tại: **{latency_ms} ms**"
    )


@bot.tree.command(
    name="hello",
    description="Bot gửi lời chào đến bạn",
)
async def hello(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(
        f"Xin chào {interaction.user.mention}! "
        "Bot đang hoạt động bình thường."
    )


bot.run(
    TOKEN,
    log_level=logging.INFO,
)