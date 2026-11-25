# ===== MIPI STORE - PART 1 / 3 - KODE ASAL KAMU =====
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
TOP_SULTAN_IMAGE = QRIS_URL

ticket_data = {}
ticket_counter = 0
user_ratings = {}
user_last_ticket = {}
STORE_STATUS = "open"
STORE_STATUS_MSG = ""
OPEN_CLOSE_CHANNEL_ID = 1569135504262299689

# ===== PRICELIST - DINAMIS =====
PRICELIST_FILE = "pricelist.json"
DEFAULT_PRICELIST = {100: 16000, 200: 32000, 300: 48000, 400: 64000, 500: 75000, 1000: 150000, 2000: 300000, 3000: 450000, 4000: 600000, 5000: 750000}
def load_pricelist():
    try:
        with open(PRICELIST_FILE, "r") as f:
            data = json.load(f)
            return {int(k): int(v) for k, v in data.items()}
    except: return DEFAULT_PRICELIST.copy()
def save_pricelist(data):
    with open(PRICELIST_FILE, "w") as f: json.dump({str(k): v for k, v in data.items()}, f, indent=2)
def get_harga(robux):
    data = load_pricelist()
    if robux in data: return data[robux]
    return robux * 150
def format_rp(nominal): return f"Rp {nominal:,}".replace(",", ".")
PRICELIST = load_pricelist()
def build_pricelist_text():
    data = load_pricelist()
    fast = ""; ecer = ""
    for rbx in sorted(data.keys()):
        harga = format_rp(data[rbx])
        if rbx >= 500: fast += f"{rbx} = {harga}\n"
        else: ecer += f"{rbx} = {harga}\n"
    return f"{fast}\nRobux Eceran\n{ecer}\nCara Order\nClick tombol ORDER ROBUX dibawah, isi formulir, lalu tunggu admin. Pembayaran hanya QRIS."
def build_pricelist_embed():
    e = discord.Embed(title="PRICELIST ROBUX FAST SEND", description=build_pricelist_text(), color=0xff69b4)
    e.set_image(url=QRIS_URL); e.set_footer(text="Mipi Store - Rafi Store"); return e

# ===== LEADERBOARD + PENDING SALDO =====
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
    data[bulan][uid]["username"] = username
    data[bulan][uid]["total"] += jumlah; data[bulan][uid]["transaksi"] += 1; data[bulan][uid]["total_rp"] += harga
    save_leaderboard(data)
def get_total_belanja(user_id):
    data = load_leaderboard(); total_rp = 0; total_robux = 0; total_transaksi = 0
    for bulan, users in data.items():
        uid = str(user_id)
        if uid in users:
            total_rp += users[uid].get("total_rp", 0); total_robux += users[uid].get("total", 0); total_transaksi += users[uid].get("transaksi", 0)
    return total_rp, total_robux, total_transaksi
PENDING_FILE = "pending_saldo.json"
def load_pending():
    try:
        with open(PENDING_FILE, "r") as f: return json.load(f)
    except: return {}
def save_pending(d):
    with open(PENDING_FILE, "w") as f: json.dump(d, f, indent=2)
def add_to_pending(user_id, username, paket_text, ticket_number, channel_name=""):
    m = re.search(r'(\d+)', str(paket_text).replace('.', '').replace(',', ''))
    if not m: return None
    jumlah = int(m.group(1)); harga = get_harga(jumlah)
    data = load_pending(); order_id = f"ORDER-{ticket_number:06d}"
    data[order_id] = {"user_id": str(user_id), "username": username, "paket": paket_text, "robux": jumlah, "harga": harga, "ticket_number": ticket_number, "channel": channel_name, "waktu": datetime.now().strftime("%d %b %Y %H:%M")}
    save_pending(data); return order_id

# ===== TOP SULTAN AUTO =====
def get_top_sultan_channel(guild):
    for ch in guild.text_channels:
        if "top-sultan" in ch.name.lower() or "top-leaderboard" in ch.name.lower(): return ch
    return None
def build_top_sultan_embed():
    data = load_leaderboard(); gabung = {}
    for bulan, users in data.items():
        for uid, info in users.items():
            if uid not in gabung: gabung[uid] = {"username": info.get("username","User"), "total_rp": 0, "total": 0, "transaksi": 0}
            gabung[uid]["total_rp"] += info.get("total_rp", 0); gabung[uid]["total"] += info.get("total", 0); gabung[uid]["transaksi"] += info.get("transaksi", 0); gabung[uid]["username"] = info.get("username", gabung[uid]["username"])
    sorted_users = sorted(gabung.items(), key=lambda x: x[1]["total_rp"], reverse=True)[:10]
    total_pembeli = len(gabung); total_pesanan = sum(v["transaksi"] for v in gabung.values()); total_omset = sum(v["total_rp"] for v in gabung.values())
    desc = "MIPI STORE • LEADERBOARD PELANGGAN TERBAIK\nDaftar peringkat pelanggan setia dengan akumulasi nominal pembelian tertinggi di toko kami.\n\n"
    if not sorted_users: desc += "> Belum ada Sultan! Order dulu, jadi #1!\n\n"
    else:
        medals = ["🥇","🥈","🥉"]
        for i, (uid, info) in enumerate(sorted_users):
            medal = medals[i] if i < 3 else "🏅"
            desc += f"{medal} **Peringkat #{i+1} - <@{uid}>** ({info['username']})\n"
            desc += f"└ Rp {info['total_rp']:,} • {info['transaksi']}x Transaksi\n".replace(",", ".")
    desc += f"\n📊 **STATISTIK TRANSAKSI**\n• Pembeli: {total_pembeli} Pembeli\n• Pesanan: {total_pesanan} Pesanan\n• Omset: Rp {total_omset:,}\n".replace(",", ".")
    desc += f"\n⚡ Papan leaderboard ini otomatis ter-update setiap 1 menit & setiap ada transaksi baru.\n🕒 Terakhir diperbarui: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB"
    e = discord.Embed(title="🏆 TOP 10 SULTAN MIPI STORE", description=desc, color=0x2B2D31)
    e.set_image(url=TOP_SULTAN_IMAGE); e.set_footer(text="MIPI STORE - TOP SULTAN • Auto Update"); return e
async def update_top_sultan(guild):
    ch = get_top_sultan_channel(guild)
    if not ch: return
    embed = build_top_sultan_embed()
    try:
        async for msg in ch.history(limit=20):
            if msg.author == guild.me and msg.embeds and "TOP 10 SULTAN" in str(msg.embeds[0].title):
                await msg.edit(embed=embed); return
        await ch.send(embed=embed)
    except Exception as e: print(f"Gagal update top-sultan: {e}")
@tasks.loop(minutes=1)
async def auto_update_top_sultan():
    for guild in bot.guilds:
        try: await update_top_sultan(guild)
        except: pass
def is_admin_or_owner(user, guild):
    if user.id == guild.owner_id: return True
    if user.guild_permissions.administrator: return True
    role_names = [r.name.lower() for r in user.roles]; return any(x in role_names for x in ["admin", "owner", "staff", "moderator", "adm"])
