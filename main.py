import discord
from discord.ext import commands, tasks
import os, time, io, html, re, asyncio, json, random, string, aiohttp
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

WELCOME_URL = "https://raw.githubusercontent.com/mipistore/mipi-store/main/97b3c2a7-b1e8-66b1-50e5-563dc75098ea.jpeg"
THANKYOU_URL = "https://raw.githubusercontent.com/mipistore/mipi-store/main/IMG_6021.jpeg"
QRIS_URL = "https://raw.githubusercontent.com/mipistore/mipi-store/main/IMG_5210.jpeg"

ticket_data = {}
ticket_counter = 0
user_ratings = {}
user_last_ticket = {}
STORE_STATUS = "open"
STORE_STATUS_MSG = ""
OPEN_CLOSE_CHANNEL_ID = 1569135504262299689

PRICELIST_FILE = "pricelist.json"
DEFAULT_PRICELIST = {100: 16000, 200: 32000, 300: 48000, 400: 64000, 500: 75000, 1000: 150000, 2000: 300000, 3000: 450000, 4000: 600000, 5000: 750000}
def load_pricelist():
    try:
        with open(PRICELIST_FILE, "r") as f:
            data = json.load(f); return {int(k): int(v) for k, v in data.items()}
    except: return DEFAULT_PRICELIST.copy()
def save_pricelist(data):
    with open(PRICELIST_FILE, "w") as f: json.dump({str(k): v for k, v in data.items()}, f, indent=2)
def get_harga(robux):
    data = load_pricelist()
    if robux in data: return data[robux]
    return robux * 150
def format_rp(nominal): return f"Rp {nominal:,}".replace(",", ".")
PRICELIST = load_pricelist()

LEADERBOARD_FILE = "leaderboard.json"
def load_leaderboard():
    try:
        with open(LEADERBOARD_FILE, "r") as f: return json.load(f)
    except: return {}
def save_leaderboard(data):
    with open(LEADERBOARD_FILE, "w") as f: json.dump(data, f, indent=2)
def add_to_leaderboard(user_id, username, paket_text):
    m = re.search(r'(\d+)', str(paket_text).replace('.', '').replace(',', ''))
    if not m: return
    jumlah = int(m.group(1)); harga = get_harga(jumlah)
    data = load_leaderboard(); bulan = datetime.now().strftime("%Y-%m")
    if bulan not in data: data[bulan] = {}
    uid = str(user_id)
    if uid not in data[bulan]: data[bulan][uid] = {"username": username, "total": 0, "transaksi": 0, "total_rp": 0}
    if "total_rp" not in data[bulan][uid]: data[bulan][uid]["total_rp"] = 0
    data[bulan][uid]["username"] = username; data[bulan][uid]["total"] += jumlah; data[bulan][uid]["transaksi"] += 1; data[bulan][uid]["total_rp"] += harga
    save_leaderboard(data)
def get_total_belanja(user_id):
    data = load_leaderboard(); total_rp = 0; total_robux = 0; total_transaksi = 0
    for bulan, users in data.items():
        uid = str(user_id)
        if uid in users:
            total_rp += users[uid].get("total_rp", 0); total_robux += users[uid].get("total", 0); total_transaksi += users[uid].get("transaksi", 0)
    return total_rp, total_robux, total_transaksi

PROMO_FILE = "promo.json"
def load_promo():
    try:
        with open(PROMO_FILE, "r") as f: return json.load(f)
    except: return {}
def save_promo(data):
    with open(PROMO_FILE, "w") as f: json.dump(data, f, indent=2)
def cek_promo(kode, harga_awal, jumlah_robux=0):
    if not kode or not str(kode).strip(): return harga_awal, 0, None
    kode = str(kode).upper().strip(); data = load_promo()
    if kode not in data: return harga_awal, 0, "❌ Kode promo tidak ditemukan!"
    p = data[kode]
    if jumlah_robux < 500: return harga_awal, 0, f"❌ Minimal belanja 500 Robux untuk pakai promo ini! Kamu beli {jumlah_robux} Robux, belum cukup Wal!"
    if p.get("dipakai", 0) >= p.get("max", 999): return harga_awal, 0, "❌ Kode promo sudah habis dipakai!"
    if p["tipe"] == "persen": diskon = int(harga_awal * p["diskon"] / 100)
    else: diskon = int(p["diskon"])
    return max(0, harga_awal - diskon), diskon, None

giveaway_data = {}
class GiveawayView(discord.ui.View):
    def __init__(self, giveaway_id): super().__init__(timeout=None); self.giveaway_id = giveaway_id
    @discord.ui.button(label="🎉 JOIN GIVEAWAY", style=discord.ButtonStyle.success, custom_id="join_giveaway")
    async def join_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = giveaway_data.get(self.giveaway_id)
        if not data: await interaction.response.send_message("❌ Giveaway ini sudah berakhir!", ephemeral=True); return
        if data["ended"]: await interaction.response.send_message("❌ Giveaway sudah berakhir Wal!", ephemeral=True); return
        uid = interaction.user.id
        if uid in data["peserta"]: await interaction.response.send_message("⚠️ Kamu udah join Wal!", ephemeral=True); return
        data["peserta"].append(uid)
        try:
            embed = interaction.message.embeds[0]
            embed.description = f"🎁 **Hadiah:** {data['hadiah']}\n\n👑 **Host:** {data['host_mention']}\n⏰ **Berakhir:** <t:{data['end_timestamp']}:R>\n🏆 **Pemenang:** {data['pemenang']} orang\n👥 **Peserta:** {len(data['peserta'])} orang\n\nPencet tombol **🎉 JOIN GIVEAWAY** dibawah buat ikutan!\n\nGood luck! 🍀"
            await interaction.message.edit(embed=embed, view=self)
        except: pass
        await interaction.response.send_message(f"✅ Berhasil join giveaway **{data['hadiah']}**! Good luck! 🍀", ephemeral=True)

async def end_giveaway(guild, channel_id, message_id, giveaway_id):
    data = giveaway_data.get(giveaway_id)
    if not data or data["ended"]: return
    data["ended"] = True
    try:
        channel = guild.get_channel(channel_id)
        if not channel: return
        try: msg = await channel.fetch_message(message_id)
        except: msg = None
        if len(data["peserta"]) == 0:
            if msg:
                embed = discord.Embed(title="🎁 GIVEAWAY BERAKHIR - GAK ADA PESERTA 😭", description=f"Hadiah: **{data['hadiah']}**", color=0xff0000); await msg.edit(embed=embed, view=None)
            await channel.send("😭 Giveaway berakhir tapi gak ada yang join!"); return
        winners = random.sample(data["peserta"], min(data["pemenang"], len(data["peserta"])))
        winner_mentions = ", ".join([f"<@{w}>" for w in winners])
        if msg:
            embed = discord.Embed(title="🎉 GIVEAWAY BERAKHIR - PEMENANG TERPILIH!", description=f"🎁 **Hadiah:** {data['hadiah']}\n\n🏆 **Pemenang:**\n{winner_mentions}\n\n👥 **Total Peserta:** {len(data['peserta'])} orang\n👑 **Host:** {data['host_mention']}", color=0x57f287); await msg.edit(embed=embed, view=None)
        await channel.send(f"🎉 **GIVEAWAY BERAKHIR!**\n\n🎁 Hadiah: **{data['hadiah']}**\n🏆 Pemenang: {winner_mentions}\n\nSelamat ya! 🥳 DM {data['host_mention']} buat klaim!")
    except Exception as e: print(f"Gagal end giveaway: {e}")

BANNED_WORDS = ["wts robux", "jual robux", "sell robux", "jual rb", "wts rb", "jual limited", "wts limited", "sell limited", "jual robux murah", "robux murah", "top up robux", "jual akun robux", "wts akun robux", "wtt robux", "wtb robux", "jual robux via", "robux via username murah"]
ALLOWED_IF_HAS = ["akun pribadi", "akun roblox", "akun pribadi secepatnya"]
def is_banned_selling(text):
    low = text.lower()
    if any(a in low for a in ALLOWED_IF_HAS) and "robux" not in low and "limited" not in low: return False
    return any(w in low for w in BANNED_WORDS)
def hitung_harga(paket_text):
    m = re.search(r'(\d+)', str(paket_text).replace('.', '').replace(',', ''))
    if not m: return "500", "Rp 75.000"
    jumlah = int(m.group(1)); harga = get_harga(jumlah); return str(jumlah), f"Rp {harga:,}".replace(",", ".")
def get_status_channel(guild):
    for ch in guild.text_channels:
        if ch.name == "📦┆・order-status": return ch
    for ch in guild.text_channels:
        if "order-status" in ch.name.lower(): return ch
    return None
def get_history_channel(guild):
    for ch in guild.text_channels:
        if ch.name == "🗂️・history-order": return ch
    for ch in guild.text_channels:
        if "history-order" in ch.name.lower(): return ch
    for ch in guild.text_channels:
        if "history" in ch.name.lower(): return ch
    return None
def get_ticket_category(guild):
    for cat in guild.categories:
        if "TICKET" in cat.name.upper(): return cat
    return None
def get_vouch_channel(guild):
    for ch in guild.channels:
        if "vouch" in ch.name.lower(): return ch
    return None
def make_html_transcript(number, messages, username, paket, duration):
    rows = ""
    for m in messages: rows += f"""<div style="margin:6px 0;padding:8px;background:#2b2d31;border-radius:8px;"><b style="color:#fff;">{html.escape(str(m['author']))}</b> <span style="color:#949ba4;font-size:12px;">{m['time']}</span><br><span style="color:#dbdee1;">{html.escape(m['content'] or '(gambar / embed)')}</span></div>"""
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Ticket #{number} Transcript - MIPI STORE</title></head><body style="background:#1e1f22;font-family:sans-serif;padding:20px;"><h2 style="color:white;">MIPI STORE - Ticket #{number}</h2><p style="color:#949ba4;">Created by {html.escape(username)} | Subject: {html.escape(paket)} | Duration: {duration} minutes | {len(messages)} messages</p>{rows}</body></html>"""
async def send_status_update(guild, number, username, user_id, paket, status_text, color):
    ch = get_status_channel(guild)
    if not ch: return
    embed = discord.Embed(title=f"📦 Order Status - Ticket #{number}", description=f"**Customer:** <@{user_id}> ({username})\n**Paket:** {paket}\n**Status:** {status_text}", color=color)
    embed.set_footer(text="MIPI STORE • Order Status"); await ch.send(embed=embed)
