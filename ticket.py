import discord
from discord.ext import commands

# 서버/채널/역할 ID 설정
LOG_CHANNEL_ID = 1104427383479611506   # ✅ 입장 로그 채널 ID
TICKET_CATEGORY_ID = 1406302967900147812
ADMIN_ROLE_ID = 1104436800728092743
GUILD_ID = 1104427382921765016


class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="❌ 티켓 닫기", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⏳ 티켓을 닫는 중입니다...", ephemeral=True)
        await interaction.channel.delete()


class TicketButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎟️ 티켓 열기", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)

        if not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message("❌ 티켓 카테고리 ID가 잘못되었습니다.", ephemeral=True)
            return

        channel_name = f"ticket-{interaction.user.id}"
        existing = discord.utils.get(guild.channels, name=channel_name)
        if existing:
            await interaction.response.send_message("이미 티켓이 열려 있습니다!", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)

        await channel.send(
            f"{interaction.user.mention}님, 문의 내용을 입력해주세요!",
            view=CloseTicketView()
        )
        await interaction.response.send_message(f"✅ 티켓이 생성되었습니다: {channel.mention}", ephemeral=True)


class TicketCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"봇 로그인 완료: {self.bot.user}")
        self.bot.add_view(TicketButtonView())
        self.bot.add_view(CloseTicketView())

        try:
            guild = discord.Object(id=GUILD_ID)
            synced = await self.bot.tree.sync(guild=guild)  # ✅ 길드 전용 동기화
            print(f"Slash Commands 동기화 완료: {[cmd.name for cmd in synced]}")
        except Exception as e:
            print(f"Slash Commands 동기화 실패: {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.get_channel(LOG_CHANNEL_ID)
        if channel:
            await channel.send(f"👋 {member.mention}님, 서버에 오신 것을 환영합니다!")

    @discord.app_commands.command(
        name="setup_ticket",
        description="티켓 버튼 메시지를 세팅합니다 (운영자 전용)."
    )
    @discord.app_commands.guilds(discord.Object(id=GUILD_ID))  # ✅ 특정 서버 전용 등록
    async def setup_ticket(self, interaction: discord.Interaction):
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message("❌ 서버 멤버만 사용할 수 있습니다.", ephemeral=True)
            return

        if ADMIN_ROLE_ID not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message("❌ 이 명령어는 운영자만 사용할 수 있습니다.", ephemeral=True)
            return

        # ✅ 먼저 즉시 응답
        await interaction.response.send_message("✅ 티켓 설정 중입니다...", ephemeral=True)

        # ✅ 채널에 티켓 버튼 메시지 전송
        view = TicketButtonView()
        await interaction.channel.send("🎫 아래 버튼을 눌러 티켓을 열어주세요!", view=view)

        # ✅ 추가 안내 followup
        await interaction.followup.send("✅ 티켓 설정 완료!", ephemeral=True)


# ✅ 확장용 setup
async def setup(bot: commands.Bot):
    await bot.add_cog(TicketCog(bot))