class KonfirmasiSaldoView(discord.ui.View):
    def __init__(self, order_id):
        super().__init__(timeout=None); self.order_id = order_id
    @discord.ui.button(label="✅ Konfirmasi Masuk Saldo", style=discord.ButtonStyle.success, custom_id="saldo_confirm_btn")
    async def confirm_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_admin_or_owner(interaction.user, interaction.guild):
            await interaction.response.send_message("❌ Hanya Admin / Owner!", ephemeral=True); return
        pend = load_pending()
        if self.order_id not in pend:
            await interaction.response.send_message("❌ Udah dikonfirmasi / ditolak!", ephemeral=True); return
        d = pend[self.order_id]
        add_to_leaderboard(int(d["user_id"]), d["username"], d["paket"])
        del pend[self.order_id]; save_pending(pend)
        await interaction.response.send_message(f"✅ **SALDO DIKONFIRMASI!**\nBuyer: <@{d['user_id']}>\nPaket: {d['paket']}\n+{d['robux']} R$ udah masuk saldo + Top Sultan!", ephemeral=False)
        for item in self.children: item.disabled = True
        try: await interaction.message.edit(view=self)
        except: pass
        try: await update_top_sultan(interaction.guild)
        except: pass
        try:
            u = await bot.fetch_user(int(d["user_id"])); await u.send(f"🎉 Saldo kamu ditambah! +{d['robux']} R$ dari {d['paket']} udah dikonfirmasi admin!")
        except: pass
    @discord.ui.button(label="❌ Tolak / Order Palsu", style=discord.ButtonStyle.danger, custom_id="saldo_reject_btn")
    async def reject_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_admin_or_owner(interaction.user, interaction.guild):
            await interaction.response.send_message("❌ Hanya Admin / Owner!", ephemeral=True); return
        pend = load_pending()
        if self.order_id not in pend:
            await interaction.response.send_message("❌ Udah diproses!", ephemeral=True); return
        d = pend[self.order_id]; del pend[self.order_id]; save_pending(pend)
        await interaction.response.send_message(f"❌ Order {self.order_id} ({d['paket']} - <@{d['user_id']}>) **DITOLAK**, ga masuk saldo!", ephemeral=False)
        for item in self.children: item.disabled = True
        try: await interaction.message.edit(view=self)
        except: pass
        try: await update_top_sultan(interaction.guild)
        except: pass

# ===== PROMO =====
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
    if kode not in data: return harga_awal, 0, "Kode promo tidak ditemukan!"
    p = data[kode]
    if jumlah_robux < 500: return harga_awal, 0, "Minimal belanja 500 Robux untuk pakai promo ini!"
    if p.get("dipakai", 0) >= p.get("max", 999): return harga_awal, 0, "Kode promo sudah habis dipakai!"
    diskon = int(harga_awal * p["diskon"] / 100) if p["tipe"] == "persen" else int(p["diskon"])
    return max(0, harga_awal - diskon), diskon, None

# ===== GIVEAWAY =====
giveaway_data = {}
class GiveawayView(discord.ui.View):
    def __init__(self, giveaway_id):
        super().__init__(timeout=None); self.giveaway_id = giveaway_id
    @discord.ui.button(label="JOIN GIVEAWAY", style=discord.ButtonStyle.success, custom_id="join_giveaway", emoji="🎉")
    async def join_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = giveaway_data.get(self.giveaway_id)
        if not data: await interaction.response.send_message("Giveaway ini sudah berakhir!", ephemeral=True); return
        if data["ended"]: await interaction.response.send_message("Giveaway sudah berakhir Wal!", ephemeral=True); return
        uid = interaction.user.id
        if uid in data["peserta"]: await interaction.response.send_message("Kamu udah join Wal!", ephemeral=True); return
        data["peserta"].append(uid)
        try:
            embed = interaction.message.embeds[0]; embed.description = "Hadiah: " + str(data["hadiah"]) + "\nHost: " + str(data["host_mention"]) + "\nPeserta: " + str(len(data["peserta"])) + " orang"; await interaction.message.edit(embed=embed, view=self)
        except: pass
        await interaction.response.send_message("Berhasil join giveaway " + str(data["hadiah"]) + "! Good luck!", ephemeral=True)
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
                embed = discord.Embed(title="GIVEAWAY BERAKHIR - GAK ADA PESERTA", description="Hadiah: " + str(data["hadiah"]), color=0xff0000); await msg.edit(embed=embed, view=None)
            await channel.send("Giveaway berakhir tapi gak ada yang join!"); return
        winners = random.sample(data["peserta"], min(data["pemenang"], len(data["peserta"]))); winner_mentions = ", ".join([f"<@{w}>" for w in winners])
        if msg:
            embed = discord.Embed(title="GIVEAWAY BERAKHIR - PEMENANG TERPILIH!", description="Hadiah: " + str(data["hadiah"]) + "\n\nPemenang:\n" + winner_mentions + "\n\nTotal Peserta: " + str(len(data["peserta"])) + " orang", color=0x57f287); await msg.edit(embed=embed, view=None)
        await channel.send("GIVEAWAY BERAKHIR!\n\nHadiah: " + str(data["hadiah"]) + "\nPemenang: " + winner_mentions)
    except Exception as e: print(f"Gagal end giveaway: {e}")

# ===== HELPER =====
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
    for m in messages: rows += "<div style=\"margin:6px 0;padding:8px;background:#2b2d31;border-radius:8px;\"><b style=\"color:#fff;\">" + html.escape(str(m["author"])) + "</b> <span style=\"color:#949ba4;font-size:12px;\">" + m["time"] + "</span><br><span style=\"color:#dbdee1;\">" + html.escape(m["content"] or "(gambar / embed)") + "</span></div>"
    return "<!DOCTYPE html><html><head><meta charset=\"utf-8\"><title>Ticket #" + str(number) + " Transcript - MIPI STORE</title></head><body style=\"background:#1e1f22;font-family:sans-serif;padding:20px;\"><h2 style=\"color:white;\">MIPI STORE - Ticket #" + str(number) + "</h2><p style=\"color:#949ba4;\">Created by " + html.escape(username) + " | Subject: " + html.escape(paket) + " | Duration: " + str(duration) + " minutes | " + str(len(messages)) + " messages</p>" + rows + "</body></html>"
async def send_status_update(guild, number, username, user_id, paket, status_text, color):
    ch = get_status_channel(guild)
    if not ch: return
    embed = discord.Embed(title="Order Status - Ticket #" + str(number), description="Customer: <@" + str(user_id) + "> (" + username + ")\nPaket: " + paket + "\nStatus: " + status_text, color=color)
    embed.set_footer(text="MIPI STORE - Order Status"); await ch.send(embed=embed)
async def send_history_log(guild, channel, data, admin_user):
    ch = get_history_channel(guild)
    if not ch: return
    number = data["number"]; user_id = data["user_id"]; roblox_user = data.get("roblox_username", data.get("username", "-")); nickname = data.get("nickname", "-"); paket = data.get("paket", "500 Robux"); pembayaran = data.get("pembayaran", "Qris"); jumlah, harga = hitung_harga(paket); ticket_name = channel.name if channel else "robux-via-username-" + str(number) + "-" + str(data.get("username", "user")); admin_text = admin_user.mention if admin_user else "Auto-Close"
    embed = discord.Embed(color=0x2b2d31); embed.description = "Ticket Log\n\nTicket\n" + ticket_name + "\nAction\nClosed\nPanel\nRobux Via Username\nMember\n<@" + str(user_id) + ">\nNickname Roblox\n" + nickname + "\nUsername Roblox\n" + roblox_user + "\nJumlah Robux\n" + jumlah + "\nTotal Harga\n" + harga + "\nPayment\n" + pembayaran + "\nAdmin\n" + admin_text; embed.set_image(url=THANKYOU_URL); await ch.send(embed=embed)