async def send_history_log(guild, channel, data, admin_user):
    ch = get_history_channel(guild)
    if not ch: return
    number = data["number"]; user_id = data["user_id"]
    roblox_user = data.get("roblox_username", data.get("username", "-")); nickname = data.get("nickname", "-"); paket = data.get("paket", "500 Robux"); pembayaran = data.get("pembayaran", "Qrs")
    jumlah, harga = hitung_harga(paket)
    ticket_name = channel.name if channel else f"robux-via-username-{number}-{data.get('username','user')}"
    embed = discord.Embed(color=0x2b2d31)
    embed.description = f"🔒 Ticket Log\n\n🎫 Ticket\n{ticket_name}\n🔒 Action\nClosed\n⚡ Panel\nRobux Via Username\n🎀 Member\n<@{user_id}>\n🏷️ Nickname Roblox\n{nickname}\n👤 Username Roblox\n{roblox_user}\n✨ Jumlah Robux\n{jumlah}\n💰 Total Harga\n{harga}\n💳 Payment\n{pembayaran}\n✅ Admin\n{admin_user.mention if admin_user else 'Auto-Close'}"
    embed.set_image(url=THANKYOU_URL); await ch.send(embed=embed)
async def send_vouch(guild, user, paket, stars, komentar, ticket_number=0, ticket_name=""):
    ch = get_vouch_channel(guild)
    if not ch: return
    jumlah, harga = hitung_harga(paket); star_str = "⭐" * stars; seller = guild.owner.mention if guild.owner else "MIPI STORE"
    if not ticket_name: ticket_name = f"robux-via-username-{ticket_number}-{user.name}"
    embed = discord.Embed(color=0x2b2d31)
    embed.description = f"✅ VOUCH RECEIVED ✅\n\n**Ticket ID**\n{ticket_number}\n**Nominal**\n{harga}\n**Seller**\n{seller}\n**Buyer**\n<@{user.id}>\n**Handled by**\n{seller}\n**Rating**\n{star_str}\n**Komentar**\n{komentar} 💗\n**Source**\n{ticket_name}"
    embed.set_thumbnail(url=user.display_avatar.url); embed.set_footer(text=f"MIPI STORE Vouch System | {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    msg = await ch.send(embed=embed)
    try:
        thread_name = f"Vouch - {user.name} | Ticket #{ticket_number}"
        if isinstance(ch, discord.ForumChannel): await ch.create_thread(name=thread_name, content=f"Vouch dari {user.mention} - Ticket #{ticket_number} - {paket} - {star_str} - {komentar}")
        else:
            thread = await msg.create_thread(name=thread_name, auto_archive_duration=1440)
            await thread.send(f"💗 **Vouch dari {user.mention}**\n\n📦 **Paket:** {paket} ({harga})\n⭐ **Rating:** {star_str}\n💬 **Komentar:** {komentar}\n🎫 **Ticket:** {ticket_name}")
    except Exception as e: print(f"Gagal buat thread vouch: {e}")
async def do_auto_close(guild, channel, data, reason="auto-closed due to inactivity • inactive for 15 minutes", admin_user=None):
    number = data["number"]; user_id = data["user_id"]; paket = data.get("paket", "ORDER ROBUX"); created = data["created_at"]; duration = int((time.time() - created)//60)
    if duration < 1: duration = 1
    user_last_ticket[user_id] = {"number": number, "paket": paket, "ticket_name": channel.name if channel else "", "seller_id": guild.owner_id}
    try: await send_history_log(guild, channel, data, admin_user)
    except Exception as e: print(f"Gagal history: {e}")
    messages = []
    try:
        async for m in channel.history(limit=200, oldest_first=True): messages.append({"author": str(m.author), "time": m.created_at.strftime("%H:%M"), "content": m.content})
    except: pass
    status_ch = get_status_channel(guild)
    if status_ch:
        embed1 = discord.Embed(title="Ticket Auto-Closed", description=f"**#{number} {reason}**\n**Ticket ID**\n{number}", color=0xfee75c)
        embed1.set_footer(text=datetime.now().strftime("%B %d, %Y at %I:%M %p")); await status_ch.send(embed=embed1)
        html_text = make_html_transcript(number, messages, data.get("username","User"), paket, duration)
        file = discord.File(io.BytesIO(html_text.encode()), filename=f"ticket-{number}-auto-transcript.html")
        embed2 = discord.Embed(title="Auto-Generated Transcript (Auto-Closed)", description=f"Transcript automatically generated for auto-closed ticket #{number}\n\n**Ticket**\nTicket #{number}\nCreated by <@{user_id}>\n{len(messages)} messages\n\n**Generation**\nDuration: {duration} minutes\nStatus: Auto-Closed -> Auto-Transcript\n\n**Subject**\n{paket}", color=0x5865f2)
        embed2.set_footer(text=datetime.now().strftime("%B %d, %Y at %I:%M %p")); await status_ch.send(embed=embed2, file=file)
    try:
        user = await bot.fetch_user(user_id)
        embed = discord.Embed(title="Rate Your Experience", description=f"Hi {user.name}! Your support ticket has been resolved.\nPlease rate your experience by clicking a star below.\n\n**Ticket #{number} in 🛒 ORDER ROBUX**\n**Resolved in**\n{duration} minutes\n\n**Closed by**\n{admin_user.name if admin_user else 'MIPI STORE (Auto-Close)'}", color=0x2b2d31)
        await user.send(embed=embed, view=RatingView(number))
    except: pass
    try: add_to_leaderboard(user_id, data.get("username", "User"), paket)
    except Exception as e: print(f"Gagal leaderboard: {e}")
    if channel.id in ticket_data: del ticket_data[channel.id]
    try: await channel.delete()
    except: pass
@tasks.loop(minutes=1)
async def check_inactive():
    now = time.time()
    for channel_id, data in list(ticket_data.items()):
        last = data.get("last_activity", data["created_at"])
        if now - last > 15*60:
            ch = bot.get_channel(channel_id)
            if not ch: del ticket_data[channel_id]; continue
            await do_auto_close(ch.guild, ch, data)
class RatingView(discord.ui.View):
    def __init__(self, ticket_number): super().__init__(timeout=None); self.ticket_number = ticket_number
    async def send_thanks(self, interaction, stars):
        user_ratings[interaction.user.id] = stars; star_str = "⭐" * stars
        embed = discord.Embed(title="Terima Kasih! 💗", description=f"Kamu memberi rating **{star_str} ({stars}/5)** untuk MIPI STORE!\n\nTerima kasih sudah order di Mipi Store! Ditunggu order berikutnya ya 🌸\n\n👇 **Pencet Add Comment dibawah biar vouch kamu muncul di #⭐┆・vouch + jadi thread kayak 404 STORE!**", color=0xff69b4)
        embed.set_image(url=THANKYOU_URL); await interaction.response.edit_message(embed=embed, view=self)
    @discord.ui.button(label="⭐ 1", style=discord.ButtonStyle.secondary, custom_id="rate1")
    async def r1(self, interaction: discord.Interaction, button: discord.ui.Button): await self.send_thanks(interaction, 1)
    @discord.ui.button(label="⭐ 2", style=discord.ButtonStyle.secondary, custom_id="rate2")
    async def r2(self, interaction: discord.Interaction, button: discord.ui.Button): await self.send_thanks(interaction, 2)
    @discord.ui.button(label="⭐ 3", style=discord.ButtonStyle.primary, custom_id="rate3")
    async def r3(self, interaction: discord.Interaction, button: discord.ui.Button): await self.send_thanks(interaction, 3)
    @discord.ui.button(label="⭐ 4", style=discord.ButtonStyle.success, custom_id="rate4")
    async def r4(self, interaction: discord.Interaction, button: discord.ui.Button): await self.send_thanks(interaction, 4)
    @discord.ui.button(label="⭐ 5", style=discord.ButtonStyle.success, custom_id="rate5")
    async def r5(self, interaction: discord.Interaction, button: discord.ui.Button): await self.send_thanks(interaction, 5)
    @discord.ui.button(label="📝 Add Comment", style=discord.ButtonStyle.secondary, custom_id="add_comment", row=1)
    async def comment(self, interaction: discord.Interaction, button: discord.ui.Button): await interaction.response.send_modal(CommentModal(ticket_number=self.ticket_number))
    @discord.ui.button(label="❌ No Thanks", style=discord.ButtonStyle.secondary, custom_id="no_thanks", row=1)
    async def no_thanks(self, interaction: discord.Interaction, button: discord.ui.Button): await interaction.response.edit_message(content="Oke! Terima kasih sudah order di MIPI STORE 💗", embed=None, view=None)
class CommentModal(discord.ui.Modal, title="Komentar / Testimoni"):
    def __init__(self, ticket_number): super().__init__(); self.ticket_number = ticket_number
    komentar = discord.ui.TextInput(label="Komentar kamu", placeholder="satset poll", style=discord.TextStyle.paragraph, required=True)
    async def on_submit(self, interaction: discord.Interaction):
        stars = user_ratings.get(interaction.user.id, 5); last = user_last_ticket.get(interaction.user.id, {}); paket = last.get("paket", "500 Robux"); ticket_name = last.get("ticket_name", f"robux-via-username-{self.ticket_number}-{interaction.user.name}")
        try:
            guild = None
            for g in bot.guilds:
                ch = get_vouch_channel(g)
                if ch: guild = g; break
            if guild: await send_vouch(guild, interaction.user, paket, stars, self.komentar.value, ticket_number=self.ticket_number, ticket_name=ticket_name)
        except Exception as e: print(f"Gagal vouch: {e}")
        await interaction.response.send_message(f"Terima kasih komentarnya! 💗\n> {self.komentar.value}\n\nVouch kamu sudah muncul di **#⭐┆・vouch** + jadi thread! 🎉\nRating: {'⭐'*stars} ({stars}/5)", ephemeral=True)
def is_admin_or_owner(user, guild):
    if user.id == guild.owner_id: return True
    if user.guild_permissions.administrator: return True
    role_names = [r.name.lower() for r in user.roles]
    return any(x in role_names for x in ["admin", "owner", "staff", "moderator", "adm"])
class StatusView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="⏳ Menunggu Pembayaran", style=discord.ButtonStyle.secondary, custom_id="status_waiting")
    async def waiting(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not is_admin_or_owner(interaction.user, interaction.guild): await interaction.followup.send("❌ Hanya **Admin & Owner** yang bisa update status!", ephemeral=True); return
        data = ticket_data.get(interaction.channel.id, {})
        if data: data["last_activity"] = time.time()
        await interaction.followup.send("⏳ Status diubah: **Menunggu Pembayaran**")
        await send_status_update(interaction.guild, data.get("number", "?"), data.get("username", interaction.user.name), data.get("user_id", interaction.user.id), data.get("paket", "ORDER ROBUX"), "⏳ Menunggu Pembayaran", 0xfee75c)
    @discord.ui.button(label="🔄 Diproses", style=discord.ButtonStyle.primary, custom_id="status_process")
    async def process(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not is_admin_or_owner(interaction.user, interaction.guild): await interaction.followup.send("❌ Hanya **Admin & Owner** yang bisa update status!", ephemeral=True); return
        data = ticket_data.get(interaction.channel.id, {})
        if data: data["last_activity"] = time.time()
        await interaction.followup.send("🔄 Status diubah: **Sedang Diproses**")
        await send_status_update(interaction.guild, data.get("number", "?"), data.get("username", interaction.user.name), data.get("user_id", interaction.user.id), data.get("paket", "ORDER ROBUX"), "🔄 Sedang Diproses", 0x5865f2)
    @discord.ui.button(label="✅ Selesai", style=discord.ButtonStyle.success, custom_id="status_done")
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not is_admin_or_owner(interaction.user, interaction.guild): await interaction.response.send_message("❌ Hanya **Admin & Owner** yang bisa update status!", ephemeral=True); return
        data = ticket_data.get(interaction.channel.id, {})
        if data: data["last_activity"] = time.time()
        await interaction.followup.send("✅ Status diubah: **Selesai** - Robux sudah masuk!")
        await send_status_update(interaction.guild, data.get("number", "?"), data.get("username", interaction.user.name), data.get("user_id", interaction.user.id), data.get("paket", "ORDER ROBUX"), "✅ Selesai / Done", 0x57f287)
class CloseView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🔒 CLOSE TICKET", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not is_admin_or_owner(interaction.user, interaction.guild): await interaction.followup.send("❌ Hanya **Admin & Owner** yang bisa menutup ticket ini!", ephemeral=True); return
        channel = interaction.channel; data = ticket_data.get(channel.id)
        if not data: await interaction.followup.send("Ticket ditutup..."); await channel.delete(); return
        await interaction.followup.send(f"Ticket ditutup oleh {interaction.user.mention}. Membuat transcript...")
        await do_auto_close(interaction.guild, channel, data, reason="closed by owner", admin_user=interaction.user)
class SaldoView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="💳 CEK SALDO SAYA", style=discord.ButtonStyle.primary, custom_id="cek_saldo_btn")
    async def cek_saldo(self, interaction: discord.Interaction, button: discord.ui.Button):
        total_rp, total_robux, total_transaksi = get_total_belanja(interaction.user.id); harga_str = f"Rp {total_rp:,}".replace(",", ".")
        embed = discord.Embed(color=0xff1493)
        embed.description = f"💳 **INFORMASI SALDO / TOTAL TRANSAKSI** ✨\n\nHalo {interaction.user.mention},\nberikut adalah rincian total transaksi atau saldo belanja kamu di **MIPI STORE:**\n\n💰 **Total Belanja:** {harga_str}\n📦 **Total Robux:** {total_robux:,} R$\n🧾 **Total Transaksi:** {total_transaksi}x\n\nMIPI STORE • CHECK SALDO"
        embed.set_footer(text="Mipi Store • Rafi Store"); await interaction.response.send_message(embed=embed, ephemeral=True)
class OrderModal(discord.ui.Modal, title="Pesanan Robux"):
    nickname = discord.ui.TextInput(label="Nickname Roblox", placeholder="Nickname Roblox kamu", required=True)
    username = discord.ui.TextInput(label="Username", placeholder="UsernameRoblox", required=True)
    paket = discord.ui.TextInput(label="Paket yang dipilih", placeholder="Contoh: 500 Robux", required=True)
    pembayaran = discord.ui.TextInput(label="Metode Pembayaran", placeholder="QRIS", default="QRIS", required=True)
    kode_promo = discord.ui.TextInput(label="Kode Promo (Opsional)", placeholder="Contoh: MIPI10 - Kosongin aja kalau gak ada", required=False)
    async def on_submit(self, interaction: discord.Interaction):
        global ticket_counter
        ticket_counter += 1; guild = interaction.guild
        overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False), interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True), guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
        category = get_ticket_category(guild)
        channel = await guild.create_text_channel(name=f"robux-via-username-{ticket_counter}-{interaction.user.name}", overwrites=overwrites, category=category)
        m_temp = re.search(r'(\d+)', str(self.paket.value).replace('.', '')); jumlah_int = int(m_temp.group(1)) if m_temp else 500
        harga_awal = get_harga(jumlah_int); kode_input = self.kode_promo.value.strip() if self.kode_promo.value else ""
        harga_akhir, diskon, err_promo = cek_promo(kode_input, harga_awal, jumlah_int); promo_text = ""
        if kode_input and not err_promo and diskon > 0:
            pdata = load_promo(); k_up = kode_input.upper()
            if k_up in pdata: pdata[k_up]["dipakai"] = pdata[k_up].get("dipakai", 0) + 1; save_promo(pdata)
            promo_text = f"\n🏷️ **Kode Promo:** {k_up} (-Rp {diskon:,})".replace(",", ".") + f"\n💸 **Harga Setelah Diskon:** Rp {harga_akhir:,}".replace(",", ".")
        elif kode_input and err_promo: promo_text = f"\n⚠️ **Kode Promo:** {kode_input.upper()} - {err_promo} (Harga normal)\n💰 **Harga:** Rp {harga_awal:,}".replace(",", ".")
        ticket_data[channel.id] = {"user_id": interaction.user.id, "username": interaction.user.name, "nickname": self.nickname.value, "roblox_username": self.username.value, "pembayaran": self.pembayaran.value, "created_at": time.time(), "last_activity": time.time(), "number": ticket_counter, "paket": self.paket.value, "promo": kode_input, "harga_akhir": harga_akhir}
        embed = discord.Embed(title=f"🎫 Ticket Baru - {interaction.user.name}", description=f"**Nickname Roblox:** {self.nickname.value}\n**Username Roblox:** {self.username.value}\n**Paket:** {self.paket.value}\n**Pembayaran:** {self.pembayaran.value}{promo_text}\n**Ticket #{ticket_counter}**\n\nSilahkan kirim bukti pembayaran QRIS disini ya 💗", color=0xff69b4)
        embed.set_image(url=WELCOME_URL)
        await channel.send(f"{interaction.user.mention} Halo! Selamat datang di MIPI STORE! 🌸", embed=embed, view=CloseView())
        embed_qris = discord.Embed(title="💳 Scan QRIS Disini", description="Silahkan scan QRIS ini untuk pembayaran ya 💗", color=0xff69b4); embed_qris.set_image(url=QRIS_URL); await channel.send(embed=embed_qris)
        await channel.send("**📦 STATUS ORDER - Owner only:**", view=StatusView())
        await send_status_update(guild, ticket_counter, interaction.user.name, interaction.user.id, self.paket.value, "🆕 Ticket Baru Dibuat", 0xff69b4)
        go_view = discord.ui.View(); go_view.add_item(discord.ui.Button(label="🚀 BUKA TICKET SAYA", style=discord.ButtonStyle.link, url=f"https://discord.com/channels/{guild.id}/{channel.id}"))
        await interaction.response.send_message(f"✅ Ticket kamu sudah dibuat!\nPencet tombol dibawah untuk langsung masuk ke ticket kamu 👇\n👉 {channel.mention}", view=go_view, ephemeral=True)
        try: await interaction.user.send(f"✅ Ticket MIPI STORE kamu sudah dibuat!\nNickname: {self.nickname.value}\nUsername: {self.username.value}\nPaket: {self.paket.value}\nLangsung klik disini ya: 👉 {channel.mention}\nLink: https://discord.com/channels/{guild.id}/{channel.id}\n\nKirim bukti QRIS kamu disana ya 💗")
        except: pass
