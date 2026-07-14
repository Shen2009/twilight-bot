import os
import random
import sqlite3

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv


# Đọc file .env khi chạy trên máy cá nhân.
# Trên Pella, token được lấy từ Environment Variables.
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_FILE = "diemdanh.db"

if not TOKEN:
    raise RuntimeError(
        "Không tìm thấy DISCORD_TOKEN. "
        "Hãy kiểm tra file .env hoặc Environment Variables trên Pella."
    )


# =========================================================
# CƠ SỞ DỮ LIỆU ĐIỂM DANH
# =========================================================

def initialize_database() -> None:
    """Tạo bảng điểm danh nếu bảng chưa tồn tại."""
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS attendance (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                points INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (guild_id, user_id)
            )
            """
        )


def add_attendance_point(guild_id: int, user_id: int) -> int:
    """Cộng 1 điểm và trả về tổng điểm mới."""
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute(
            """
            INSERT INTO attendance (guild_id, user_id, points)
            VALUES (?, ?, 1)
            ON CONFLICT(guild_id, user_id)
            DO UPDATE SET points = points + 1
            """,
            (guild_id, user_id),
        )

        cursor = connection.execute(
            """
            SELECT points
            FROM attendance
            WHERE guild_id = ? AND user_id = ?
            """,
            (guild_id, user_id),
        )

        result = cursor.fetchone()

    return result[0] if result else 0


# =========================================================
# CẤU HÌNH BOT
# =========================================================

intents = discord.Intents.default()

# Cần để bot lấy danh sách thành viên và trạng thái online.
intents.members = True
intents.presences = True


class TwilightBot(commands.Bot):
    async def setup_hook(self) -> None:
        """Khởi tạo database và đồng bộ slash command."""
        initialize_database()

        synced_commands = await self.tree.sync()
        print(f"Đã đồng bộ {len(synced_commands)} slash command.")


bot = TwilightBot(
    command_prefix="!",
    intents=intents,
)


@bot.event
async def on_ready() -> None:
    if bot.user is None:
        return

    print("=" * 50)
    print(f"Bot đã đăng nhập: {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print("=" * 50)

    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="/blame | /diemdanh"),
    )


# =========================================================
# LỆNH /BLAME
# =========================================================

@bot.tree.command(
    name="blame",
    description="Gọi tên ngẫu nhiên một thành viên đang online",
)
@app_commands.guild_only()
async def blame(interaction: discord.Interaction) -> None:
    guild = interaction.guild

    if guild is None:
        await interaction.response.send_message(
            "Lệnh này chỉ sử dụng được trong server.",
            ephemeral=True,
        )
        return

    # Online gồm: online, idle và do not disturb.
    active_statuses = {
        discord.Status.online,
        discord.Status.idle,
        discord.Status.dnd,
    }

    online_members = [
        member
        for member in guild.members
        if not member.bot
        and member.id != interaction.user.id
        and member.status in active_statuses
    ]

    if not online_members:
        await interaction.response.send_message(
            "Không tìm thấy thành viên nào khác đang online.",
            ephemeral=True,
        )
        return

    selected_member = random.choice(online_members)

    playful_messages = [
        "{user} nguuuu 😄",
        "đetconme {user} 👀",
        "{user} gay",
        "ditconme{user} ",
        "nguvl {user} ✨",
    ]

    message = random.choice(playful_messages).format(
        user=selected_member.mention
    )

    await interaction.response.send_message(
        message,
        allowed_mentions=discord.AllowedMentions(
            users=True,
            roles=False,
            everyone=False,
        ),
    )


# =========================================================
# LỆNH /DIEMDANH
# =========================================================

@bot.tree.command(
    name="diemdanh",
    description="Điểm danh và nhận thêm 1 điểm",
)
@app_commands.guild_only()
async def diemdanh(interaction: discord.Interaction) -> None:
    guild = interaction.guild

    if guild is None:
        await interaction.response.send_message(
            "Lệnh này chỉ sử dụng được trong server.",
            ephemeral=True,
        )
        return

    total_points = add_attendance_point(
        guild_id=guild.id,
        user_id=interaction.user.id,
    )

    await interaction.response.send_message(
        f"✅ {interaction.user.mention} đã điểm danh thành công!\n"
        f"🏆 Tổng điểm điểm danh: **{total_points} điểm**",
        allowed_mentions=discord.AllowedMentions(
            users=True,
            roles=False,
            everyone=False,
        ),
    )


bot.run(TOKEN)