async def send_vouch(guild, user, paket, stars, komentar, ticket_number=0, ticket_name=""):
    ch = get_vouch_channel(guild)
    if not ch: return
    jumlah, harga = hitung_harga(paket); star_str = "⭐" * stars; seller = guild.owner.mention if guild.owner else "MIPI STORE"
    if not ticket_name: ticket_name = "robux-via-username-" + str(ticket_number) + "-" + user.name
    embed = discord.Embed(color=0x2b2d31); embed.description = "VOUCH RECEIVED\n\nTicket ID\n" + str(ticket_number) + "\nNominal\n" + harga + "\nSeller\n" + seller + "\nBuyer\n<@" + str(user.id) + ">\nHandled by\n" + seller + "\nRating\n" + star_str + "\nKomentar\n" + komentar + " 💗\nSource\n" + ticket_name; embed.set_thumbnail(url=user.display_avatar.url); embed.set_footer(text="MIPI STORE Vouch System | " + datetime.now().strftime("%B %d, %Y at %I:%M %p"))
    msg = await ch.send(embed=embed)
    try:
        thread_name = "Vouch - " + user.name + " | Ticket #" + str(ticket_number)
        if isinstance(ch, discord.ForumChannel): await ch.create_thread(name=thread_name, content="Vouch dari " + user.mention + " - Ticket #" + str(ticket_number) + " - " + paket + " - " + star_str + " - " + komentar)
        else:
            thread = await msg.create_thread(name=thread_name, auto_archive_duration=1440); await thread.send("Vouch dari " + user.mention + "\n\nPaket: " + paket + " (" + harga + ")\nRating: " + star_str + "\nKomentar: " + komentar + "\nTicket: " + ticket_name)
    except Exception as e: print(f"Gagal buat thread vouch: {e}")

# ===== AUTO CLOSE =====
async def do_auto_close(guild, channel, data, reason="auto-closed due to inactivity", admin_user=None):
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
        embed1 = discord.Embed(title="Ticket Auto-Closed", description="#" + str(number) + " " + reason + "\nTicket ID\n" + str(number), color=0xfee75c); embed1.set_footer(text=datetime.now().strftime("%B %d, %Y at %I:%M %p")); await status_ch.send(embed=embed1)
        html_text = make_html_transcript(number, messages, data.get("username", "User"), paket, duration); file = discord.File(io.BytesIO(html_text.encode()), filename="ticket-" + str(number) + "-auto-transcript.html")
        embed2 = discord.Embed(title="Auto-Generated Transcript (Auto-Closed)", description="Transcript automatically generated for auto-closed ticket #" + str(number) + "\n\nTicket\nTicket #" + str(number) + "\nCreated by <@" + str(user_id) + ">\n" + str(len(messages)) + " messages\n\nGeneration\nDuration: " + str(duration) + " minutes\nStatus: Auto-Closed -> Auto-Transcript\n\nSubject\n" + paket, color=0x5865f2); embed2.set_footer(text=datetime.now().strftime("%B %d, %Y at %I:%M %p")); await status_ch.send(embed=embed2, file=file)
    try:
        user = await bot.fetch_user(user_id); closer = admin_user.name if admin_user else "MIPI STORE (Auto-Close)"; embed = discord.Embed(title="Rate Your Experience", description="Hi " + user.name + "! Your support ticket has been resolved.\nPlease rate your experience by clicking a star below.\n\nTicket #" + str(number) + " in ORDER ROBUX\nResolved in\n" + str(duration) + " minutes\n\nClosed by\n" + closer, color=0x2b2d31); await user.send(embed=embed, view=RatingView(number))
    except: pass
    try:
        order_id = add_to_pending(user_id, data.get("username", "User"), paket, number, channel.name if channel else "")
        if order_id:
            ch_pending = get_history_channel(guild) or get_status_channel(guild)
            if ch_pending:
                jumlah_tmp, harga_tmp = hitung_harga(paket)
                embed_p = discord.Embed(title=f"⏳ PENDING SALDO - {order_id}", description=f"Buyer: <@{user_id}>\nPaket: {paket}\nRobux: {jumlah_tmp} R$\nHarga: {harga_tmp}\nTicket: #{number}\n\n**Order ini BELUM masuk leaderboard!**\nAdmin harus pencet ✅ dulu baru masuk saldo!", color=0xfee75c)
                await ch_pending.send(embed=embed_p, view=KonfirmasiSaldoView(order_id))
    except Exception as e: print(f"Gagal pending saldo: {e}")
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

# ===== RATING / VOUCH =====
class RatingView(discord.ui.View):
    def __init__(self, ticket_number):
        super().__init__(timeout=None); self.ticket_number = ticket_number
    async def send_thanks(self, interaction, stars):
        user_ratings[interaction.user.id] = stars; star_str = "⭐" * stars; embed = discord.Embed(title="Terima Kasih! 💗", description="Kamu memberi rating " + star_str + " (" + str(stars) + "/5) untuk MIPI STORE!\n\nTerima kasih sudah order di Mipi Store! Ditunggu order berikutnya ya 🌸", color=0xff69b4); embed.set_image(url=THANKYOU_URL); await interaction.response.edit_message(embed=embed, view=self)
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
        stars = user_ratings.get(interaction.user.id, 5); last = user_last_ticket.get(interaction.user.id, {}); paket = last.get("paket", "500 Robux"); ticket_name = last.get("ticket_name", "robux-via-username-" + str(self.ticket_number) + "-" + interaction.user.name)
        try:
            guild = None
            for g in bot.guilds:
                ch = get_vouch_channel(g)
                if ch: guild = g; break
            if guild: await send_vouch(guild, interaction.user, paket, stars, self.komentar.value, ticket_number=self.ticket_number, ticket_name=ticket_name)
        except Exception as e: print(f"Gagal vouch: {e}")
        await interaction.response.send_message("Terima kasih komentarnya! 💗\n> " + self.komentar.value + "\n\nVouch kamu sudah muncul di vouch + jadi thread! 🎉\nRating: " + ("⭐"*stars) + " (" + str(stars) + "/5)", ephemeral=True)