class OrderView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="ORDER ROBUX", style=discord.ButtonStyle.primary, custom_id="order_robux")
    async def order_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if STORE_STATUS == "break":
            embed = discord.Embed(color=0xfee75c); embed.description = "## 🟡 MIPI STORE LAGI BREAK! ☕\n\nMimin break sebentar yaa, 15-30 menit aja!\n\n🚫 **Ticket lagi dikunci sementara** biar Mimin bisa istirahat dulu!\nTunggu sampe Mimin **OPEN** lagi yaa, jangan spam pencet tombol!\n\nMakasih udah ngerti! 💗"; await interaction.response.send_message(embed=embed, ephemeral=True); return
        if STORE_STATUS == "closed":
            embed = discord.Embed(color=0xff0000); embed.description = "## 🔴 MIPI STORE UDAH TUTUP! 💤\n\nMohon maaf yaa, toko udah **TUTUP**!\n\n🚫 **Ticket lagi dikunci** biar ga numpuk!\nOrderan kamu bakal dibales besok pas Mimin **OPEN** lagi!\n\nMakasih udah mampir hari ini! Sampai ketemu besok! 💗"; await interaction.response.send_message(embed=embed, ephemeral=True); return
        await interaction.response.send_modal(OrderModal()) 
# ===== PART 3/5 - COMMANDS + REKBER PINK PERSIS CHLOE - FIX 2 KOTAK =====
@bot.event
async def on_message(message):
    if message.author.bot: return
    if message.guild and "market" in message.channel.name.lower():
        if message.author.id != message.guild.owner_id and not message.author.guild_permissions.administrator:
            if is_banned_selling(message.content):
                try: await message.delete()
                except: pass
                embed = discord.Embed(title="Stickied Message:", description="DILARANG MENJUAL PRODUK YANG KAMI JUAL SEPERTI ROBUX DAN LIMITED ITEM", color=0xff0000)
                warn = await message.channel.send(f"{message.author.mention}", embed=embed); await asyncio.sleep(10)
                try: await warn.delete()
                except: pass
                try: await message.author.send(f"⚠️ Pesan kamu di **#{message.channel.name}** dihapus!\n\n**Alasan:** Dilarang menjual produk yang kami jual seperti Robux dan Limited Item di MIPI STORE!")
                except: pass
                return
    if message.channel.id in ticket_data: ticket_data[message.channel.id]["last_activity"] = time.time()
    await bot.process_commands(message)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    # Backup handler kalau tombol panel LayoutView kehapus dari memori
    try:
        cid = interaction.data.get("custom_id", "") if interaction.data else ""
    except: cid = ""
    if cid == "rekber_buat_ticket":
        if STORE_STATUS != "open":
            await interaction.response.send_message("🔴 MIPI lagi BREAK / CLOSED! Rekber buka lagi pas OPEN ya!", ephemeral=True); return
        rekber_data[interaction.user.id] = {"rentang": None, "fee": 0, "rentang_label": "-", "buyer_id": None, "seller_id": None, "fee_by": None, "jenis": "-", "harga": 0, "harga_text": "-"}
        view = RekberFormV2Pink(interaction.user.id)
        await interaction.response.send_message(view=view, ephemeral=True)
        return

@bot.event
async def on_ready():
    print(f"Login {bot.user}")
    bot.add_view(OrderView()); bot.add_view(CloseView()); bot.add_view(StatusView()); bot.add_view(RatingView(0)); bot.add_view(SaldoView()); bot.add_view(GiveawayView("dummy"))
    if not check_inactive.is_running(): check_inactive.start()
    await bot.tree.sync()

@bot.tree.command(name="ticket", description="Tampilkan panel order MIPI STORE")
async def ticket(interaction: discord.Interaction):
    if STORE_STATUS != "open":
        status_text = "🟡 BREAK - Mimin break 15-30 menit!" if STORE_STATUS == "break" else "🔴 CLOSED - Toko tutup, balik besok yaa!"
        await interaction.response.send_message(f"{status_text}\n\n🚫 Ticket lagi dikunci sementara biar ga spam! Tunggu OPEN lagi yaa! 💗", ephemeral=True); return
    embed1 = discord.Embed(title="Mipi Store - Order Robux 💗", description="🌸 **ROBUX VIA USERNAME**\nFast Process • Aman • Instan\n\nSyarat top up via username:\n>> SUDAH 18+\n>> SUDAH TERVERIFIKASI 2 LANGKAH", color=0xff69b4); embed1.set_image(url=WELCOME_URL)
    embed2 = discord.Embed(title="💰 PRICELIST ROBUX FAST SEND", description="500 = Rp 75.000\n1000 = Rp 150.000\n2000 = Rp 300.000\n3000 = Rp 450.000\n4000 = Rp 600.000\n5000 = Rp 750.000\n\n🌸 **Robux Eceran**\n100 = Rp 16.000\n200 = Rp 32.000\n300 = Rp 48.000\n400 = Rp 64.000\n\n🛒 **Cara Order**\nClick tombol ORDER ROBUX dibawah, isi formulir, lalu tunggu admin. Pembayaran **hanya QRIS**.", color=0xff69b4); embed2.set_image(url=QRIS_URL); embed2.set_footer(text="Mipi Store • Rafi Store")
    await interaction.response.send_message(embed=embed1); await interaction.followup.send(embed=embed2, view=OrderView())

@bot.tree.command(name="setup-ticket", description="Kirim panel ticket order (Owner only)")
async def setup_ticket(interaction: discord.Interaction):
    if interaction.user.id != interaction.guild.owner_id: await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    embed1 = discord.Embed(title="Mipi Store - Order Robux 💗", description="🌸 **ROBUX VIA USERNAME**\nFast Process • Aman • Instan\n\nSyarat top up via username:\n>> SUDAH 18+\n>> SUDAH TERVERIFIKASI 2 LANGKAH", color=0xff69b4); embed1.set_image(url=WELCOME_URL)
    await interaction.response.send_message(embed=embed1)
    embed2 = discord.Embed(title="💰 PRICELIST ROBUX FAST SEND", description="500 = Rp 75.000\n1000 = Rp 150.000\n2000 = Rp 300.000\n3000 = Rp 450.000\n4000 = Rp 600.000\n5000 = Rp 750.000\n\n🌸 **Robux Eceran**\n100 = Rp 16.000\n200 = Rp 32.000\n300 = Rp 48.000\n400 = Rp 64.000", color=0xff69b4); embed2.set_image(url=QRIS_URL); embed2.set_footer(text="Mipi Store • Rafi Store")
    await interaction.followup.send(embed=embed2, view=OrderView())

@bot.tree.command(name="leaderboard", description="Lihat Top Buyer MIPI STORE bulan ini")
async def leaderboard(interaction: discord.Interaction):
    bulan = datetime.now().strftime("%Y-%m"); data = load_leaderboard(); bulan_data = data.get(bulan, {})
    if not bulan_data: await interaction.response.send_message("Belum ada data Top Buyer bulan ini Wal! 🌸", ephemeral=True); return
    sorted_users = sorted(bulan_data.items(), key=lambda x: x[1]["total"], reverse=True)[:10]
    medali = ["🥇","🥈","🥉","#4","#5","#6","#7","#8","#9","#10"]
    desc = f"Leaderboard bulanan • {bulan}\nPeringkat berdasarkan total Robux yang tercatat.\n\n**TOP 10 BUYERS**\n"
    for i, (uid, info) in enumerate(sorted_users): desc += f"{medali[i]} <@{uid}> — {info['total']:,} R$ · {info['transaksi']} transaksi\n"
    embed = discord.Embed(title="🏆 MIPI STORE — TOP BUYER", description=desc, color=0xff69b4); embed.set_footer(text="Mipi Store • Rafi Store"); await interaction.response.send_message(embed=embed)

@bot.tree.command(name="saldo", description="Cek total belanja kamu di MIPI STORE")
async def saldo_slash(interaction: discord.Interaction):
    total_rp, total_robux, total_transaksi = get_total_belanja(interaction.user.id); harga_str = f"Rp {total_rp:,}".replace(",", ".")
    embed = discord.Embed(color=0xff1493); embed.description = f"💳 **INFORMASI SALDO / TOTAL TRANSAKSI** ✨\n\nHalo {interaction.user.mention},\n\n💰 **Total Belanja:** {harga_str}\n📦 **Total Robux:** {total_robux:,} R$\n🧾 **Total Transaksi:** {total_transaksi}x\n\nMIPI STORE • CHECK SALDO"; embed.set_footer(text="Mipi Store • Rafi Store"); await interaction.response.send_message(embed=embed, ephemeral=True)
@bot.command(name="saldo")
async def saldo_prefix(ctx):
    total_rp, total_robux, total_transaksi = get_total_belanja(ctx.author.id); harga_str = f"Rp {total_rp:,}".replace(",", ".")
    embed = discord.Embed(color=0xff1493); embed.description = f"💳 **INFORMASI SALDO / TOTAL TRANSAKSI** ✨\n\nHalo {ctx.author.mention},\n\n💰 **Total Belanja:** {harga_str}\n📦 **Total Robux:** {total_robux:,} R$\n🧾 **Total Transaksi:** {total_transaksi}x"; await ctx.send(embed=embed)
@bot.tree.command(name="setup-saldo", description="Kirim panel cek saldo ke channel ini (Owner only)")
async def setup_saldo(interaction: discord.Interaction):
    if interaction.user.id != interaction.guild.owner_id: await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    embed = discord.Embed(title="💳 CEK SALDO - MIPI STORE", description="🌸 **MAU TAU UDAH HABIS BERAPA DI MIPI STORE?**\n\nPencet tombol **💳 CEK SALDO SAYA** dibawah ini!\n\nNanti bakal muncul:\n💰 Total Belanja kamu\n📦 Total Robux yang udah dibeli\n🧾 Total Transaksi kamu", color=0xff69b4); await interaction.response.send_message(embed=embed, view=SaldoView())
@bot.tree.command(name="add-saldo", description="Tambah saldo manual ke buyer (Admin / Owner only)")
async def add_saldo(interaction: discord.Interaction, user: discord.User, robux: int):
    if not is_admin_or_owner(interaction.user, interaction.guild): await interaction.response.send_message("❌ Hanya Admin / Owner!", ephemeral=True); return
    if robux <= 0: await interaction.response.send_message("❌ Jumlah Robux harus lebih dari 0!", ephemeral=True); return
    harga = get_harga(robux); add_to_leaderboard(user.id, user.name, f"{robux} Robux"); total_rp, total_robux, total_transaksi = get_total_belanja(user.id)
    embed = discord.Embed(color=0x57f287); embed.description = f"✅ **Saldo {user.mention} ditambah!**\n\n📦 **+{robux:,} R$**\n💰 **+{format_rp(harga)}**\n\n🧾 **Total Transaksi Sekarang:** {total_transaksi}x\n📦 **Total Robux Sekarang:** {total_robux:,} R$\n💰 **Total Belanja Sekarang:** {format_rp(total_rp)}"; await interaction.response.send_message(embed=embed)
@bot.command(name="add-saldo")
async def add_saldo_prefix(ctx, user: discord.User, robux: int):
    if not is_admin_or_owner(ctx.author, ctx.guild): await ctx.send("❌ Hanya Admin / Owner!"); return
    harga = get_harga(robux); add_to_leaderboard(user.id, user.name, f"{robux} Robux"); await ctx.send(f"✅ **Saldo {user.mention} ditambah!**\n📦 +{robux:,} R$\n💰 +{format_rp(harga)}")

@bot.tree.command(name="buat-promo", description="Buat kode promo diskon (Owner only)")
async def buat_promo(interaction: discord.Interaction, kode: str, diskon: int, tipe: str = "nominal", max_pakai: int = 10):
    if interaction.user.id != interaction.guild.owner_id: await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    kode = kode.upper().strip(); data = load_promo(); data[kode] = {"diskon": diskon, "tipe": tipe, "max": max_pakai, "dipakai": 0, "dibuat_oleh": interaction.user.name}; save_promo(data)
    desc = f"Diskon **{diskon}%**" if tipe == "persen" else f"Diskon **{format_rp(diskon)}**"
    embed = discord.Embed(title="🏷️ KODE PROMO BARU!", description=f"🎉 **Kode:** `{kode}`\n{desc}\n📦 **Max Pakai:** {max_pakai} orang\n⚠️ **Minimal Belanja:** 500 Robux", color=0x57f287); await interaction.response.send_message(embed=embed)