# ===== STATUS + CLOSE + SALDO VIEW =====
class StatusView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="⏳ Menunggu Pembayaran", style=discord.ButtonStyle.secondary, custom_id="status_waiting")
    async def waiting(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not is_admin_or_owner(interaction.user, interaction.guild): await interaction.followup.send("Hanya Admin & Owner yang bisa update status!", ephemeral=True); return
        data = ticket_data.get(interaction.channel.id, {})
        if data: data["last_activity"] = time.time()
        await interaction.followup.send("Status diubah: Menunggu Pembayaran"); await send_status_update(interaction.guild, data.get("number", "?"), data.get("username", interaction.user.name), data.get("user_id", interaction.user.id), data.get("paket", "ORDER ROBUX"), "Menunggu Pembayaran", 0xfee75c)
    @discord.ui.button(label="🔄 Diproses", style=discord.ButtonStyle.primary, custom_id="status_process")
    async def process(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not is_admin_or_owner(interaction.user, interaction.guild): await interaction.followup.send("Hanya Admin & Owner yang bisa update status!", ephemeral=True); return
        data = ticket_data.get(interaction.channel.id, {})
        if data: data["last_activity"] = time.time()
        await interaction.followup.send("Status diubah: Sedang Diproses"); await send_status_update(interaction.guild, data.get("number", "?"), data.get("username", interaction.user.name), data.get("user_id", interaction.user.id), data.get("paket", "ORDER ROBUX"), "Sedang Diproses", 0x5865f2)
    @discord.ui.button(label="✅ Selesai", style=discord.ButtonStyle.success, custom_id="status_done")
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not is_admin_or_owner(interaction.user, interaction.guild): await interaction.response.send_message("Hanya Admin & Owner yang bisa update status!", ephemeral=True); return
        data = ticket_data.get(interaction.channel.id, {})
        if data: data["last_activity"] = time.time()
        await interaction.followup.send("Status diubah: Selesai - Robux sudah masuk!"); await send_status_update(interaction.guild, data.get("number", "?"), data.get("username", interaction.user.name), data.get("user_id", interaction.user.id), data.get("paket", "ORDER ROBUX"), "Selesai / Done", 0x57f287)
class CloseView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🔒 CLOSE TICKET", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not is_admin_or_owner(interaction.user, interaction.guild): await interaction.followup.send("Hanya Admin & Owner yang bisa menutup ticket ini!", ephemeral=True); return
        channel = interaction.channel; data = ticket_data.get(channel.id)
        if not data: await interaction.followup.send("Ticket ditutup..."); await channel.delete(); return
        await interaction.followup.send("Ticket ditutup oleh " + interaction.user.mention + ". Membuat transcript..."); await do_auto_close(interaction.guild, channel, data, reason="closed by owner", admin_user=interaction.user)
class SaldoView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="💳 CEK SALDO SAYA", style=discord.ButtonStyle.primary, custom_id="cek_saldo_btn")
    async def cek_saldo(self, interaction: discord.Interaction, button: discord.ui.Button):
        total_rp, total_robux, total_transaksi = get_total_belanja(interaction.user.id); harga_str = f"Rp {total_rp:,}".replace(",", "."); embed = discord.Embed(color=0xff1493); embed.description = "INFORMASI SALDO / TOTAL TRANSAKSI\n\nHalo " + interaction.user.mention + ",\n\nTotal Belanja: " + harga_str + "\nTotal Robux: " + str(total_robux) + " R$\nTotal Transaksi: " + str(total_transaksi) + "x\n\nMIPI STORE - CHECK SALDO"; embed.set_footer(text="Mipi Store - Rafi Store"); await interaction.response.send_message(embed=embed, ephemeral=True)

# ===== ORDER MODAL + VIEW =====
class OrderModal(discord.ui.Modal, title="Pesanan Robux"):
    nickname = discord.ui.TextInput(label="Nickname Roblox", placeholder="Nickname Roblox kamu", required=True)
    username = discord.ui.TextInput(label="Username", placeholder="UsernameRoblox", required=True)
    paket = discord.ui.TextInput(label="Paket yang dipilih", placeholder="Contoh: 500 Robux", required=True)
    pembayaran = discord.ui.TextInput(label="Metode Pembayaran", placeholder="QRIS", default="QRIS", required=True)
    kode_promo = discord.ui.TextInput(label="Kode Promo (Opsional)", placeholder="Contoh: MIPI10 - Kosongin aja kalau gak ada", required=False)
    async def on_submit(self, interaction: discord.Interaction):
        global ticket_counter; ticket_counter += 1; guild = interaction.guild
        overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False), interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True), guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
        category = get_ticket_category(guild); channel = await guild.create_text_channel(name="robux-via-username-" + str(ticket_counter) + "-" + interaction.user.name, overwrites=overwrites, category=category)
        m_temp = re.search(r'(\d+)', str(self.paket.value).replace('.', '')); jumlah_int = int(m_temp.group(1)) if m_temp else 500; harga_awal = get_harga(jumlah_int); kode_input = self.kode_promo.value.strip() if self.kode_promo.value else ""; harga_akhir, diskon, err_promo = cek_promo(kode_input, harga_awal, jumlah_int); promo_text = ""
        if kode_input and not err_promo and diskon > 0:
            pdata = load_promo(); k_up = kode_input.upper()
            if k_up in pdata: pdata[k_up]["dipakai"] = pdata[k_up].get("dipakai", 0) + 1; save_promo(pdata)
            promo_text = "\nKode Promo: " + k_up + " (-" + format_rp(diskon) + ")\nHarga Setelah Diskon: " + format_rp(harga_akhir)
        elif kode_input and err_promo: promo_text = "\nKode Promo: " + kode_input.upper() + " - " + err_promo + " (Harga normal)\nHarga: " + format_rp(harga_awal)
        ticket_data[channel.id] = {"user_id": interaction.user.id, "username": interaction.user.name, "nickname": self.nickname.value, "roblox_username": self.username.value, "pembayaran": self.pembayaran.value, "created_at": time.time(), "last_activity": time.time(), "number": ticket_counter, "paket": self.paket.value, "promo": kode_input, "harga_akhir": harga_akhir}
        embed = discord.Embed(title="Ticket Baru - " + interaction.user.name, description="Nickname Roblox: " + self.nickname.value + "\nUsername Roblox: " + self.username.value + "\nPaket: " + self.paket.value + "\nPembayaran: " + self.pembayaran.value + promo_text + "\nTicket #" + str(ticket_counter) + "\n\nSilahkan kirim bukti pembayaran QRIS disini ya 💗", color=0xff69b4); embed.set_image(url=WELCOME_URL); await channel.send(interaction.user.mention + " Halo! Selamat datang di MIPI STORE! 🌸", embed=embed, view=CloseView())
        embed_qris = discord.Embed(title="Scan QRIS Disini", description="Silahkan scan QRIS ini untuk pembayaran ya 💗", color=0xff69b4); embed_qris.set_image(url=QRIS_URL); await channel.send(embed=embed_qris); await channel.send("STATUS ORDER - Owner only:", view=StatusView()); await send_status_update(guild, ticket_counter, interaction.user.name, interaction.user.id, self.paket.value, "Ticket Baru Dibuat", 0xff69b4)
        go_view = discord.ui.View(); go_view.add_item(discord.ui.Button(label="BUKA TICKET SAYA", style=discord.ButtonStyle.link, url="https://discord.com/channels/" + str(guild.id) + "/" + str(channel.id), emoji="🚀")); await interaction.response.send_message("Ticket kamu sudah dibuat!\nPencet tombol dibawah untuk langsung masuk ke ticket kamu 👇\n" + channel.mention, view=go_view, ephemeral=True)
        try: await interaction.user.send("Ticket MIPI STORE kamu sudah dibuat!\nNickname: " + self.nickname.value + "\nUsername: " + self.username.value + "\nPaket: " + self.paket.value + "\nLangsung klik disini ya: " + channel.mention + "\nLink: https://discord.com/channels/" + str(guild.id) + "/" + str(channel.id) + "\n\nKirim bukti QRIS kamu disana ya 💗")
        except: pass
class OrderView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="ORDER ROBUX", style=discord.ButtonStyle.primary, custom_id="order_robux")
    async def order_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if STORE_STATUS == "break":
            embed = discord.Embed(color=0xfee75c); embed.description = "MIPI STORE LAGI BREAK! ☕\n\nMimin break sebentar yaa, 15-30 menit aja!\n\nTicket lagi dikunci sementara biar Mimin bisa istirahat dulu!\nTunggu sampe Mimin OPEN lagi yaa, jangan spam pencet tombol!\n\nMakasih udah ngerti! 💗"; await interaction.response.send_message(embed=embed, ephemeral=True); return
        if STORE_STATUS == "closed":
            embed = discord.Embed(color=0xff0000); embed.description = "MIPI STORE UDAH TUTUP! 💤\n\nMohon maaf yaa, toko udah TUTUP!\n\nTicket lagi dikunci biar ga numpuk!\nOrderan kamu bakal dibales besok pas Mimin OPEN lagi!\n\nMakasih udah mampir hari ini! Sampai ketemu besok! 💗"; await interaction.response.send_message(embed=embed, ephemeral=True); return
        await interaction.response.send_modal(OrderModal())