@bot.tree.command(name="list-promo", description="Lihat semua kode promo yang aktif")
async def list_promo(interaction: discord.Interaction):
    data = load_promo()
    if not data: await interaction.response.send_message("Belum ada kode promo Wal! Bikin dulu pake `/buat-promo`", ephemeral=True); return
    desc = "**🏷️ LIST KODE PROMO MIPI STORE**\n\n"
    for kode, p in data.items():
        sisa = p.get("max", 999) - p.get("dipakai", 0); d = f"{p['diskon']}%" if p["tipe"] == "persen" else format_rp(p['diskon']); status = "✅ AKTIF" if sisa > 0 else "❌ HABIS"; desc += f"`{kode}` - Diskon {d} - Sisa {sisa}/{p.get('max', 999)} - Min 500 R$ - {status}\n"
    await interaction.response.send_message(embed=discord.Embed(description=desc, color=0xff69b4), ephemeral=True)
@bot.tree.command(name="cek-promo", description="Cek apakah kode promo masih bisa dipakai")
async def cek_promo_cmd(interaction: discord.Interaction, kode: str, paket: str = "500"):
    kode_up = kode.upper().strip(); data = load_promo()
    if kode_up not in data: await interaction.response.send_message(f"❌ Kode `{kode_up}` tidak ditemukan!", ephemeral=True); return
    p = data[kode_up]; sisa = p.get("max", 999) - p.get("dipakai", 0); m = re.search(r'(\d+)', str(paket).replace('.', '')); jumlah = int(m.group(1)) if m else 500; harga_awal = get_harga(jumlah); harga_baru, diskon, err = cek_promo(kode_up, harga_awal, jumlah)
    if err: await interaction.response.send_message(err, ephemeral=True); return
    await interaction.response.send_message(f"✅ Kode `{kode_up}` **MASIH AKTIF!**\n\n📦 Paket: {jumlah} Robux\n💰 Harga Normal: {format_rp(harga_awal)}\n🏷️ Diskon: {format_rp(diskon)}\n💸 Harga Setelah Diskon: **{format_rp(harga_baru)}**\n📦 Sisa: {sisa} orang\n⚠️ Minimal: 500 Robux", ephemeral=True)
@bot.tree.command(name="hapus-promo", description="Hapus kode promo (Owner only)")
async def hapus_promo(interaction: discord.Interaction, kode: str):
    if interaction.user.id != interaction.guild.owner_id: await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    kode = kode.upper().strip(); data = load_promo()
    if kode not in data: await interaction.response.send_message(f"❌ Kode `{kode}` tidak ditemukan!", ephemeral=True); return
    del data[kode]; save_promo(data); await interaction.response.send_message(f"✅ Kode promo `{kode}` sudah dihapus!", ephemeral=True)

@bot.tree.command(name="giveaway", description="Buat giveaway otomatis (Owner only)")
async def giveaway_create(interaction: discord.Interaction, hadiah: str, durasi_menit: int, pemenang: int = 1):
    if interaction.user.id != interaction.guild.owner_id: await interaction.response.send_message("❌ Hanya Owner yang bisa bikin giveaway!", ephemeral=True); return
    if durasi_menit < 1: await interaction.response.send_message("❌ Durasi minimal 1 menit Wal!", ephemeral=True); return
    giveaway_id = f"{interaction.channel.id}-{interaction.id}"; end_time = int(time.time() + durasi_menit * 60)
    giveaway_data[giveaway_id] = {"hadiah": hadiah, "host_mention": interaction.user.mention, "host_id": interaction.user.id, "end_timestamp": end_time, "pemenang": pemenang, "peserta": [], "ended": False, "channel_id": interaction.channel.id}
    embed = discord.Embed(title="🎁 GIVEAWAY MIPI STORE! 🎁", description=f"🎁 **Hadiah:** {hadiah}\n\n👑 **Host:** {interaction.user.mention}\n⏰ **Berakhir:** <t:{end_time}:R>\n🏆 **Pemenang:** {pemenang} orang\n👥 **Peserta:** 0 orang\n\nPencet tombol **🎉 JOIN GIVEAWAY** dibawah buat ikutan!\n\nGood luck! 🍀", color=0xff69b4)
    await interaction.response.send_message(embed=embed, view=GiveawayView(giveaway_id))
    msg = await interaction.original_response(); giveaway_data[giveaway_id]["message_id"] = msg.id; await asyncio.sleep(durasi_menit * 60); await end_giveaway(interaction.guild, interaction.channel.id, msg.id, giveaway_id)
@bot.tree.command(name="giveaway-end", description="Akhiri giveaway lebih cepat (Owner only)")
async def giveaway_end(interaction: discord.Interaction):
    if interaction.user.id != interaction.guild.owner_id: await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    found = None
    for gid, data in giveaway_data.items():
        if data["channel_id"] == interaction.channel.id and not data["ended"]: found = (gid, data); break
    if not found: await interaction.response.send_message("❌ Gak ada giveaway yang lagi jalan di channel ini!", ephemeral=True); return
    gid, data = found; await interaction.response.send_message("🎉 Giveaway diakhiri lebih cepat! Mengundi pemenang...", ephemeral=True); await end_giveaway(interaction.guild, interaction.channel.id, data.get("message_id"), gid)

@bot.tree.command(name="market-rules", description="Kirim aturan market")
async def market_rules(interaction: discord.Interaction):
    if interaction.user.id != interaction.guild.owner_id: await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    embed = discord.Embed(title="Stickied Message:", description="DILARANG MENJUAL PRODUK YANG KAMI JUAL SEPERTI ROBUX DAN LIMITED ITEM", color=0xff0000); msg = await interaction.channel.send(embed=embed)
    try: await msg.pin()
    except: pass
    await interaction.response.send_message("✅ Aturan market sudah di-pin!", ephemeral=True)
@bot.command(name="market-rules")
async def market_rules_prefix(ctx):
    if ctx.author.id != ctx.guild.owner_id: await ctx.send("❌ Hanya Owner!"); return
    embed = discord.Embed(title="Stickied Message:", description="DILARANG MENJUAL PRODUK YANG KAMI JUAL SEPERTI ROBUX DAN LIMITED ITEM", color=0xff0000); msg = await ctx.send(embed=embed)
    try: await msg.pin()
    except: pass
    await ctx.send("✅ Aturan market sudah di-pin!")
@bot.tree.command(name="ping", description="Cek bot")
async def ping(interaction: discord.Interaction): await interaction.response.send_message(f"Pong! 🏓 MIPI STORE online Wal! {round(bot.latency*1000)}ms")
@bot.command(name="ping")
async def ping_prefix(ctx): await ctx.send(f"Pong! 🏓 MIPI STORE online Wal! {round(bot.latency*1000)}ms")

@bot.tree.command(name="checkavatar", description="Mengecek detail profil dan avatar akun Roblox dengan username")
async def checkavatar(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    try:
        headers = {"User-Agent": "Mozilla/5.0 MIPI-STORE-Bot"}
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.post("https://users.roproxy.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": True}) as r:
                data = await r.json()
                if not data.get("data"): await interaction.followup.send(f"❌ Username `{username}` tidak ditemukan!"); return
                user = data["data"][0]; user_id = user["id"]; display = user.get("displayName", username); uname = user.get("name", username)
            async with s.get(f"https://users.roproxy.com/v1/users/{user_id}") as r:
                info = await r.json(); created = info.get("created", "")
                try: tgl = datetime.fromisoformat(created.replace("Z", "+00:00")).strftime("%d %B %Y")
                except: tgl = created
            async with s.get(f"https://avatar.roproxy.com/v1/users/{user_id}/avatar") as r:
                av = await r.json(); tipe = av.get("playerAvatarType", "R15"); assets = av.get("assets", [])
            async with s.get(f"https://thumbnails.roproxy.com/v1/users/avatar?userIds={user_id}&size=720x720&format=Png&isCircular=false") as r:
                thumb = await r.json(); avatar_url = thumb["data"][0]["imageUrl"] if thumb.get("data") else None
            profil_url = f"https://www.roblox.com/users/{user_id}/profile"
            desc = f"🔍 **Profil Roblox:** [{uname}]({profil_url})\n👤 **Display Name**\n{display}\n🆔 **User ID**\n{user_id}\n📅 **Tanggal Dibuat**\n{tgl}\n🏃 **Tipe Avatar**\n{tipe}\n\n📦 **Total Item:** {len(assets)} item"
            e = discord.Embed(title=f"Profil Roblox: {uname}", description=desc, color=0xFF69B4); e.url = profil_url
            if avatar_url: e.set_image(url=avatar_url)
            e.set_footer(text="MIPI STORE • /checkavatar")
            view = discord.ui.View(); view.add_item(discord.ui.Button(label="👤 Buka Profil Roblox", style=discord.ButtonStyle.link, url=profil_url, emoji="🔍")); view.add_item(discord.ui.Button(label="🎮 Lihat Avatar 3D", style=discord.ButtonStyle.link, url=profil_url))
            await interaction.followup.send(embed=e, view=view)
    except Exception as ex: await interaction.followup.send(f"❌ Gagal cek avatar: {ex}")

@bot.tree.command(name="cekrbx", description="Link untuk mengecek riwayat transaksi Robux Gamepass")
async def cekrbx(interaction: discord.Interaction, username: str = None, link_gamepass: str = None):
    await interaction.response.defer(ephemeral=True)
    e = discord.Embed(title="🔍 CEK RIWAYAT TRANSAKSI ROBUX - MIPI STORE", description="Cek sendiri Robux kamu udah masuk / belum, tanpa nunggu admin! 💗", color=0xFF69B4)
    if username:
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": True}) as r:
                    data = await r.json()
                    if not data.get("data"): await interaction.followup.send(f"❌ Username `{username}` tidak ditemukan!", ephemeral=True); return
                    user_id = data["data"][0]["id"]; display = data["data"][0].get("displayName", username)
                e.add_field(name=f"👤 Akun: {username} ({display})", value=f"🆔 User ID: `{user_id}`", inline=False)
        except Exception as ex: e.add_field(name="⚠️ Info", value=f"Gagal ambil gamepass: {ex}", inline=False)
    if link_gamepass:
        m = re.search(r'(\d+)', link_gamepass)
        if m: e.add_field(name="🎫 Gamepass yang dicek", value=f"ID: `{m.group(1)}`\nLink: https://www.roblox.com/game-pass/{m.group(1)}", inline=False)
    e.add_field(name="🔗 LINK CEK RESMI ROBLOX", value="1. **Cek Transaksi:**\nhttps://www.roblox.com/transactions\n\n2. **Cek Pending Robux:**\nhttps://www.roblox.com/transactions#pending-robux\n\n3. **Cek Saldo:**\nhttps://www.roblox.com/my/account#!/info", inline=False)
    e.add_field(name="📖 CARA CEK", value="1. Login Roblox di browser\n2. Buka link Transaksi di atas\n3. Pilih Penjualan / Pembelian\n4. Kalau Pending, tunggu 3-7 hari (Hold Roblox)", inline=False)
    e.set_footer(text="MIPI STORE • Kalau belum masuk 3 hari, buka tiket di #open-ticket")
    await interaction.followup.send(embed=e, ephemeral=True)

@bot.tree.command(name="setup-cek", description="Buatin channel cek yang estetik otomatis (Owner only)")
async def setup_cek(interaction: discord.Interaction):
    if interaction.user.id != interaction.guild.owner_id: await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    await interaction.response.defer(ephemeral=True); guild = interaction.guild; cat = None
    for c in guild.categories:
        if "MIPI" in c.name.upper() and "CEK" in c.name.upper(): cat = c; break
    if not cat: cat = await guild.create_category("🌸・MIPI — CEK ROBLOX")
    ch1 = await guild.create_text_channel("🔍┆・check-avatar", category=cat); ch2 = await guild.create_text_channel("💰┆・cek-rbx", category=cat)
    e1 = discord.Embed(color=0xff69b4); e1.description = "## 🌸・CHECK AVATAR ROBLOX\n━━━━━━━━━━━━━━━━━━━━━━\nMau liat avatar temen? Cek disini aja, **gratis & instan!** ✨\n\n### 📝 CARA PAKAI\n```\n/checkavatar username: usernameRobloxKamu\n```\n### 💡 CONTOH\n```\n/checkavatar username: 1mrafii\n```"; e1.set_image(url=WELCOME_URL); e1.set_footer(text="MIPI STORE • /checkavatar")
    e2 = discord.Embed(color=0xff69b4); e2.description = "## 💰・CEK RIWAYAT ROBUX\n━━━━━━━━━━━━━━━━━━━━━━\nRobux belum masuk? Cek sendiri disini! ✨\n\n### 📝 CARA PAKAI\n```\n/cekrbx username: usernameRobloxKamu\n```\n### 🔗 LINK RESMI\n[📦 Cek Transaksi](https://www.roblox.com/transactions)\n[⏳ Cek Pending](https://www.roblox.com/transactions#pending-robux)"; e2.set_image(url=QRIS_URL); e2.set_footer(text="MIPI STORE • /cekrbx")
    await ch1.send(embed=e1); await ch2.send(embed=e2)
    await interaction.followup.send(embed=discord.Embed(color=0x57f287, description=f"## ✅ BERHASIL DIBUAT! 🎉\n📂 Kategori: **{cat.name}**\n🔍 Channel: {ch1.mention}\n💰 Channel: {ch2.mention}"), ephemeral=True)

def get_openclose_channel(guild):
    ch = guild.get_channel(OPEN_CLOSE_CHANNEL_ID)
    if ch: return ch
    for ch in guild.text_channels:
        if "open-close" in ch.name.lower(): return ch
    return guild.system_channel
async def kirim_status_openclose(guild, tipe):
    global STORE_STATUS, STORE_STATUS_MSG
    ch = get_openclose_channel(guild)
    if not ch: return None
    STORE_STATUS = tipe
    if tipe == "open": STORE_STATUS_MSG = ""
    elif tipe == "break": STORE_STATUS_MSG = "Mimin lagi break 15-30 menit yaa!"
    else: STORE_STATUS_MSG = "Toko udah TUTUP! Balik besok yaa!"
    if tipe == "open":
        embed = discord.Embed(color=0x57f287); embed.description = "# 🟢 MIPI STORE - OPEN! 💗\n━━━━━━━━━━━━━━━\n**Selamat datang di MIPI STORE!**\nToko udah **BUKA** yaa! ✨\n\n💎 **Robux Ready Stock!**\n⚡ **Proses Fast Satset!**\n💰 **Harga Mulai Rp 3.500 aja!**\n\n📌 **Cara Order:**\nKetik `/ticket` atau buka ticket di channel order!\n🛒 **Order sekarang, Mimin fast respon!**"; embed.set_image(url=WELCOME_URL); embed.set_footer(text="MIPI STORE • OPEN")
    elif tipe == "break":
        embed = discord.Embed(color=0xfee75c); embed.description = "# 🟡 MIPI STORE - BREAK SEBENTAR! ☕\n━━━━━━━━━━━━━━━\n**Mimin break sebentar yaa!** 🙏\n\n⏳ **Break:** 15 - 30 Menit\n💗 Chat tetap bisa masuk, tapi slow respon dulu ya!\n\n🚫 **TICKET DIKUNCI SEMENTARA!**"; embed.set_footer(text="MIPI STORE • BREAK - Ticket Dikunci")
    else:
        embed = discord.Embed(color=0xff0000); embed.description = "# 🔴 MIPI STORE - CLOSED! 💤\n━━━━━━━━━━━━━━━\n**Mohon maaf, toko udah TUTUP yaa!** 🙏\n\n🚫 **TICKET DIKUNCI!**\nMimin udah off, biar ga numpuk spam ticket, ticket dibuka lagi besok pas OPEN!\n\n💗 Makasih yang udah order hari ini!"; embed.set_image(url=THANKYOU_URL); embed.set_footer(text="MIPI STORE • CLOSED - Ticket Dikunci")
    msg = await ch.send(embed=embed); return msg
@bot.tree.command(name="open", description="Buka toko MIPI STORE (Owner/Admin only)")
async def open_cmd(interaction: discord.Interaction):
    if not is_admin_or_owner(interaction.user, interaction.guild): await interaction.response.send_message("❌ Hanya Admin / Owner!", ephemeral=True); return
    await kirim_status_openclose(interaction.guild, "open"); await interaction.response.send_message("✅ **MIPI STORE udah OPEN!** 🟢 Ticket dibuka lagi!", ephemeral=True)
@bot.tree.command(name="break", description="Break sebentar (Owner/Admin only)")
async def break_cmd(interaction: discord.Interaction):
    if not is_admin_or_owner(interaction.user, interaction.guild): await interaction.response.send_message("❌ Hanya Admin / Owner!", ephemeral=True); return
    await kirim_status_openclose(interaction.guild, "break"); await interaction.response.send_message("✅ **MIPI STORE BREAK!** 🟡 Ticket dikunci sementara!", ephemeral=True)
@bot.tree.command(name="close", description="Tutup toko MIPI STORE (Owner/Admin only)")
async def close_cmd(interaction: discord.Interaction):
    if not is_admin_or_owner(interaction.user, interaction.guild): await interaction.response.send_message("❌ Hanya Admin / Owner!", ephemeral=True); return
    await kirim_status_openclose(interaction.guild, "closed"); await interaction.response.send_message("✅ **MIPI STORE udah CLOSED!** 🔴 Ticket dikunci!", ephemeral=True)
@bot.command(name="open")
async def open_prefix(ctx):
    if not is_admin_or_owner(ctx.author, ctx.guild): await ctx.send("❌ Hanya Admin / Owner!"); return
    await kirim_status_openclose(ctx.guild, "open"); await ctx.send("✅ **MIPI STORE udah OPEN!** 🟢")
@bot.command(name="break")
async def break_prefix(ctx):
    if not is_admin_or_owner(ctx.author, ctx.guild): await ctx.send("❌ Hanya Admin / Owner!"); return
    await kirim_status_openclose(ctx.guild, "break"); await ctx.send("✅ **MIPI STORE BREAK!** 🟡")
@bot.command(name="close")
async def close_prefix(ctx):
    if not is_admin_or_owner(ctx.author, ctx.guild): await ctx.send("❌ Hanya Admin / Owner!"); return
    await kirim_status_openclose(ctx.guild, "closed"); await ctx.send("✅ **MIPI STORE udah CLOSED!** 🔴")

# ===== REKBER MIPI - PERSIS CHLOE TAPI PINK 💗 - FIX 2 KOTAK =====
rekber_data = {}; rekber_counter = 0; rekber_history = []
REKBER_FEES = [("Rp 1.000 - Rp 9.000", 1000, 9000, 1500), ("Rp 10.000 - Rp 49.000", 10000, 49000, 1500), ("Rp 50.000 - Rp 99.000", 50000, 99000, 1500), ("Rp 100.000 - Rp 199.000", 100000, 199000, 2500), ("Rp 200.000 - Rp 499.000", 200000, 499000, 4000), ("Rp 500.000 - Rp 1.000.000", 500000, 1000000, 7000), ("Di atas Rp 1.000.000", 1000001, 999999999, 10000)]
def get_fee_rekber(harga):
    for label, mn, mx, fee in REKBER_FEES:
        if mn <= harga <= mx: return label, fee
    return "Di atas Rp 1.000.000", 10000
def get_rekber_state(user_id):
    if user_id not in rekber_data: rekber_data[user_id] = {"rentang": None, "fee": 0, "rentang_label": "-", "buyer_id": None, "seller_id": None, "fee_by": None, "jenis": "-", "harga": 0, "harga_text": "-"}
    return rekber_data[user_id]
class RekberDetailModalV2(discord.ui.Modal, title="Detail Barang Middleman"):
    def __init__(self, user_id, parent_view): super().__init__(); self.user_id = user_id; self.parent_view = parent_view
    jenis = discord.ui.TextInput(label="Jenis Barang", placeholder="Contoh: Nama Item/Akun Roblox/Robux/Dll.", required=True, max_length=100)
    harga = discord.ui.TextInput(label="Harga Barang (angka saja)", placeholder="Contoh: 100000 atau 100.000", required=True, max_length=20)
    async def on_submit(self, interaction: discord.Interaction):
        hb = self.harga.value.replace(".", "").replace(",", "").replace("Rp", "").replace(" ", "")
        try: harga_int = int(hb)
        except: await interaction.response.send_message("❌ Harga harus angka!", ephemeral=True); return
        st = get_rekber_state(self.user_id); st["jenis"] = self.jenis.value; st["harga"] = harga_int; st["harga_text"] = format_rp(harga_int); self.parent_view.build(); await interaction.response.edit_message(view=self.parent_view)