# ===== END PART 1 / 3 =====
# ===== MIPI STORE - PART 2 / 3 =====
@bot.event
async def on_message(message):
    if message.author.bot: return
    if message.guild and "market" in message.channel.name.lower():
        if message.author.id != message.guild.owner_id and not message.author.guild_permissions.administrator:
            if is_banned_selling(message.content):
                try: await message.delete()
                except: pass
                embed = discord.Embed(title="Stickied Message:", description="DILARANG MENJUAL PRODUK YANG KAMI JUAL SEPERTI ROBUX DAN LIMITED ITEM", color=0xff0000)
                warn = await message.channel.send(message.author.mention, embed=embed)
                await asyncio.sleep(10)
                try: await warn.delete()
                except: pass
                try: await message.author.send("Pesan kamu di #" + message.channel.name + " dihapus!\n\nAlasan: Dilarang menjual produk yang kami jual seperti Robux dan Limited Item di MIPI STORE!")
                except: pass
                return
    if message.channel.id in ticket_data: ticket_data[message.channel.id]["last_activity"] = time.time()
    await bot.process_commands(message)
@bot.event
async def on_ready():
    print(f"Login {bot.user}")
    bot.add_view(OrderView()); bot.add_view(CloseView()); bot.add_view(StatusView()); bot.add_view(RatingView(0)); bot.add_view(SaldoView()); bot.add_view(GiveawayView("dummy"))
    for oid in load_pending().keys(): bot.add_view(KonfirmasiSaldoView(oid))
    if not check_inactive.is_running(): check_inactive.start()
    if not auto_update_top_sultan.is_running(): auto_update_top_sultan.start()
    for g in bot.guilds:
        try: await update_top_sultan(g)
        except: pass
    try: await bot.tree.sync()
    except Exception as e: print(f"Sync error: {e}")

# ===== TICKET - VERSI BARU AUTO-UPDATE (ISI SAMA PERSIS KAYA PUNYA KAMU + SIMPEN ID PANEL) =====
# Biar /ticket ga numpuk lagi, sekarang dia EDIT pesan lama kalo udah pernah dibikin
PANEL_FILE = "panel.json"
def load_panel():
    try:
        with open(PANEL_FILE, "r") as f: return json.load(f)
    except: return {}
def save_panel(d):
    with open(PANEL_FILE, "w") as f: json.dump(d, f, indent=2)
async def update_all_panels(guild):
    panels = load_panel()
    for key, info in list(panels.items()):
        try:
            ch = guild.get_channel(int(info["channel_id"]))
            if not ch: continue
            msg = await ch.fetch_message(int(info["message_id"]))
            if key == "ticket":
                e1 = discord.Embed(title="Mipi Store - Order Robux 💗", description="ROBUX VIA USERNAME\nFast Process - Aman - Instan\n\nSyarat top up via username:\n>> SUDAH 18+\n>> SUDAH TERVERIFIKASI 2 LANGKAH", color=0xff69b4); e1.set_image(url=WELCOME_URL)
                await msg.edit(embeds=[e1, build_pricelist_embed()], view=OrderView())
        except: pass

@bot.tree.command(name="ticket", description="Tampilkan panel order MIPI STORE")
async def ticket(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        if STORE_STATUS != "open":
            status_text = "BREAK - Mimin break 15-30 menit!" if STORE_STATUS == "break" else "CLOSED - Toko tutup, balik besok yaa!"
            await interaction.followup.send(status_text + "\n\nTicket lagi dikunci sementara biar ga spam! Tunggu OPEN lagi yaa! 💗", ephemeral=True); return
        panels = load_panel()
        if "ticket" in panels:
            try:
                ch = interaction.guild.get_channel(int(panels["ticket"]["channel_id"])); msg = await ch.fetch_message(int(panels["ticket"]["message_id"]))
                embed1 = discord.Embed(title="Mipi Store - Order Robux 💗", description="ROBUX VIA USERNAME\nFast Process - Aman - Instan\n\nSyarat top up via username:\n>> SUDAH 18+\n>> SUDAH TERVERIFIKASI 2 LANGKAH", color=0xff69b4); embed1.set_image(url=WELCOME_URL)
                await msg.edit(embeds=[embed1, build_pricelist_embed()], view=OrderView())
                await interaction.followup.send(f"✅ Panel udah di-update, ga bikin baru! Cek {ch.mention}", ephemeral=True); return
            except: pass
        embed1 = discord.Embed(title="Mipi Store - Order Robux 💗", description="ROBUX VIA USERNAME\nFast Process - Aman - Instan\n\nSyarat top up via username:\n>> SUDAH 18+\n>> SUDAH TERVERIFIKASI 2 LANGKAH", color=0xff69b4); embed1.set_image(url=WELCOME_URL)
        embed2 = build_pricelist_embed()
        msg = await interaction.followup.send(embeds=[embed1, embed2], view=OrderView())
        panels["ticket"] = {"channel_id": str(msg.channel.id), "message_id": str(msg.id)}; save_panel(panels)
    except Exception as e:
        print(f"ERROR /ticket: {e}")
        await interaction.followup.send(f"❌ Error /ticket: {e}", ephemeral=True)
@bot.tree.command(name="setup-ticket", description="Kirim panel ticket order (Owner only)")
async def setup_ticket(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.followup.send("Hanya Owner!", ephemeral=True); return
        embed1 = discord.Embed(title="Mipi Store - Order Robux 💗", description="ROBUX VIA USERNAME\nFast Process - Aman - Instan\n\nSyarat top up via username:\n>> SUDAH 18+\n>> SUDAH TERVERIFIKASI 2 LANGKAH", color=0xff69b4); embed1.set_image(url=WELCOME_URL)
        embed2 = build_pricelist_embed()
        await interaction.followup.send(embeds=[embed1, embed2], view=OrderView())
    except Exception as e:
        print(f"ERROR /setup-ticket: {e}")
        await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

# ===== EDIT PRICELIST DI DC - PUNYA KAMU ASLI =====
class EditHargaModal(discord.ui.Modal, title="Ubah Harga"):
    def __init__(self, robux_lama):
        super().__init__()
        self.robux_lama = robux_lama
        self.harga_input = discord.ui.TextInput(label=f"Harga Baru untuk {robux_lama} Robux", placeholder="Contoh: 80000", required=True)
        self.add_item(self.harga_input)
    async def on_submit(self, interaction: discord.Interaction):
        try: harga_baru = int(self.harga_input.value.replace(".", "").replace(",", "").replace("Rp", "").strip())
        except:
            await interaction.response.send_message("❌ Harga harus angka! Contoh: 80000", ephemeral=True); return
        data = load_pricelist(); data[self.robux_lama] = harga_baru; save_pricelist(data)
        await update_all_panels(interaction.guild)
        await interaction.response.send_message(f"✅ BERHASIL!\n{self.robux_lama} Robux ➡️ {format_rp(harga_baru)}\nTicket udah ke update otomatis!", ephemeral=True)
class TambahPaketModal(discord.ui.Modal, title="Tambah Paket Baru"):
    robux_input = discord.ui.TextInput(label="Jumlah Robux", placeholder="Contoh: 600", required=True)
    harga_input = discord.ui.TextInput(label="Harga", placeholder="Contoh: 90000", required=True)
    async def on_submit(self, interaction: discord.Interaction):
        try:
            rbx = int(self.robux_input.value.strip()); harga = int(self.harga_input.value.replace(".", "").replace("Rp", "").strip())
        except:
            await interaction.response.send_message("❌ Harus angka semua!", ephemeral=True); return
        data = load_pricelist(); data[rbx] = harga; save_pricelist(data); await update_all_panels(interaction.guild)
        await interaction.response.send_message(f"✅ Paket baru ditambah!\n{rbx} Robux = {format_rp(harga)}", ephemeral=True)
class PricelistEditView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None); data = load_pricelist(); options = []
        for rbx in sorted(data.keys()): options.append(discord.SelectOption(label=f"{rbx} Robux - {format_rp(data[rbx])}", value=str(rbx)))
        select = discord.ui.Select(placeholder="Pilih paket yang mau diubah...", options=options[:25], custom_id="pilih_paket_edit"); select.callback = self.pilih_paket; self.add_item(select)
    async def pilih_paket(self, interaction: discord.Interaction):
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("Hanya Owner!", ephemeral=True); return
        robux = int(interaction.data["values"][0]); await interaction.response.send_modal(EditHargaModal(robux))
    @discord.ui.button(label="➕ Tambah Paket Baru", style=discord.ButtonStyle.success, custom_id="tambah_paket_btn")
    async def tambah_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("Hanya Owner!", ephemeral=True); return
        await interaction.response.send_modal(TambahPaketModal())
    @discord.ui.button(label="👀 Lihat Pricelist", style=discord.ButtonStyle.primary, custom_id="lihat_pricelist_btn")
    async def lihat_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=build_pricelist_embed(), ephemeral=True)
@bot.tree.command(name="edit-pricelist", description="Edit pricelist langsung di DC - klik klik aja! (Owner)")
async def edit_pricelist(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.followup.send("Hanya Owner!", ephemeral=True); return
        embed = discord.Embed(title="✏️ EDIT PRICELIST - DI DC AJA!", description="Ga usah buka website!\n\n1. Pilih paket di dropdown bawah\n2. Ketik harga baru\n3. Beres! Ticket langsung ke update!\n\nPricelist sekarang:\n\n" + build_pricelist_text(), color=0xff69b4)
        await interaction.followup.send(embed=embed, view=PricelistEditView(), ephemeral=True)
    except Exception as e:
        print(f"ERROR /edit-pricelist: {e}")
        await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)
@bot.tree.command(name="set-harga", description="Ubah harga Robux cepat (Owner)")
async def set_harga(interaction: discord.Interaction, robux: int, harga_baru: int):
    await interaction.response.defer(ephemeral=True)
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.followup.send("Hanya Owner!", ephemeral=True); return
    data = load_pricelist(); harga_lama = data.get(robux, 0); data[robux] = harga_baru; save_pricelist(data); await update_all_panels(interaction.guild)
    await interaction.followup.send(f"✅ Harga berubah!\n{robux} Robux: {format_rp(harga_lama)} ➡️ {format_rp(harga_baru)}\nTicket udah otomatis ke update!")
@bot.tree.command(name="tambah-harga", description="Tambah paket baru (Owner)")
async def tambah_harga(interaction: discord.Interaction, robux: int, harga: int):
    await interaction.response.defer(ephemeral=True)
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.followup.send("Hanya Owner!", ephemeral=True); return
    data = load_pricelist(); data[robux] = harga; save_pricelist(data); await update_all_panels(interaction.guild)
    await interaction.followup.send(f"✅ Paket baru ditambah!\n{robux} = {format_rp(harga)}")
@bot.tree.command(name="hapus-harga", description="Hapus paket (Owner)")
async def hapus_harga(interaction: discord.Interaction, robux: int):
    await interaction.response.defer(ephemeral=True)
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.followup.send("Hanya Owner!", ephemeral=True); return
    data = load_pricelist()
    if robux not in data:
        await interaction.followup.send("Paket ga ketemu!", ephemeral=True); return
    del data[robux]; save_pricelist(data); await update_all_panels(interaction.guild)
    await interaction.followup.send(f"✅ {robux} Robux udah dihapus!")