class RekberStatusView(discord.ui.View):
    def __init__(self, rekber_id, data): super().__init__(timeout=None); self.rekber_id = rekber_id; self.data = data
    @discord.ui.button(label="💳 Buyer Sudah Bayar", style=discord.ButtonStyle.primary, custom_id="rekber_bayar")
    async def bayar(self, interaction: discord.Interaction, button: discord.ui.Button): await interaction.response.send_message(f"✅ {interaction.user.mention} konfirmasi **Buyer Sudah Bayar**! Admin tolong cek mutasi ya!")
    @discord.ui.button(label="📦 Seller Sudah Kirim", style=discord.ButtonStyle.primary, custom_id="rekber_kirim")
    async def kirim(self, interaction: discord.Interaction, button: discord.ui.Button): await interaction.response.send_message(f"📦 {interaction.user.mention} konfirmasi **Seller Sudah Kirim**! Buyer tolong cek barangnya ya!")
    @discord.ui.button(label="✅ Barang Diterima", style=discord.ButtonStyle.success, custom_id="rekber_terima")
    async def terima(self, interaction: discord.Interaction, button: discord.ui.Button): await interaction.response.send_message(f"✅ {interaction.user.mention} konfirmasi **Barang Diterima**! Admin, bisa teruskan duit ke Seller! 💰")
    @discord.ui.button(label="🎉 Selesai / Close", style=discord.ButtonStyle.success, custom_id="rekber_done")
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_admin_or_owner(interaction.user, interaction.guild): await interaction.response.send_message("❌ Hanya Admin yang bisa close Rekber!", ephemeral=True); return
        data_hist = None
        for h in rekber_history:
            if h["id"] == self.rekber_id: h["status"] = "SELESAI"; data_hist = h; break
        if data_hist:
            guild = interaction.guild; buyer = guild.get_member(data_hist["buyer_id"]) or data_hist["buyer"]; seller = guild.get_member(data_hist["seller_id"]) or data_hist["seller"]
            ticket_id = await kirim_history_rekber(guild, self.rekber_id, buyer, seller, data_hist["jenis"], data_hist["harga"], data_hist["fee"], data_hist["fee_by"], interaction.user)
            await interaction.response.send_message(f"🎉 Rekber `REKBER-{self.rekber_id}` **SELESAI**!\n🎫 Ticket ID: `{ticket_id}`\n📜 History sudah di-post!\nTicket akan dihapus 10 detik lagi...")
        else: await interaction.response.send_message(f"🎉 Rekber `REKBER-{self.rekber_id}` SELESAI!")
        await asyncio.sleep(10)
        try: await interaction.channel.delete()
        except: pass

# ===== PANEL MIPI - PERSIS CHLOE TAPI PINK DI SAMPING =====
class RekberPanelLayout(discord.ui.LayoutView):
    def __init__(self, guild):
        super().__init__(timeout=None); self.guild = guild
        hist_ch = None
        for ch in guild.text_channels:
            if "history" in ch.name.lower() and ("rekber" in ch.name.lower() or "midman" in ch.name.lower()): hist_ch = ch; break
        hist_url = f"https://discord.com/channels/{guild.id}/{hist_ch.id}" if hist_ch else f"https://discord.com/channels/{guild.id}"
        container = discord.ui.Container(accent_colour=discord.Colour(0xFF69B4))
        container.add_item(discord.ui.TextDisplay("## Middleman/Rekber Service by MIPI STORE"))
        btn_hist = discord.ui.Button(label="History Transaksi", style=discord.ButtonStyle.link, url=hist_url, emoji="📜")
        container.add_item(discord.ui.ActionRow(btn_hist))
        container.add_item(discord.ui.Separator(visible=True))
        container.add_item(discord.ui.TextDisplay("**Daftar Fee Middleman:**\n• Rp 1.000 - Rp 9.000 -> Fee **1.500**\n• Rp 10.000 - Rp 49.000 -> Fee **1.500**\n• Rp 50.000 - Rp 99.000 -> Fee **1.500**\n• Rp 100.000 - Rp 199.000 -> Fee **2.500**\n• Rp 200.000 - Rp 499.000 -> Fee **4.000**\n• Rp 500.000 - Rp 1.000.000 -> Fee **7.000**\n• Di atas Rp 1.000.000 -> Fee **10.000**\n\n📎 Fee dibayar 1x per transaksi\n📎 Fee bisa ditanggung buyer / seller / split"))
        container.add_item(discord.ui.Separator(visible=True))
        container.add_item(discord.ui.TextDisplay("Untuk membuat ticket middleman, klik tombol di bawah lalu pilih **buyer** dan **seller** dari dropdown member Discord."))
        container.add_item(discord.ui.Separator(visible=True))
        btn_buat = discord.ui.Button(label="Buat Ticket Middleman", style=discord.ButtonStyle.secondary, custom_id="rekber_buat_ticket", emoji="🎫")
        btn_buat.callback = self.buat_ticket_cb
        container.add_item(discord.ui.ActionRow(btn_buat))
        self.add_item(container)
    async def buat_ticket_cb(self, interaction: discord.Interaction):
        if STORE_STATUS != "open": await interaction.response.send_message("🔴 MIPI lagi BREAK / CLOSED! Rekber buka lagi pas OPEN ya!", ephemeral=True); return
        rekber_data[interaction.user.id] = {"rentang": None, "fee": 0, "rentang_label": "-", "buyer_id": None, "seller_id": None, "fee_by": None, "jenis": "-", "harga": 0, "harga_text": "-"}
        view = RekberFormV2Pink(interaction.user.id)
        await interaction.response.send_message(view=view, ephemeral=True)