@bot.tree.command(name="lihat-harga", description="Lihat pricelist sekarang")
async def lihat_harga(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send(embed=build_pricelist_embed(), ephemeral=True)

# ===== LEADERBOARD + TOP SULTAN - PUNYA KAMU ASLI + TAMBAH BULANAN DI PART 3 =====
@bot.tree.command(name="leaderboard", description="Lihat Top Buyer MIPI STORE bulan ini")
async def leaderboard(interaction: discord.Interaction):
    await interaction.response.defer()
    try: await interaction.followup.send(embed=build_top_sultan_embed())
    except Exception as e:
        print(f"ERROR leaderboard: {e}"); await interaction.followup.send(f"❌ Error leaderboard: {e}")
@bot.tree.command(name="top-sultan", description="Lihat Top Sultan MIPI STORE")
async def top_sultan_cmd(interaction: discord.Interaction):
    await interaction.response.defer()
    try: await interaction.followup.send(embed=build_top_sultan_embed())
    except Exception as e:
        print(f"ERROR top-sultan: {e}"); await interaction.followup.send(f"❌ Error top-sultan: {e}")
@bot.tree.command(name="setup-top-sultan", description="Bikin channel top-sultan auto-update (Owner)")
async def setup_top_sultan(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.followup.send("Hanya Owner!", ephemeral=True); return
    guild = interaction.guild; ch = get_top_sultan_channel(guild)
    if not ch: ch = await guild.create_text_channel("🏆┆・top-sultan")
    await ch.set_permissions(guild.default_role, view_channel=True, send_messages=False, add_reactions=False)
    await update_top_sultan(guild); await interaction.followup.send(f"✅ Channel Top Sultan auto-update udah jadi! {ch.mention}\nPapan bakal ke-update tiap 1 menit + tiap ada order dikonfirmasi!", ephemeral=True)
@bot.tree.command(name="saldo", description="Cek total belanja kamu di MIPI STORE")
async def saldo_slash(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    total_rp, total_robux, total_transaksi = get_total_belanja(interaction.user.id); harga_str = f"Rp {total_rp:,}".replace(",", "."); embed = discord.Embed(color=0xff1493); embed.description = "INFORMASI SALDO / TOTAL TRANSAKSI\n\nHalo " + interaction.user.mention + ",\n\nTotal Belanja: " + harga_str + "\nTotal Robux: " + str(total_robux) + " R$\nTotal Transaksi: " + str(total_transaksi) + "x\n\nMIPI STORE - CHECK SALDO"; embed.set_footer(text="Mipi Store - Rafi Store"); await interaction.followup.send(embed=embed, ephemeral=True)
@bot.command(name="saldo")
async def saldo_prefix(ctx):
    total_rp, total_robux, total_transaksi = get_total_belanja(ctx.author.id); harga_str = f"Rp {total_rp:,}".replace(",", "."); embed = discord.Embed(color=0xff1493); embed.description = "INFORMASI SALDO / TOTAL TRANSAKSI\n\nHalo " + ctx.author.mention + ",\n\nTotal Belanja: " + harga_str + "\nTotal Robux: " + str(total_robux) + " R$\nTotal Transaksi: " + str(total_transaksi) + "x"; await ctx.send(embed=embed)
@bot.tree.command(name="setup-saldo", description="Kirim panel cek saldo ke channel ini (Owner only)")
async def setup_saldo(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.followup.send("Hanya Owner!", ephemeral=True); return
    embed = discord.Embed(title="CEK SALDO - MIPI STORE", description="MAU TAU UDAH HABIS BERAPA DI MIPI STORE?\n\nPencet tombol CEK SALDO SAYA dibawah ini!\n\nNanti bakal muncul:\nTotal Belanja kamu\nTotal Robux yang udah dibeli\nTotal Transaksi kamu", color=0xff69b4); await interaction.followup.send(embed=embed, view=SaldoView())
@bot.tree.command(name="add-saldo", description="Tambah saldo manual ke buyer (Admin / Owner only)")
async def add_saldo(interaction: discord.Interaction, user: discord.User, robux: int):
    await interaction.response.defer(ephemeral=True)
    if not is_admin_or_owner(interaction.user, interaction.guild):
        await interaction.followup.send("Hanya Admin / Owner!", ephemeral=True); return
    if robux <= 0:
        await interaction.followup.send("Jumlah Robux harus lebih dari 0!", ephemeral=True); return
    harga = get_harga(robux); add_to_leaderboard(user.id, user.name, str(robux) + " Robux"); total_rp, total_robux, total_transaksi = get_total_belanja(user.id); embed = discord.Embed(color=0x57f287); embed.description = "Saldo " + user.mention + " ditambah!\n\n+" + str(robux) + " R$\n+" + format_rp(harga) + "\n\nTotal Transaksi Sekarang: " + str(total_transaksi) + "x\nTotal Robux Sekarang: " + str(total_robux) + " R$\nTotal Belanja Sekarang: " + format_rp(total_rp); await interaction.followup.send(embed=embed)
    try: await update_top_sultan(interaction.guild)
    except: pass
@bot.command(name="add-saldo")
async def add_saldo_prefix(ctx, user: discord.User, robux: int):
    if not is_admin_or_owner(ctx.author, ctx.guild): await ctx.send("Hanya Admin / Owner!"); return
    harga = get_harga(robux); add_to_leaderboard(user.id, user.name, str(robux) + " Robux"); await ctx.send("Saldo " + user.mention + " ditambah!\n+" + str(robux) + " R$\n+" + format_rp(harga))
    try: await update_top_sultan(ctx.guild)
    except: pass
@bot.tree.command(name="kurangi-saldo", description="Kurangi saldo buyer - GA BISA SAMPE MINUS! (Admin/Owner)")
async def kurangi_saldo(interaction: discord.Interaction, user: discord.User, robux: int, alasan: str = ""):
    await interaction.response.defer(ephemeral=True)
    if not is_admin_or_owner(interaction.user, interaction.guild):
        await interaction.followup.send("Hanya Admin / Owner!", ephemeral=True); return
    if robux <= 0:
        await interaction.followup.send("❌ Jumlah harus lebih dari 0!", ephemeral=True); return
    total_rp, total_robux, total_tx = get_total_belanja(user.id)
    if robux > total_robux:
        await interaction.followup.send(f"❌ **GAGAL! SALDO GA CUKUP!**\n\nSaldo {user.mention} sekarang: **{total_robux} R$**\nKamu mau kurangin: **{robux} R$**\nKurang: **{robux - total_robux} R$**\n\nSaldo gabisa minus! Max kurangin {total_robux} R$ aja!", ephemeral=True); return
    data = load_leaderboard(); sisa = robux
    for bulan in sorted(data.keys(), reverse=True):
        if str(user.id) in data[bulan] and sisa > 0:
            cur = data[bulan][str(user.id)]["total"]; potong = min(cur, sisa); data[bulan][str(user.id)]["total"] -= potong; data[bulan][str(user.id)]["total_rp"] -= get_harga(potong); sisa -= potong
    save_leaderboard(data); total_rp2, total_robux2, _ = get_total_belanja(user.id)
    await interaction.followup.send(f"✅ Saldo {user.mention} dikurangi **-{robux} R$**\nSisa saldo: **{total_robux2} R$**\nAlasan: {alasan if alasan else '-'}")
    try: await update_top_sultan(interaction.guild)
    except: pass
    try:
        ch = get_history_channel(interaction.guild)
        if ch: await ch.send(f"⚠️ **LOG SALDO:** Admin {interaction.user.mention} ngurangin saldo {user.mention} -{robux} R$ | Sisa: {total_robux2} R$ | Alasan: {alasan}")
    except: pass
@bot.tree.command(name="pending-saldo", description="Lihat order yang belum dikonfirmasi masuk saldo (Admin)")
async def pending_saldo_cmd(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if not is_admin_or_owner(interaction.user, interaction.guild):
        await interaction.followup.send("Hanya Admin / Owner!", ephemeral=True); return
    pend = load_pending()
    if not pend:
        await interaction.followup.send("✅ Ga ada pending! Semua order udah dikonfirmasi!", ephemeral=True); return
    txt = "**⏳ PENDING SALDO - BELUM MASUK LEADERBOARD:**\n\n"
    for oid, d in pend.items(): txt += f"• **{oid}** | <@{d['user_id']}> | {d['paket']} | {d['robux']} R$ | Ticket #{d['ticket_number']}\n"
    txt += "\nPencet ✅ di channel history-order buat konfirmasi!"; await interaction.followup.send(txt, ephemeral=True)
@bot.tree.command(name="konfirmasi-saldo", description="Konfirmasi manual order masuk saldo (Admin)")
async def konfirmasi_saldo_cmd(interaction: discord.Interaction, order_id: str):
    await interaction.response.defer(ephemeral=True)
    if not is_admin_or_owner(interaction.user, interaction.guild):
        await interaction.followup.send("Hanya Admin / Owner!", ephemeral=True); return
    pend = load_pending(); order_id = order_id.upper().strip()
    if order_id not in pend:
        await interaction.followup.send(f"❌ {order_id} ga ketemu! Cek `/pending-saldo`", ephemeral=True); return
    d = pend[order_id]; add_to_leaderboard(int(d["user_id"]), d["username"], d["paket"]); del pend[order_id]; save_pending(pend); await interaction.followup.send(f"✅ {order_id} dikonfirmasi! +{d['robux']} R$ masuk ke <@{d['user_id']}>!")
    try: await update_top_sultan(interaction.guild)
    except: pass

# ===== PROMO =====
@bot.tree.command(name="buat-promo", description="Buat kode promo diskon (Owner only)")
async def buat_promo(interaction: discord.Interaction, kode: str, diskon: int, tipe: str = "nominal", max_pakai: int = 10):
    await interaction.response.defer(ephemeral=True)
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.followup.send("Hanya Owner!", ephemeral=True); return
    kode = kode.upper().strip(); data = load_promo(); data[kode] = {"diskon": diskon, "tipe": tipe, "max": max_pakai, "dipakai": 0, "dibuat_oleh": interaction.user.name}; save_promo(data); desc = "Diskon " + str(diskon) + "%" if tipe == "persen" else "Diskon " + format_rp(diskon); embed = discord.Embed(title="KODE PROMO BARU!", description="Kode: " + kode + "\n" + desc + "\nMax Pakai: " + str(max_pakai) + " orang\nMinimal Belanja: 500 Robux", color=0x57f287); await interaction.followup.send(embed=embed)
@bot.tree.command(name="list-promo", description="Lihat semua kode promo yang aktif")
async def list_promo(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    data = load_promo()
    if not data:
        await interaction.followup.send("Belum ada kode promo Wal! Bikin dulu pake /buat-promo", ephemeral=True); return
    desc = "LIST KODE PROMO MIPI STORE\n\n"
    for kode, p in data.items():
        sisa = p.get("max", 999) - p.get("dipakai", 0); d = str(p["diskon"]) + "%" if p["tipe"] == "persen" else format_rp(p["diskon"]); status = "AKTIF" if sisa > 0 else "HABIS"; desc += kode + " - Diskon " + d + " - Sisa " + str(sisa) + "/" + str(p.get("max", 999)) + " - Min 500 R$ - " + status + "\n"
    await interaction.followup.send(embed=discord.Embed(description=desc, color=0xff69b4), ephemeral=True)
@bot.tree.command(name="cek-promo", description="Cek apakah kode promo masih bisa dipakai")
async def cek_promo_cmd(interaction: discord.Interaction, kode: str, paket: str = "500"):
    await interaction.response.defer(ephemeral=True)
    kode_up = kode.upper().strip(); data = load_promo()
    if kode_up not in data:
        await interaction.followup.send("Kode " + kode_up + " tidak ditemukan!", ephemeral=True); return
    p = data[kode_up]; sisa = p.get("max", 999) - p.get("dipakai", 0); m = re.search(r'(\d+)', str(paket).replace('.', '')); jumlah = int(m.group(1)) if m else 500; harga_awal = get_harga(jumlah); harga_baru, diskon, err = cek_promo(kode_up, harga_awal, jumlah)
    if err:
        await interaction.followup.send(err, ephemeral=True); return
    await interaction.followup.send("Kode " + kode_up + " MASIH AKTIF!\n\nPaket: " + str(jumlah) + " Robux\nHarga Normal: " + format_rp(harga_awal) + "\nDiskon: " + format_rp(diskon) + "\nHarga Setelah Diskon: " + format_rp(harga_baru) + "\nSisa: " + str(sisa) + " orang\nMinimal: 500 Robux", ephemeral=True)
@bot.tree.command(name="hapus-promo", description="Hapus kode promo (Owner only)")
async def hapus_promo(interaction: discord.Interaction, kode: str):
    await interaction.response.defer(ephemeral=True)
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.followup.send("Hanya Owner!", ephemeral=True); return
    kode = kode.upper().strip(); data = load_promo()
    if kode not in data:
        await interaction.followup.send("Kode " + kode + " tidak ditemukan!", ephemeral=True); return
    del data[kode]; save_promo(data); await interaction.followup.send("Kode promo " + kode + " sudah dihapus!", ephemeral=True)

# ===== GIVEAWAY =====
@bot.tree.command(name="giveaway", description="Buat giveaway otomatis (Owner only)")
async def giveaway_create(interaction: discord.Interaction, hadiah: str, durasi_menit: int, pemenang: int = 1):
    await interaction.response.defer()
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.followup.send("Hanya Owner yang bisa bikin giveaway!", ephemeral=True); return
    if durasi_menit < 1:
        await interaction.followup.send("Durasi minimal 1 menit Wal!", ephemeral=True); return
    giveaway_id = str(interaction.channel.id) + "-" + str(interaction.id); end_time = int(time.time() + durasi_menit * 60); giveaway_data[giveaway_id] = {"hadiah": hadiah, "host_mention": interaction.user.mention, "host_id": interaction.user.id, "end_timestamp": end_time, "pemenang": pemenang, "peserta": [], "ended": False, "channel_id": interaction.channel.id}
    embed = discord.Embed(title="GIVEAWAY MIPI STORE!", description="Hadiah: " + hadiah + "\n\nHost: " + interaction.user.mention + "\nBerakhir: <t:" + str(end_time) + ":R>\nPemenang: " + str(pemenang) + " orang\nPeserta: 0 orang\n\nPencet tombol JOIN GIVEAWAY dibawah buat ikutan!\n\nGood luck!", color=0xff69b4); msg = await interaction.followup.send(embed=embed, view=GiveawayView(giveaway_id)); giveaway_data[giveaway_id]["message_id"] = msg.id; await asyncio.sleep(durasi_menit * 60); await end_giveaway(interaction.guild, interaction.channel.id, msg.id, giveaway_id)
@bot.tree.command(name="giveaway-end", description="Akhiri giveaway lebih cepat (Owner only)")
async def giveaway_end(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.followup.send("Hanya Owner!", ephemeral=True); return
    found = None
    for gid, data in giveaway_data.items():
        if data["channel_id"] == interaction.channel.id and not data["ended"]: found = (gid, data); break
    if not found:
        await interaction.followup.send("Gak ada giveaway yang lagi jalan di channel ini!", ephemeral=True); return
    gid, data = found; await interaction.followup.send("Giveaway diakhiri lebih cepat! Mengundi pemenang...", ephemeral=True); await end_giveaway(interaction.guild, interaction.channel.id, data.get("message_id"), gid)
@bot.tree.command(name="market-rules", description="Kirim aturan market")
async def market_rules(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.followup.send("Hanya Owner!", ephemeral=True); return
    embed = discord.Embed(title="Stickied Message:", description="DILARANG MENJUAL PRODUK YANG KAMI JUAL SEPERTI ROBUX DAN LIMITED ITEM", color=0xff0000); msg = await interaction.channel.send(embed=embed)
    try: await msg.pin()
    except: pass
    await interaction.followup.send("Aturan market sudah di-pin!", ephemeral=True)
@bot.command(name="market-rules")
async def market_rules_prefix(ctx):
    if ctx.author.id != ctx.guild.owner_id: await ctx.send("Hanya Owner!"); return
    embed = discord.Embed(title="Stickied Message:", description="DILARANG MENJUAL PRODUK YANG KAMI JUAL SEPERTI ROBUX DAN LIMITED ITEM", color=0xff0000); msg = await ctx.send(embed=embed)
    try: await msg.pin()
    except: pass
    await ctx.send("Aturan market sudah di-pin!")
@bot.tree.command(name="ping", description="Cek bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send(f"Pong! MIPI STORE online Wal! {round(bot.latency*1000)}ms", ephemeral=True)
@bot.command(name="ping")
async def ping_prefix(ctx): await ctx.send(f"Pong! MIPI STORE online Wal! {round(bot.latency*1000)}ms")

# ===== CHECK AVATAR + CEK RBX =====
@bot.tree.command(name="checkavatar", description="Mengecek detail profil dan avatar akun Roblox dengan username")
async def checkavatar(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    try:
        headers = {"User-Agent": "Mozilla/5.0 MIPI-STORE-Bot"}
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.post("https://users.roproxy.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": True}) as r:
                data = await r.json()
                if not data.get("data"): await interaction.followup.send("Username " + username + " tidak ditemukan!"); return
                user = data["data"][0]; user_id = user["id"]; display = user.get("displayName", username); uname = user.get("name", username)
            async with s.get(f"https://users.roproxy.com/v1/users/{user_id}") as r:
                info = await r.json(); created = info.get("created", "")
                try: tgl = datetime.fromisoformat(created.replace("Z", "+00:00")).strftime("%d %B %Y")
                except: tgl = created
            async with s.get(f"https://avatar.roproxy.com/v1/users/{user_id}/avatar") as r:
                av = await r.json(); tipe = av.get("playerAvatarType", "R15"); assets = av.get("assets", []