# ===== FORM TICKET MIDDLEMAN - 2 KOTAK PINK, BIAR GA LIMIT 10 =====
class RekberFormV2Pink(discord.ui.LayoutView):
    def __init__(self, user_id):
        super().__init__(timeout=600); self.user_id = user_id; self.build()
    def build(self):
        st = get_rekber_state(self.user_id); self.clear_items()
        c1 = discord.ui.Container(accent_colour=discord.Colour(0xFF69B4))
        c1.add_item(discord.ui.TextDisplay(f"## 🎫 Ticket Middleman\n• Rentang Transaksi: {st['rentang_label']}\n• Fee Rekber: {format_rp(st['fee']) if st['fee'] else '-'}\n• Buyer: {f'<@{st['buyer_id']}>' if st['buyer_id'] else '-'}\n• Seller: {f'<@{st['seller_id']}>' if st['seller_id'] else '-'}\n• Fee Ditanggung: {st['fee_by'] or '-'}\n• Jenis Barang: {st['jenis']}\n• Harga Barang: {st['harga_text']}"))
        c1.add_item(discord.ui.Separator(visible=True))
        c1.add_item(discord.ui.TextDisplay("Pilih rentang harga transaksi."))
        rentang = discord.ui.StringSelect(placeholder="Pilih rentang transaksi", custom_id="rekber_rentang", options=[discord.SelectOption(label="Rp 1.000 - Rp 9.000", description="Fee: Rp 1.500", value="0"), discord.SelectOption(label="Rp 10.000 - Rp 49.000", description="Fee: Rp 1.500", value="1"), discord.SelectOption(label="Rp 50.000 - Rp 99.000", description="Fee: Rp 1.500", value="2"), discord.SelectOption(label="Rp 100.000 - Rp 199.000", description="Fee: Rp 2.500", value="3"), discord.SelectOption(label="Rp 200.000 - Rp 499.000", description="Fee: Rp 4.000", value="4"), discord.SelectOption(label="Rp 500.000 - Rp 1.000.000", description="Fee: Rp 7.000", value="5"), discord.SelectOption(label="Di atas Rp 1.000.000", description="Fee: Rp 10.000", value="6")]); rentang.callback = self.pilih_rentang; c1.add_item(discord.ui.ActionRow(rentang))
        c1.add_item(discord.ui.TextDisplay("Klik jika pembelinya kamu ->"))
        b1 = discord.ui.Button(label="Saya", style=discord.ButtonStyle.primary, custom_id="saya_buyer"); b1.callback = self.saya_buyer
        c1.add_item(discord.ui.ActionRow(b1))
        u1 = discord.ui.UserSelect(placeholder="Pilih buyer", custom_id="pilih_buyer"); u1.callback = self.pilih_buyer_cb
        c1.add_item(discord.ui.ActionRow(u1))
        c1.add_item(discord.ui.TextDisplay("Klik jika penjualnya kamu ->"))
        b2 = discord.ui.Button(label="Saya", style=discord.ButtonStyle.primary, custom_id="saya_seller"); b2.callback = self.saya_seller
        c1.add_item(discord.ui.ActionRow(b2))
        u2 = discord.ui.UserSelect(placeholder="Pilih seller", custom_id="pilih_seller"); u2.callback = self.pilih_seller_cb
        c1.add_item(discord.ui.ActionRow(u2))
        self.add_item(c1)
        c2 = discord.ui.Container(accent_colour=discord.Colour(0xFF69B4))
        c2.add_item(discord.ui.TextDisplay("Pilih yang bayar fee rekber."))
        fee_by = discord.ui.StringSelect(placeholder="Fee rekber ditanggung oleh...", custom_id="fee_by", options=[discord.SelectOption(label="Pembeli", value="Pembeli"), discord.SelectOption(label="Penjual", value="Penjual"), discord.SelectOption(label="Split (50:50)", value="Split (50:50)")]); fee_by.callback = self.pilih_fee_by; c2.add_item(discord.ui.ActionRow(fee_by))
        btn_detail = discord.ui.Button(label="Isi Detail Barang", style=discord.ButtonStyle.primary, custom_id="isi_detail", emoji="📝"); btn_detail.callback = self.isi_detail; c2.add_item(discord.ui.ActionRow(btn_detail))
        btn_buat = discord.ui.Button(label="Buat Ticket", style=discord.ButtonStyle.success, custom_id="buat_ticket", emoji="✅"); btn_buat.callback = self.buat_ticket
        btn_batal = discord.ui.Button(label="Batal", style=discord.ButtonStyle.danger, custom_id="batal", emoji="❌"); btn_batal.callback = self.batal
        c2.add_item(discord.ui.ActionRow(btn_buat, btn_batal))
        self.add_item(c2)
    async def refresh(self, interaction): self.build(); await interaction.response.edit_message(view=self)
    async def pilih_rentang(self, interaction):
        idx = int(interaction.data["values"][0]); label, mn, mx, fee = REKBER_FEES[idx]; st = get_rekber_state(self.user_id); st["rentang_label"] = label; st["fee"] = fee; await self.refresh(interaction)
    async def saya_buyer(self, interaction): st = get_rekber_state(self.user_id); st["buyer_id"] = interaction.user.id; await self.refresh(interaction)
    async def pilih_buyer_cb(self, interaction): st = get_rekber_state(self.user_id); st["buyer_id"] = int(interaction.data["values"][0]); await self.refresh(interaction)
    async def saya_seller(self, interaction): st = get_rekber_state(self.user_id); st["seller_id"] = interaction.user.id; await self.refresh(interaction)
    async def pilih_seller_cb(self, interaction): st = get_rekber_state(self.user_id); st["seller_id"] = int(interaction.data["values"][0]); await self.refresh(interaction)
    async def pilih_fee_by(self, interaction): st = get_rekber_state(self.user_id); st["fee_by"] = interaction.data["values"][0]; await self.refresh(interaction)
    async def isi_detail(self, interaction): await interaction.response.send_modal(RekberDetailModalV2(self.user_id, self))
    async def buat_ticket(self, interaction):
        global rekber_counter; st = get_rekber_state(self.user_id)
        if not st["rentang_label"] or st["rentang_label"] == "-" or not st["buyer_id"] or not st["seller_id"] or not st["fee_by"] or st["jenis"] == "-" or st["harga"] == 0: await interaction.response.send_message("❌ Lengkapi semua field dulu: rentang, buyer, seller, fee ditanggung oleh, jenis barang, dan harga barang.", ephemeral=True); return
        if st["buyer_id"] == st["seller_id"]: await interaction.response.send_message("❌ Buyer dan seller tidak boleh user yang sama.", ephemeral=True); return
        rekber_counter += 1; guild = interaction.guild; buyer = guild.get_member(st["buyer_id"]) or await guild.fetch_member(st["buyer_id"]); seller = guild.get_member(st["seller_id"]) or await guild.fetch_member(st["seller_id"])
        overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False), buyer: discord.PermissionOverwrite(read_messages=True, send_messages=True), seller: discord.PermissionOverwrite(read_messages=True, send_messages=True), interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True), guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
        cat = get_ticket_category(guild); channel = await guild.create_text_channel(name=f"rekber-{rekber_counter}-{buyer.name}-{seller.name}", overwrites=overwrites, category=cat); fee = st["fee"]
        if st["fee_by"] == "Pembeli": total_buyer = st["harga"] + fee; terima_seller = st["harga"]
        elif st["fee_by"] == "Penjual": total_buyer = st["harga"]; terima_seller = st["harga"] - fee
        else: total_buyer = st["harga"] + fee//2; terima_seller = st["harga"] - fee//2
        embed = discord.Embed(title=f"🛡️ REKBER MIPI STORE - #{rekber_counter}", description=f"**👤 Buyer:** {buyer.mention}\n**👤 Seller:** {seller.mention}\n**📦 Jenis:** {st['jenis']}\n**💰 Harga:** {format_rp(st['harga'])}\n**💸 Fee:** {format_rp(fee)} ({st['fee_by']})\n**💳 Buyer Transfer:** {format_rp(total_buyer)}\n**💰 Seller Terima:** {format_rp(terima_seller)}", color=0xFF69B4); embed.set_image(url=WELCOME_URL)
        await channel.send(f"{buyer.mention} {seller.mention} Ticket Rekber dibuat oleh {interaction.user.mention}!", embed=embed, view=RekberStatusView(rekber_counter, st))
        await channel.send(embed=discord.Embed(title="💳 Buyer Transfer Kesini", description=f"Total: {format_rp(total_buyer)}", color=0xFF69B4).set_image(url=QRIS_URL))
        rekber_history.append({"id": rekber_counter, "buyer": buyer.name, "buyer_id": st["buyer_id"], "seller": seller.name, "seller_id": st["seller_id"], "jenis": st["jenis"], "harga": st["harga"], "fee": fee, "fee_by": st["fee_by"], "status": "BERJALAN", "waktu": datetime.now().isoformat(), "channel": channel.name})
        del rekber_data[self.user_id]; await interaction.response.send_message(f"✅ Ticket Rekber dibuat! 🎫 {channel.mention}", ephemeral=True)
    async def batal(self, interaction):
        if self.user_id in rekber_data: del rekber_data[self.user_id]
        await interaction.response.edit_message(content="❌ Pembuatan Ticket Rekber dibatalkan.", view=None)

def get_history_rekber_channel(guild):
    for ch in guild.text_channels:
        if "history" in ch.name.lower() and ("rekber" in ch.name.lower() or "midman" in ch.name.lower()): return ch
    return None
def buat_ticket_id_rekber():
    kode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)); return f"T-{kode[:4]}-{kode[4:]}"
async def kirim_history_rekber(guild, rekber_id, buyer, seller, jenis, harga, fee, fee_by, admin):
    ch = get_history_rekber_channel(guild)
    if not ch: ch = await guild.create_text_channel(name="history-midman-rekber")
    ticket_id = buat_ticket_id_rekber(); tanggal = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    embed = discord.Embed(title=f"Transaksi Middleman Berhasil #{rekber_id}", description=f"**Detail Transaksi:**\n• Ticket ID: {ticket_id}\n• Pembeli: {buyer.mention if hasattr(buyer, 'mention') else buyer}\n• Penjual: {seller.mention if hasattr(seller, 'mention') else seller}\n• Jenis Barang: {jenis}\n• Nominal Transaksi: {format_rp(harga)}\n• Fee Rekber: {format_rp(fee)} ({fee_by})\n• Tanggal Transaksi: {tanggal}\n• Admin Midman: {admin.mention if hasattr(admin, 'mention') else admin}\n\nTerima kasih telah menggunakan layanan middleman MIPI STORE.", color=0x57f287)
    embed.set_footer(text="MIPI STORE • Rekber Aman 100% • Trusted"); await ch.send(embed=embed); return ticket_id
@bot.tree.command(name="setup-rekber", description="Kirim panel Rekber MIPI PINK (Owner only)")
async def setup_rekber(interaction: discord.Interaction):
    if interaction.user.id != interaction.guild.owner_id: await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    view = RekberPanelLayout(interaction.guild)
    await interaction.response.send_message(view=view)
@bot.tree.command(name="setup-history-rekber", description="Bikin channel history rekber (Owner)")
async def setup_history_rekber(interaction: discord.Interaction):
    if interaction.user.id != interaction.guild.owner_id: await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    ch = get_history_rekber_channel(interaction.guild)
    if ch: await interaction.response.send_message(f"✅ Udah ada: {ch.mention}", ephemeral=True); return
    ch = await interaction.guild.create_text_channel(name="history-midman-rekber", topic="History Transaksi Middleman / Rekber MIPI STORE")
    await ch.send(embed=discord.Embed(title="📜 History Transaksi Middleman - MIPI STORE", description="Semua transaksi Rekber yang BERHASIL akan muncul disini otomatis! 💗", color=0x57f287)); await interaction.response.send_message(f"✅ Channel history dibuat: {ch.mention}", ephemeral=True)
@bot.tree.command(name="cek-fee-rekber", description="Cek fee rekber")
async def cek_fee_rekber(interaction: discord.Interaction, harga: int):
    label, fee = get_fee_rekber(harga); await interaction.response.send_message(f"💰 Harga: {format_rp(harga)}\n📊 Rentang: {label}\n💸 Fee: **{format_rp(fee)}**", ephemeral=True)
@bot.tree.command(name="history-rekber", description="Lihat history rekber")
async def history_rekber_cmd(interaction: discord.Interaction):
    if not rekber_history: await interaction.response.send_message("Belum ada transaksi Rekber!", ephemeral=True); return
    desc = "**📜 HISTORY REKBER**\n\n"
    for h in rekber_history[-15:]: desc += f"• `REKBER-{h['id']}` - {h['jenis']} - {format_rp(h['harga'])} - Fee {format_rp(h['fee'])} - {h['status']}\n"
    await interaction.response.send_message(embed=discord.Embed(description=desc, color=0xff69b4), ephemeral=True)
@bot.tree.command(name="blacklist", description="Blacklist user (Admin)")
async def blacklist_cmd(interaction: discord.Interaction, user: discord.Member):
    if not is_admin_or_owner(interaction.user, interaction.guild): await interaction.response.send_message("❌ Hanya Admin!", ephemeral=True); return
    if not hasattr(bot, "blacklist_data"): bot.blacklist_data = set()
    bot.blacklist_data.add(user.id); await interaction.response.send_message(f"⛔ {user.mention} di-blacklist!", ephemeral=True)
@bot.tree.command(name="unblacklist", description="Unblacklist user (Admin)")
async def unblacklist_cmd(interaction: discord.Interaction, user: discord.Member):
    if not is_admin_or_owner(interaction.user, interaction.guild): await interaction.response.send_message("❌ Hanya Admin!", ephemeral=True); return
    if hasattr(bot, "blacklist_data"): bot.blacklist_data.discard(user.id)
    await interaction.response.send_message(f"✅ {user.mention} di-unblacklist!", ephemeral=True)
@bot.tree.command(name="status", description="Cek status toko")
async def status_cmd(interaction: discord.Interaction): await interaction.response.send_message(f"🏪 MIPI STORE - Status: **{STORE_STATUS.upper()}**", ephemeral=True)
@bot.tree.command(name="open-toko", description="Buka toko (Owner)")
async def open_toko(interaction: discord.Interaction):
    if interaction.user.id != interaction.guild.owner_id: await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    await kirim_status_openclose(interaction.guild, "open"); await interaction.response.send_message("🟢 MIPI STORE DIBUKA!", ephemeral=True)
@bot.tree.command(name="close-toko", description="Tutup toko (Owner)")
async def close_toko(interaction: discord.Interaction):
    if interaction.user.id != interaction.guild.owner_id: await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    await kirim_status_openclose(interaction.guild, "closed"); await interaction.response.send_message("🔴 MIPI STORE DITUTUP!", ephemeral=True)

bot.run(os.getenv("DISCORD_TOKEN"))
