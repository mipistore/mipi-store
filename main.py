# PART 1 - MIPI STORE v5.0
import discord
from discord.ext import commands, tasks
import os, time, io, html, re, asyncio, json, random, aiohttp
from datetime import datetime, timedelta, date
from collections import defaultdict, Counter

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
giveaway_data = {}
daily_stats = {"orders": 0, "revenue": 0, "date": str(date.today())}
reminder_sent = set()

STORE_STATUS = "open"
STORE_STATUS_MSG = ""
OPEN_CLOSE_CHANNEL_ID = 1569135504262299689

# ===== PRICELIST =====
PRICELIST_FILE = "pricelist.json"
DEFAULT_PRICELIST = {100: 16000, 200: 32000, 300: 48000, 400: 64000, 500: 75000, 1000: 150000, 2000: 300000, 3000: 450000, 4000: 600000, 5000: 750000}

def load_pricelist():
    try:
        with open(PRICELIST_FILE, "r") as f:
            return {int(k): int(v) for k, v in json.load(f).items()}
    except:
        return DEFAULT_PRICELIST.copy()

def save_pricelist(data):
    with open(PRICELIST_FILE, "w") as f:
        json.dump({str(k): v for k, v in data.items()}, f, indent=2)

def get_harga(robux):
    data = load_pricelist()
    if robux in data: return data[robux]
    if robux >= 10000: return int(robux * 145)
    if robux >= 5000: return int(robux * 148)
    return int(robux * 150)

def format_rp(n): return f"Rp {n:,}".replace(",", ".")
def parse_paket(t):
    m = re.search(r'(\d+)', str(t).replace('.', '').replace(',', ''))
    return int(m.group(1)) if m else 500

def hitung_harga(paket_text):
    jumlah = parse_paket(paket_text)
    return str(jumlah), format_rp(get_harga(jumlah))

PRICELIST = load_pricelist()

# ===== LEADERBOARD / TIER =====
LEADERBOARD_FILE = "leaderboard.json"
def load_leaderboard():
    try:
        with open(LEADERBOARD_FILE, "r") as f: return json.load(f)
    except: return {}
def save_leaderboard(d):
    with open(LEADERBOARD_FILE, "w") as f: json.dump(d, f, indent=2)

def add_to_leaderboard(user_id, username, paket_text):
    jumlah = parse_paket(paket_text)
    harga = get_harga(jumlah)
    data = load_leaderboard()
    bulan = datetime.now().strftime("%Y-%m")
    if bulan not in data: data[bulan] = {}
    uid = str(user_id)
    if uid not in data[bulan]:
        data[bulan][uid] = {"username": username, "total": 0, "transaksi": 0, "total_rp": 0}
    data[bulan][uid]["username"] = username
    data[bulan][uid]["total"] += jumlah
    data[bulan][uid]["transaksi"] += 1
    data[bulan][uid]["total_rp"] += harga
    save_leaderboard(data)
    daily_stats["orders"] += 1
    daily_stats["revenue"] += harga

def get_total_belanja(user_id):
    data = load_leaderboard()
    tr = tro = tt = 0
    for bulan, users in data.items():
        uid = str(user_id)
        if uid in users:
            tr += users[uid].get("total_rp", 0)
            tro += users[uid].get("total", 0)
            tt += users[uid].get("transaksi", 0)
    return tr, tro, tt

def get_member_tier(user_id):
    tr, tro, tt = get_total_belanja(user_id)
    if tr >= 5000000: return "DIAMOND", "💎", 15, "Diskon 15% + Prioritas"
    if tr >= 2000000: return "GOLD", "🥇", 10, "Diskon 10% + Prioritas"
    if tr >= 1000000: return "SILVER", "🥈", 7, "Diskon 7%"
    if tr >= 500000: return "BRONZE", "🥉", 5, "Diskon 5%"
    return "MEMBER", "🌸", 0, "Belanja 500k buat naik ke Bronze!"

def get_tier_discount(user_id):
    return get_member_tier(user_id)[2]

# ===== PROMO =====
PROMO_FILE = "promo.json"
def load_promo():
    try:
        with open(PROMO_FILE, "r") as f: return json.load(f)
    except: return {}
def save_promo(d):
    with open(PROMO_FILE, "w") as f: json.dump(d, f, indent=2)

def cek_promo(kode, harga_awal, jumlah_robux=0):
    if not kode or not str(kode).strip(): return harga_awal, 0, None
    kode = str(kode).upper().strip()
    data = load_promo()
    if kode not in data: return harga_awal, 0, "❌ Kode promo tidak ditemukan!"
    p = data[kode]
    if jumlah_robux < 500: return harga_awal, 0, "❌ Minimal 500 Robux!"
    if p.get("dipakai", 0) >= p.get("max", 999): return harga_awal, 0, "❌ Kode promo habis!"
    diskon = int(harga_awal * p["diskon"] / 100) if p["tipe"] == "persen" else int(p["diskon"])
    return max(0, harga_awal - diskon), diskon, None

# ===== STOK =====
STOK_FILE = "stok.json"
def load_stok():
    try:
        with open(STOK_FILE, "r") as f: return json.load(f)
    except: return {"total_stok": 50000, "terjual_hari_ini": 0, "terjual_total": 0, "last_restock": datetime.now().isoformat(), "history": []}
def save_stok(d):
    with open(STOK_FILE, "w") as f: json.dump(d, f, indent=2)
def cek_stok_cukup(jumlah):
    d = load_stok(); return d["total_stok"] >= jumlah, d["total_stok"]
def kurangi_stok(jumlah, user_id, paket):
    d = load_stok()
    if d["total_stok"] < jumlah: return False, d["total_stok"]
    d["total_stok"] -= jumlah; d["terjual_hari_ini"] += jumlah; d["terjual_total"] += jumlah
    d["history"].append({"user_id": user_id, "paket": paket, "jumlah": jumlah, "waktu": datetime.now().isoformat(), "sisa": d["total_stok"]})
    save_stok(d); return True, d["total_stok"]
def tambah_stok(jumlah, admin_name, keterangan="Restock"):
    d = load_stok(); d["total_stok"] += jumlah; d["last_restock"] = datetime.now().isoformat()
    d["history"].append({"admin": admin_name, "aksi": "restock", "jumlah": jumlah, "keterangan": keterangan, "waktu": datetime.now().isoformat(), "sisa": d["total_stok"]})
    save_stok(d); return d["total_stok"]
def is_stok_menipis(): return load_stok()["total_stok"] < 5000
def is_stok_kritis(): return load_stok()["total_stok"] < 1000

# ===== INVOICE =====
INVOICE_FILE = "invoice.json"
invoice_counter = 1000
def load_invoice():
    try:
        with open(INVOICE_FILE, "r") as f: return json.load(f)
    except: return {}
def save_invoice(d):
    with open(INVOICE_FILE, "w") as f: json.dump(d, f, indent=2)
def buat_invoice(user_id, username, paket, jumlah_robux, harga_awal, harga_akhir, diskon, kode_promo, pembayaran, roblox_username, nickname):
    global invoice_counter
    invoice_counter += 1
    inv_id = f"MIPI-{invoice_counter}-{random.randint(100,999)}"
    data = load_invoice()
    data[inv_id] = {"id": inv_id, "user_id": user_id, "username": username, "paket": paket, "jumlah_robux": jumlah_robux, "harga_awal": harga_awal, "harga_akhir": harga_akhir, "diskon": diskon, "kode_promo": kode_promo, "pembayaran": pembayaran, "roblox_username": roblox_username, "nickname": nickname, "status": "PENDING", "created_at": datetime.now().isoformat(), "paid_at": None, "done_at": None, "admin": None}
    save_invoice(data); return inv_id
def update_invoice_status(inv_id, status, admin_name=None):
    data = load_invoice()
    if inv_id not in data: return False
    data[inv_id]["status"] = status
    if status == "PAID": data[inv_id]["paid_at"] = datetime.now().isoformat()
    if status == "DONE": data[inv_id]["done_at"] = datetime.now().isoformat()
    if admin_name: data[inv_id]["admin"] = admin_name
    save_invoice(data); return True
def cari_invoice(inv_id):
    return load_invoice().get(inv_id.upper(), None)
def invoice_user(user_id):
    data = load_invoice()
    hasil = [v for v in data.values() if str(v["user_id"]) == str(user_id)]
    hasil.sort(key=lambda x: x["created_at"], reverse=True)
    return hasil[:10]

# ===== REFERRAL =====
REFERRAL_FILE = "referral.json"
def load_referral():
    try:
        with open(REFERRAL_FILE, "r") as f: return json.load(f)
    except: return {}
def save_referral(d):
    with open(REFERRAL_FILE, "w") as f: json.dump(d, f, indent=2)
def get_referral_code(user_id):
    data = load_referral(); uid = str(user_id)
    if uid not in data:
        code = f"MIPI-{uid[-4:]}-{random.randint(100,999)}"
        data[uid] = {"code": code, "invite_count": 0, "total_bonus": 0, "invited_users": [], "claimed": 0}
        save_referral(data)
    return data[uid]["code"]
def pakai_referral(code, new_user_id, new_username):
    data = load_referral()
    for uid, info in data.items():
        if info["code"] == code.upper() and uid != str(new_user_id):
            if str(new_user_id) in info["invited_users"]: return False, "Udah pernah pake kode ini!"
            info["invited_users"].append(str(new_user_id)); info["invite_count"] += 1; info["total_bonus"] += 5000
            save_referral(data); return True, "Berhasil!"
    return False, "Kode referral ga ditemukan!"
def klaim_bonus_referral(user_id):
    data = load_referral(); uid = str(user_id)
    if uid not in data: return 0, "Belum punya referral!"
    belum = data[uid]["total_bonus"] - data[uid]["claimed"]
    if belum <= 0: return 0, "Ga ada bonus! Ajak temen dulu!"
    data[uid]["claimed"] += belum; save_referral(data); return belum, "Berhasil!"

# ===== BLACKLIST & CATATAN =====
BLACKLIST_FILE = "blacklist.json"
def load_blacklist():
    try:
        with open(BLACKLIST_FILE, "r") as f: return json.load(f)
    except: return {}
def save_blacklist(d):
    with open(BLACKLIST_FILE, "w") as f: json.dump(d, f, indent=2)
def is_blacklisted(user_id): return str(user_id) in load_blacklist()
def get_blacklist_reason(user_id):
    info = load_blacklist().get(str(user_id))
    return (info.get("alasan",""), info.get("oleh",""), info.get("waktu","")) if info else (None,None,None)

CATATAN_FILE = "catatan.json"
def load_catatan():
    try:
        with open(CATATAN_FILE, "r") as f: return json.load(f)
    except: return {}
def save_catatan(d):
    with open(CATATAN_FILE, "w") as f: json.dump(d, f, indent=2)
def tambah_catatan(user_id, username, catatan, oleh):
    data = load_catatan(); uid = str(user_id)
    if uid not in data: data[uid] = {"username": username, "list": []}
    data[uid]["list"].append({"catatan": catatan, "oleh": oleh, "waktu": datetime.now().isoformat()})
    data[uid]["username"] = username; save_catatan(data)
def lihat_catatan(user_id): return load_catatan().get(str(user_id), {"username": "", "list": []})

# ===== PRE-ORDER =====
PREORDER_FILE = "preorder.json"
def load_preorder():
    try:
        with open(PREORDER_FILE, "r") as f: return json.load(f)
    except: return []
def save_preorder(d):
    with open(PREORDER_FILE, "w") as f: json.dump(d, f, indent=2)
def tambah_preorder(user_id, username, paket, roblox_username, nickname, jumlah):
    data = load_preorder()
    data.append({"user_id": user_id, "username": username, "paket": paket, "roblox_username": roblox_username, "nickname": nickname, "jumlah": jumlah, "waktu": datetime.now().isoformat(), "status": "MENUNGGU RESTOCK"})
    save_preorder(data); return len(data)

# ===== VOUCHER HARIAN =====
VOUCHER_FILE = "voucher_harian.json"
def load_voucher_harian():
    try:
        with open(VOUCHER_FILE, "r") as f: return json.load(f)
    except: return {}
def save_voucher_harian(d):
    with open(VOUCHER_FILE, "w") as f: json.dump(d, f, indent=2)
def klaim_voucher_harian(user_id):
    data = load_voucher_harian(); today = str(date.today()); uid = str(user_id)
    if uid in data and data[uid].get("tanggal") == today: return False, "Udah klaim hari ini!"
    hadiah = random.choice([("Diskon 5%", "MIPIHARI5", 5, "persen"), ("Diskon 10%", "MIPIHARI10", 10, "persen"), ("Potongan Rp 5000", "MIPIHEMAT5K", 5000, "nominal"), ("Potongan Rp 10000", "MIPIHEMAT10K", 10000, "nominal")])
    data[uid] = {"tanggal": today, "hadiah": hadiah[0], "kode": hadiah[1]}
    save_voucher_harian(data)
    promo = load_promo()
    if hadiah[1] not in promo:
        promo[hadiah[1]] = {"diskon": hadiah[2], "tipe": hadiah[3], "max": 1, "dipakai": 0, "dibuat_oleh": "VOUCHER HARIAN"}
        save_promo(promo)
    return True, hadiah
    # ===== PART 2 - GIVEAWAY + FILTER + HELPER + TICKET =====

# ===== GIVEAWAY =====
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
                embed = discord.Embed(title="🎁 GIVEAWAY BERAKHIR - GAK ADA PESERTA 😭", description=f"Hadiah: **{data['hadiah']}**", color=0xff0000)
                await msg.edit(embed=embed, view=None)
            await channel.send("😭 Giveaway berakhir tapi gak ada yang join!")
            return
        winners = random.sample(data["peserta"], min(data["pemenang"], len(data["peserta"])))
        winner_mentions = ", ".join([f"<@{w}>" for w in winners])
        if msg:
            embed = discord.Embed(title="🎉 GIVEAWAY BERAKHIR!", description=f"🎁 **Hadiah:** {data['hadiah']}\n\n🏆 **Pemenang:**\n{winner_mentions}\n\n👥 **Total Peserta:** {len(data['peserta'])} orang", color=0x57f287)
            await msg.edit(embed=embed, view=None)
        await channel.send(f"🎉 **GIVEAWAY BERAKHIR!**\n\n🎁 Hadiah: **{data['hadiah']}**\n🏆 Pemenang: {winner_mentions}\n\nSelamat ya! DM {data['host_mention']} buat klaim!")
    except Exception as e:
        print(f"Gagal end giveaway: {e}")

class GiveawayView(discord.ui.View):
    def __init__(self, giveaway_id):
        super().__init__(timeout=None)
        self.giveaway_id = giveaway_id
    @discord.ui.button(label="🎉 JOIN GIVEAWAY", style=discord.ButtonStyle.success, custom_id="join_giveaway")
    async def join_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = giveaway_data.get(self.giveaway_id)
        if not data or data["ended"]:
            await interaction.response.send_message("❌ Giveaway sudah berakhir!", ephemeral=True); return
        if interaction.user.id in data["peserta"]:
            await interaction.response.send_message("⚠️ Kamu udah join!", ephemeral=True); return
        if is_blacklisted(interaction.user.id):
            await interaction.response.send_message("❌ Kamu di-blacklist!", ephemeral=True); return
        data["peserta"].append(interaction.user.id)
        try:
            embed = interaction.message.embeds[0]
            embed.description = f"🎁 **Hadiah:** {data['hadiah']}\n\n👑 **Host:** {data['host_mention']}\n⏰ **Berakhir:** <t:{data['end_timestamp']}:R>\n🏆 **Pemenang:** {data['pemenang']} orang\n👥 **Peserta:** {len(data['peserta'])} orang"
            await interaction.message.edit(embed=embed, view=self)
        except: pass
        await interaction.response.send_message(f"✅ Berhasil join! Peserta: {len(data['peserta'])}", ephemeral=True)

# ===== FILTER JUALAN LIAR =====
BANNED_WORDS = ["wts robux", "jual robux", "sell robux", "jual rb", "wts rb", "jual limited", "wts limited", "sell limited", "jual robux murah", "robux murah", "top up robux", "jual akun robux", "wtt robux", "wtb robux", "jual robux via"]
ALLOWED_IF_HAS = ["akun pribadi", "akun roblox"]
def is_banned_selling(text):
    low = text.lower()
    if any(a in low for a in ALLOWED_IF_HAS) and "robux" not in low and "limited" not in low:
        return False
    return any(w in low for w in BANNED_WORDS)

# ===== HELPER CHANNEL =====
def get_status_channel(guild):
    for ch in guild.text_channels:
        if "order-status" in ch.name.lower(): return ch
    return None
def get_history_channel(guild):
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
    for m in messages:
        rows += f"""<div style="margin:6px 0;padding:8px;background:#2b2d31;border-radius:8px;"><b style="color:#fff;">{html.escape(str(m['author']))}</b> <span style="color:#949ba4;font-size:12px;">{m['time']}</span><br><span style="color:#dbdee1;">{html.escape(m['content'] or '(gambar / embed)')}</span></div>"""
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Ticket #{number}</title></head><body style="background:#1e1f22;font-family:sans-serif;padding:20px;"><h2 style="color:white;">MIPI STORE - Ticket #{number}</h2><p style="color:#949ba4;">{html.escape(username)} | {html.escape(paket)} | {duration} menit | {len(messages)} pesan</p>{rows}</body></html>"""

async def send_status_update(guild, number, username, user_id, paket, status_text, color):
    ch = get_status_channel(guild)
    if not ch: return
    embed = discord.Embed(title=f"📦 Order Status - Ticket #{number}", description=f"**Customer:** <@{user_id}> ({username})\n**Paket:** {paket}\n**Status:** {status_text}", color=color)
    await ch.send(embed=embed)

async def send_history_log(guild, channel, data, admin_user):
    ch = get_history_channel(guild)
    if not ch: return
    number = data["number"]; user_id = data["user_id"]
    roblox_user = data.get("roblox_username", "-")
    nickname = data.get("nickname", "-")
    paket = data.get("paket", "500 Robux")
    pembayaran = data.get("pembayaran", "QRIS")
    jumlah, harga = hitung_harga(paket)
    ticket_name = channel.name if channel else f"ticket-{number}"
    embed = discord.Embed(color=0x2b2d31)
    embed.description = f"🔒 Ticket Log\n\n🎫 Ticket\n{ticket_name}\n🔒 Action\nClosed\n🎀 Member\n<@{user_id}>\n🏷️ Nickname Roblox\n{nickname}\n👤 Username Roblox\n{roblox_user}\n✨ Jumlah Robux\n{jumlah}\n💰 Total Harga\n{harga}\n💳 Payment\n{pembayaran}\n✅ Admin\n{admin_user.mention if admin_user else 'Auto-Close'}"
    embed.set_image(url=THANKYOU_URL)
    await ch.send(embed=embed)

async def send_vouch(guild, user, paket, stars, komentar, ticket_number=0, ticket_name=""):
    ch = get_vouch_channel(guild)
    if not ch: return
    jumlah, harga = hitung_harga(paket)
    star_str = "⭐" * stars
    seller = guild.owner.mention if guild.owner else "MIPI STORE"
    if not ticket_name: ticket_name = f"robux-via-username-{ticket_number}-{user.name}"
    embed = discord.Embed(color=0x2b2d31)
    embed.description = f"✅ VOUCH RECEIVED ✅\n\n**Ticket ID**\n{ticket_number}\n**Nominal**\n{harga}\n**Seller**\n{seller}\n**Buyer**\n<@{user.id}>\n**Rating**\n{star_str}\n**Komentar**\n{komentar} 💗\n**Source**\n{ticket_name}"
    embed.set_thumbnail(url=user.display_avatar.url)
    msg = await ch.send(embed=embed)
    try:
        thread = await msg.create_thread(name=f"Vouch - {user.name} | Ticket #{ticket_number}", auto_archive_duration=1440)
        await thread.send(f"💗 **Vouch dari {user.mention}**\n\n📦 **Paket:** {paket} ({harga})\n⭐ **Rating:** {star_str}\n💬 **Komentar:** {komentar}")
    except: pass

# ===== AUTO CLOSE + REMINDER =====
async def do_auto_close(guild, channel, data, reason="auto-closed", admin_user=None):
    number = data["number"]; user_id = data["user_id"]; paket = data.get("paket", "ORDER ROBUX")
    created = data["created_at"]; duration = int((time.time() - created)//60)
    if duration < 1: duration = 1
    user_last_ticket[user_id] = {"number": number, "paket": paket, "ticket_name": channel.name if channel else "", "seller_id": guild.owner_id}
    try: await send_history_log(guild, channel, data, admin_user)
    except: pass
    messages = []
    try:
        async for m in channel.history(limit=200, oldest_first=True):
            messages.append({"author": str(m.author), "time": m.created_at.strftime("%H:%M"), "content": m.content})
    except: pass
    status_ch = get_status_channel(guild)
    if status_ch:
        embed1 = discord.Embed(title="Ticket Auto-Closed", description=f"**#{number} {reason}**", color=0xfee75c)
        await status_ch.send(embed=embed1)
        html_text = make_html_transcript(number, messages, data.get("username","User"), paket, duration)
        file = discord.File(io.BytesIO(html_text.encode()), filename=f"ticket-{number}-transcript.html")
        embed2 = discord.Embed(title="Transcript", description=f"Ticket #{number} - {len(messages)} pesan - {duration} menit", color=0x5865f2)
        await status_ch.send(embed=embed2, file=file)
    try:
        user = await bot.fetch_user(user_id)
        embed = discord.Embed(title="Rate Your Experience", description=f"Hi {user.name}! Ticket kamu selesai.\n\n**Ticket #{number}**\n**Durasi:** {duration} menit\n**Closed by:** {admin_user.name if admin_user else 'MIPI STORE'}", color=0x2b2d31)
        await user.send(embed=embed, view=RatingView(number))
    except: pass
    try: add_to_leaderboard(user_id, data.get("username", "User"), paket)
    except: pass
    try:
        jumlah = parse_paket(paket)
        kurangi_stok(jumlah, user_id, paket)
    except: pass
    if channel.id in ticket_data: del ticket_data[channel.id]
    try: await channel.delete()
    except: pass

@tasks.loop(minutes=1)
async def check_inactive():
    now = time.time()
    for channel_id, data in list(ticket_data.items()):
        last = data.get("last_activity", data["created_at"])
        if now - last > 5*60 and channel_id not in reminder_sent:
            ch = bot.get_channel(channel_id)
            if ch:
                try:
                    await ch.send(f"<@{data['user_id']}> ⏰ **Reminder:** Ticket belum ada aktivitas 5 menit! Kirim bukti bayar ya biar cepet diproses! 💗")
                    reminder_sent.add(channel_id)
                except: pass
        if now - last > 15*60:
            ch = bot.get_channel(channel_id)
            if not ch: del ticket_data[channel_id]; continue
            if channel_id in reminder_sent: reminder_sent.remove(channel_id)
            await do_auto_close(ch.guild, ch, data)

@tasks.loop(minutes=5)
async def cek_stok_alert():
    if is_stok_kritis():
        for g in bot.guilds:
            owner = g.owner
            if owner:
                try: await owner.send(f"🚨 **STOK KRITIS!** Tinggal {load_stok()['total_stok']:,} R$! Segera restock! `/tambah-stok`")
                except: pass

# ===== RATING =====
class RatingView(discord.ui.View):
    def __init__(self, ticket_number):
        super().__init__(timeout=None); self.ticket_number = ticket_number
    async def send_thanks(self, interaction, stars):
        user_ratings[interaction.user.id] = stars
        star_str = "⭐" * stars
        embed = discord.Embed(title="Terima Kasih! 💗", description=f"Kamu memberi rating **{star_str} ({stars}/5)**\n\nPencet Add Comment dibawah biar vouch kamu muncul di #⭐┆・vouch!", color=0xff69b4)
        embed.set_image(url=THANKYOU_URL)
        await interaction.response.edit_message(embed=embed, view=self)
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
    async def comment(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CommentModal(ticket_number=self.ticket_number))
    @discord.ui.button(label="❌ No Thanks", style=discord.ButtonStyle.secondary, custom_id="no_thanks", row=1)
    async def no_thanks(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Oke! Makasih udah order di MIPI STORE 💗", embed=None, view=None)

class CommentModal(discord.ui.Modal, title="Komentar / Testimoni"):
    def __init__(self, ticket_number):
        super().__init__(); self.ticket_number = ticket_number
    komentar = discord.ui.TextInput(label="Komentar kamu", placeholder="satset poll", style=discord.TextStyle.paragraph, required=True)
    async def on_submit(self, interaction: discord.Interaction):
        stars = user_ratings.get(interaction.user.id, 5)
        last = user_last_ticket.get(interaction.user.id, {})
        paket = last.get("paket", "500 Robux")
        ticket_name = last.get("ticket_name", f"ticket-{self.ticket_number}")
        try:
            for g in bot.guilds:
                if get_vouch_channel(g):
                    await send_vouch(g, interaction.user, paket, stars, self.komentar.value, ticket_number=self.ticket_number, ticket_name=ticket_name)
                    break
        except: pass
        await interaction.response.send_message(f"Makasih! 💗\n> {self.komentar.value}\n\nVouch kamu udah muncul di vouch! Rating: {'⭐'*stars}", ephemeral=True)

def is_admin_or_owner(user, guild):
    if user.id == guild.owner_id: return True
    if user.guild_permissions.administrator: return True
    role_names = [r.name.lower() for r in user.roles]
    return any(x in role_names for x in ["admin", "owner", "staff", "moderator", "adm"])

# ===== VIEWS =====
class StatusView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="⏳ Menunggu Pembayaran", style=discord.ButtonStyle.secondary, custom_id="status_waiting")
    async def waiting(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not is_admin_or_owner(interaction.user, interaction.guild):
            await interaction.followup.send("❌ Hanya Admin!", ephemeral=True); return
        data = ticket_data.get(interaction.channel.id, {})
        if data: data["last_activity"] = time.time()
        await interaction.followup.send("⏳ Status: **Menunggu Pembayaran**")
        await send_status_update(interaction.guild, data.get("number", "?"), data.get("username", ""), data.get("user_id", 0), data.get("paket", ""), "⏳ Menunggu Pembayaran", 0xfee75c)
    @discord.ui.button(label="🔄 Diproses", style=discord.ButtonStyle.primary, custom_id="status_process")
    async def process(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not is_admin_or_owner(interaction.user, interaction.guild):
            await interaction.followup.send("❌ Hanya Admin!", ephemeral=True); return
        data = ticket_data.get(interaction.channel.id, {})
        if data: data["last_activity"] = time.time()
        await interaction.followup.send("🔄 Status: **Sedang Diproses**")
        await send_status_update(interaction.guild, data.get("number", "?"), data.get("username", ""), data.get("user_id", 0), data.get("paket", ""), "🔄 Sedang Diproses", 0x5865f2)
    @discord.ui.button(label="✅ Selesai", style=discord.ButtonStyle.success, custom_id="status_done")
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not is_admin_or_owner(interaction.user, interaction.guild):
            await interaction.followup.send("❌ Hanya Admin!", ephemeral=True); return
        data = ticket_data.get(interaction.channel.id, {})
        if data: data["last_activity"] = time.time()
        await interaction.followup.send("✅ Status: **Selesai**")
        await send_status_update(interaction.guild, data.get("number", "?"), data.get("username", ""), data.get("user_id", 0), data.get("paket", ""), "✅ Selesai", 0x57f287)
        if data and data.get("invoice_id"): update_invoice_status(data["invoice_id"], "DONE", interaction.user.name)

class CloseView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🔒 CLOSE TICKET", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not is_admin_or_owner(interaction.user, interaction.guild):
            await interaction.followup.send("❌ Hanya Admin!", ephemeral=True); return
        channel = interaction.channel; data = ticket_data.get(channel.id)
        if not data:
            await channel.delete(); return
        await interaction.followup.send(f"Ticket ditutup oleh {interaction.user.mention}...")
        await do_auto_close(interaction.guild, channel, data, reason="closed by owner", admin_user=interaction.user)

class SaldoView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="💳 CEK SALDO SAYA", style=discord.ButtonStyle.primary, custom_id="cek_saldo_btn")
    async def cek_saldo(self, interaction: discord.Interaction, button: discord.ui.Button):
        tr, tro, tt = get_total_belanja(interaction.user.id)
        tier, emoji, diskon, desc = get_member_tier(interaction.user.id)
        embed = discord.Embed(color=0xff1493)
        embed.description = f"💳 **SALDO KAMU**\n\nHalo {interaction.user.mention}\n👑 Tier: {emoji} {tier} - Diskon {diskon}%\n💰 Total Belanja: {format_rp(tr)}\n📦 Total Robux: {tro:,} R$\n🧾 Transaksi: {tt}x\n🎁 Referral: `{get_referral_code(interaction.user.id)}`"
        await interaction.response.send_message(embed=embed, ephemeral=True)

class OrderModal(discord.ui.Modal, title="Pesanan Robux"):
    nickname = discord.ui.TextInput(label="Nickname Roblox", placeholder="Nickname Roblox kamu", required=True)
    username = discord.ui.TextInput(label="Username", placeholder="UsernameRoblox", required=True)
    paket = discord.ui.TextInput(label="Paket yang dipilih", placeholder="Contoh: 500 Robux", required=True)
    pembayaran = discord.ui.TextInput(label="Metode Pembayaran", placeholder="QRIS", default="QRIS", required=True)
    kode_promo = discord.ui.TextInput(label="Kode Promo / Referral (Opsional)", placeholder="MIPI10 atau kode referral", required=False)
    async def on_submit(self, interaction: discord.Interaction):
        global ticket_counter
        if is_blacklisted(interaction.user.id):
            alasan, oleh, _ = get_blacklist_reason(interaction.user.id)
            await interaction.response.send_message(f"❌ Kamu di-blacklist!\nAlasan: {alasan}", ephemeral=True); return
        jumlah_int = parse_paket(self.paket.value)
        cukup, sisa = cek_stok_cukup(jumlah_int)
        if not cukup:
            await interaction.response.send_message(f"❌ **STOK GA CUKUP!** Mau {jumlah_int:,} R$, sisa {sisa:,} R$!\nMau Pre-Order? `/preorder`", ephemeral=True); return
        ticket_counter += 1
        guild = interaction.guild
        overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False), interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True), guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
        category = get_ticket_category(guild)
        channel = await guild.create_text_channel(name=f"robux-via-username-{ticket_counter}-{interaction.user.name}", overwrites=overwrites, category=category)
        harga_awal = get_harga(jumlah_int)
        tier_diskon_persen = get_tier_discount(interaction.user.id)
        tier_diskon = int(harga_awal * tier_diskon_persen / 100) if tier_diskon_persen > 0 else 0
        harga_setelah_tier = harga_awal - tier_diskon
        kode_input = self.kode_promo.value.strip() if self.kode_promo.value else ""
        referral_info = ""
        if kode_input and kode_input.upper().startswith("MIPI-"):
            sukses, msg = pakai_referral(kode_input, interaction.user.id, interaction.user.name)
            referral_info = f"\n🎁 Referral: {msg}" if sukses else f"\n⚠️ Referral: {msg}"
            kode_input = ""
        harga_akhir, diskon, err_promo = cek_promo(kode_input, harga_setelah_tier, jumlah_int)
        total_diskon = tier_diskon + diskon
        promo_text = ""
        if tier_diskon > 0:
            tier, emoji, _, _ = get_member_tier(interaction.user.id)
            promo_text += f"\n👑 Diskon Tier {emoji} {tier}: -{format_rp(tier_diskon)}"
        if kode_input and not err_promo and diskon > 0:
            pdata = load_promo(); k_up = kode_input.upper()
            if k_up in pdata:
                pdata[k_up]["dipakai"] = pdata[k_up].get("dipakai", 0) + 1
                save_promo(pdata)
            promo_text += f"\n🏷️ Promo {k_up}: -{format_rp(diskon)}\n💸 Harga Setelah Diskon: {format_rp(harga_akhir)}"
        elif kode_input and err_promo:
            promo_text += f"\n⚠️ Promo: {err_promo}"
        if referral_info: promo_text += referral_info
        inv_id = buat_invoice(interaction.user.id, interaction.user.name, self.paket.value, jumlah_int, harga_awal, harga_akhir, total_diskon, kode_input, self.pembayaran.value, self.username.value, self.nickname.value)
        ticket_data[channel.id] = {"user_id": interaction.user.id, "username": interaction.user.name, "nickname": self.nickname.value, "roblox_username": self.username.value, "pembayaran": self.pembayaran.value, "created_at": time.time(), "last_activity": time.time(), "number": ticket_counter, "paket": self.paket.value, "promo": kode_input, "harga_akhir": harga_akhir, "invoice_id": inv_id, "jumlah": jumlah_int}
        tier, emoji, _, _ = get_member_tier(interaction.user.id)
        embed = discord.Embed(title=f"🎫 Ticket Baru - {interaction.user.name}", description=f"**Nickname:** {self.nickname.value}\n**Username:** {self.username.value}\n**Paket:** {self.paket.value}\n**Pembayaran:** {self.pembayaran.value}{promo_text}\n**Ticket #{ticket_counter}**\n**🧾 Invoice:** `{inv_id}`\n**👑 Tier:** {emoji} {tier}\n\nKirim bukti QRIS disini ya 💗", color=0xff69b4)
        embed.set_image(url=WELCOME_URL)
        await channel.send(f"{interaction.user.mention} Halo! Selamat datang di MIPI STORE! 🌸", embed=embed, view=CloseView())
        embed_qris = discord.Embed(title="💳 Scan QRIS Disini", description=f"**Total:** {format_rp(harga_akhir)}\n**Invoice:** `{inv_id}`", color=0xff69b4)
        embed_qris.set_image(url=QRIS_URL)
        await channel.send(embed=embed_qris)
        await channel.send("**📦 STATUS ORDER - Owner only:**", view=StatusView())
        await send_status_update(guild, ticket_counter, interaction.user.name, interaction.user.id, self.paket.value, "🆕 Ticket Baru", 0xff69b4)
        go_view = discord.ui.View()
        go_view.add_item(discord.ui.Button(label="🚀 BUKA TICKET SAYA", style=discord.ButtonStyle.link, url=f"https://discord.com/channels/{guild.id}/{channel.id}"))
        await interaction.response.send_message(f"✅ Ticket dibuat!\n🧾 Invoice: `{inv_id}`\n💰 Total: {format_rp(harga_akhir)}\n👉 {channel.mention}", view=go_view, ephemeral=True)

class OrderView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="ORDER ROBUX", style=discord.ButtonStyle.primary, custom_id="order_robux")
    async def order_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if is_blacklisted(interaction.user.id):
            await interaction.response.send_message("❌ Kamu di-blacklist!", ephemeral=True); return
        if STORE_STATUS == "break":
            await interaction.response.send_message("🟡 **MIPI LAGI BREAK!** ☕\nMimin break 15-30 menit, ticket dikunci dulu ya!", ephemeral=True); return
        if STORE_STATUS == "closed":
            await interaction.response.send_message("🔴 **MIPI UDAH TUTUP!** 💤\nBalik besok ya, ticket dikunci biar ga numpuk!", ephemeral=True); return
        await interaction.response.send_modal(OrderModal())
        # ===== PART 3 - EVENTS + COMMAND UTAMA =====

@bot.event
async def on_message(message):
    if message.author.bot: return
    if message.guild and "market" in message.channel.name.lower():
        if message.author.id != message.guild.owner_id and not message.author.guild_permissions.administrator:
            if is_banned_selling(message.content):
                try: await message.delete()
                except: pass
                embed = discord.Embed(title="Stickied Message:", description="DILARANG MENJUAL PRODUK YANG KAMI JUAL SEPERTI ROBUX DAN LIMITED ITEM", color=0xff0000)
                warn = await message.channel.send(f"{message.author.mention}", embed=embed)
                await asyncio.sleep(10)
                try: await warn.delete()
                except: pass
                return
    if message.channel.id in ticket_data:
        ticket_data[message.channel.id]["last_activity"] = time.time()
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f"Login {bot.user} - MIPI STORE v5.0")
    bot.add_view(OrderView()); bot.add_view(CloseView()); bot.add_view(StatusView()); bot.add_view(RatingView(0)); bot.add_view(SaldoView()); bot.add_view(GiveawayView("dummy"))
    if not check_inactive.is_running(): check_inactive.start()
    if not cek_stok_alert.is_running(): cek_stok_alert.start()
    await bot.tree.sync()

# ===== TICKET =====
@bot.tree.command(name="ticket", description="Tampilkan panel order MIPI STORE")
async def ticket(interaction: discord.Interaction):
    if is_blacklisted(interaction.user.id):
        await interaction.response.send_message("❌ Kamu di-blacklist!", ephemeral=True); return
    if STORE_STATUS != "open":
        txt = "🟡 BREAK - Mimin break 15-30 menit!" if STORE_STATUS == "break" else "🔴 CLOSED - Toko tutup, balik besok yaa!"
        await interaction.response.send_message(f"{txt}\n\n🚫 Ticket dikunci biar ga spam!", ephemeral=True); return
    embed1 = discord.Embed(title="Mipi Store - Order Robux 💗", description="🌸 **ROBUX VIA USERNAME**\nFast Process • Aman • Instan\n\nSyarat:\n>> SUDAH 18+\n>> SUDAH TERVERIFIKASI 2 LANGKAH", color=0xff69b4)
    embed1.set_image(url=WELCOME_URL)
    stok = load_stok()
    embed2 = discord.Embed(title="💰 PRICELIST ROBUX FAST SEND", description=f"📦 Stok: {stok['total_stok']:,} R$\n\n500 = Rp 75.000\n1000 = Rp 150.000\n2000 = Rp 300.000\n3000 = Rp 450.000\n4000 = Rp 600.000\n5000 = Rp 750.000\n\n🌸 Eceran\n100 = Rp 16.000\n200 = Rp 32.000\n300 = Rp 48.000\n400 = Rp 64.000\n\n🛒 Click ORDER ROBUX dibawah, pembayaran hanya QRIS.", color=0xff69b4)
    embed2.set_image(url=QRIS_URL)
    embed2.set_footer(text="Mipi Store • Rafi Store")
    await interaction.response.send_message(embed=embed1)
    await interaction.followup.send(embed=embed2, view=OrderView())

@bot.tree.command(name="leaderboard", description="Lihat Top Buyer bulan ini")
async def leaderboard(interaction: discord.Interaction):
    bulan = datetime.now().strftime("%Y-%m")
    data = load_leaderboard()
    bulan_data = data.get(bulan, {})
    if not bulan_data:
        await interaction.response.send_message("Belum ada data Top Buyer bulan ini!", ephemeral=True); return
    sorted_users = sorted(bulan_data.items(), key=lambda x: x[1]["total"], reverse=True)[:10]
    medali = ["🥇","🥈","🥉","#4","#5","#6","#7","#8","#9","#10"]
    desc = f"Leaderboard {bulan}\n\n**TOP 10 BUYERS**\n"
    for i, (uid, info) in enumerate(sorted_users):
        tier, emoji, _, _ = get_member_tier(int(uid))
        desc += f"{medali[i]} <@{uid}> {emoji} — {info['total']:,} R$ · {info['transaksi']}x · {format_rp(info.get('total_rp',0))}\n"
    embed = discord.Embed(title="🏆 MIPI STORE — TOP BUYER", description=desc, color=0xff69b4)
    await interaction.response.send_message(embed=embed)

# ===== SALDO =====
@bot.tree.command(name="saldo", description="Cek total belanja kamu")
async def saldo_slash(interaction: discord.Interaction):
    tr, tro, tt = get_total_belanja(interaction.user.id)
    tier, emoji, diskon, desc = get_member_tier(interaction.user.id)
    embed = discord.Embed(color=0xff1493)
    embed.description = f"💳 **SALDO KAMU** ✨\n\nHalo {interaction.user.mention}\n\n👑 Tier: {emoji} {tier} - Diskon {diskon}%\n{desc}\n\n💰 Total Belanja: {format_rp(tr)}\n📦 Total Robux: {tro:,} R$\n🧾 Transaksi: {tt}x\n🎁 Referral: `{get_referral_code(interaction.user.id)}`"
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command(name="saldo")
async def saldo_prefix(ctx):
    tr, tro, tt = get_total_belanja(ctx.author.id)
    await ctx.send(f"💳 Saldo {ctx.author.mention}\n💰 {format_rp(tr)} | 📦 {tro:,} R$ | 🧾 {tt}x")

@bot.tree.command(name="setup-saldo", description="Kirim panel cek saldo (Owner only)")
async def setup_saldo(interaction: discord.Interaction):
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    embed = discord.Embed(title="💳 CEK SALDO - MIPI STORE", description="🌸 **MAU TAU UDAH HABIS BERAPA?**\n\nPencet **💳 CEK SALDO SAYA** dibawah!\n\n💰 Total Belanja\n📦 Total Robux\n🧾 Total Transaksi\n👑 Tier & Diskon\n\nCuma kamu yang bisa liat!", color=0xff69b4)
    await interaction.response.send_message(embed=embed, view=SaldoView())

@bot.tree.command(name="add-saldo", description="Tambah saldo manual (Admin only)")
async def add_saldo(interaction: discord.Interaction, user: discord.User, robux: int):
    if not is_admin_or_owner(interaction.user, interaction.guild):
        await interaction.response.send_message("❌ Hanya Admin!", ephemeral=True); return
    harga = get_harga(robux)
    add_to_leaderboard(user.id, user.name, f"{robux} Robux")
    await interaction.response.send_message(f"✅ Saldo {user.mention} ditambah!\n📦 +{robux:,} R$ | 💰 +{format_rp(harga)}")

# ===== PROMO =====
@bot.tree.command(name="buat-promo", description="Buat kode promo (Owner only)")
async def buat_promo(interaction: discord.Interaction, kode: str, diskon: int, tipe: str = "nominal", max_pakai: int = 10):
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    kode = kode.upper().strip()
    data = load_promo()
    data[kode] = {"diskon": diskon, "tipe": tipe, "max": max_pakai, "dipakai": 0, "dibuat_oleh": interaction.user.name}
    save_promo(data)
    desc = f"Diskon **{diskon}%**" if tipe == "persen" else f"Diskon **{format_rp(diskon)}**"
    await interaction.response.send_message(f"🎉 **Kode `{kode}` dibuat!**\n{desc}\n📦 Max: {max_pakai} orang | Min: 500 Robux")

@bot.tree.command(name="list-promo", description="Lihat semua promo")
async def list_promo(interaction: discord.Interaction):
    data = load_promo()
    if not data:
        await interaction.response.send_message("Belum ada promo! `/buat-promo` dulu!", ephemeral=True); return
    desc = "**🏷️ LIST PROMO**\n\n"
    for kode, p in data.items():
        sisa = p.get("max", 999) - p.get("dipakai", 0)
        d = f"{p['diskon']}%" if p["tipe"] == "persen" else format_rp(p["diskon"])
        status = "✅ AKTIF" if sisa > 0 else "❌ HABIS"
        desc += f"`{kode}` - {d} - Sisa {sisa} - {status}\n"
    await interaction.response.send_message(embed=discord.Embed(description=desc, color=0xff69b4), ephemeral=True)

@bot.tree.command(name="cek-promo", description="Cek kode promo")
async def cek_promo_cmd(interaction: discord.Interaction, kode: str, paket: str = "500"):
    kode_up = kode.upper().strip()
    data = load_promo()
    if kode_up not in data:
        await interaction.response.send_message(f"❌ Kode `{kode_up}` ga ada!", ephemeral=True); return
    jumlah = parse_paket(paket)
    harga_awal = get_harga(jumlah)
    harga_baru, diskon, err = cek_promo(kode_up, harga_awal, jumlah)
    if err:
        await interaction.response.send_message(err, ephemeral=True); return
    await interaction.response.send_message(f"✅ `{kode_up}` AKTIF!\n📦 {jumlah} R$ | 💰 {format_rp(harga_awal)} -> 💸 **{format_rp(harga_baru)}** (Diskon {format_rp(diskon)})", ephemeral=True)

@bot.tree.command(name="hapus-promo", description="Hapus promo (Owner only)")
async def hapus_promo(interaction: discord.Interaction, kode: str):
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    data = load_promo(); kode = kode.upper().strip()
    if kode not in data:
        await interaction.response.send_message("❌ Ga ketemu!", ephemeral=True); return
    del data[kode]; save_promo(data)
    await interaction.response.send_message(f"✅ Promo `{kode}` dihapus!", ephemeral=True)

# ===== GIVEAWAY =====
@bot.tree.command(name="giveaway", description="Buat giveaway (Owner only)")
async def giveaway_create(interaction: discord.Interaction, hadiah: str, durasi_menit: int, pemenang: int = 1):
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    gid = f"{interaction.channel.id}-{interaction.id}"
    end_time = int(time.time() + durasi_menit * 60)
    giveaway_data[gid] = {"hadiah": hadiah, "host_mention": interaction.user.mention, "host_id": interaction.user.id, "end_timestamp": end_time, "pemenang": pemenang, "peserta": [], "ended": False, "channel_id": interaction.channel.id}
    embed = discord.Embed(title="🎁 GIVEAWAY MIPI STORE!", description=f"🎁 **Hadiah:** {hadiah}\n\n👑 **Host:** {interaction.user.mention}\n⏰ **Berakhir:** <t:{end_time}:R>\n🏆 **Pemenang:** {pemenang} orang\n👥 **Peserta:** 0 orang", color=0xff69b4)
    await interaction.response.send_message(embed=embed, view=GiveawayView(gid))
    msg = await interaction.original_response()
    giveaway_data[gid]["message_id"] = msg.id
    await asyncio.sleep(durasi_menit * 60)
    await end_giveaway(interaction.guild, interaction.channel.id, msg.id, gid)

@bot.tree.command(name="giveaway-end", description="Akhiri giveaway sekarang (Owner only)")
async def giveaway_end(interaction: discord.Interaction):
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    found = None
    for gid, data in giveaway_data.items():
        if data["channel_id"] == interaction.channel.id and not data["ended"]:
            found = (gid, data); break
    if not found:
        await interaction.response.send_message("❌ Ga ada giveaway jalan!", ephemeral=True); return
    gid, data = found
    await interaction.response.send_message("🎉 Giveaway diakhiri! Mengundi...", ephemeral=True)
    await end_giveaway(interaction.guild, interaction.channel.id, data.get("message_id"), gid)

# ===== MARKET + PING =====
@bot.tree.command(name="market-rules", description="Kirim aturan market")
async def market_rules(interaction: discord.Interaction):
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    embed = discord.Embed(title="Stickied Message:", description="DILARANG MENJUAL PRODUK YANG KAMI JUAL SEPERTI ROBUX DAN LIMITED ITEM", color=0xff0000)
    msg = await interaction.channel.send(embed=embed)
    try: await msg.pin()
    except: pass
    await interaction.response.send_message("✅ Aturan di-pin!", ephemeral=True)

@bot.tree.command(name="ping", description="Cek bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! 🏓 MIPI STORE online! {round(bot.latency*1000)}ms | Stok: {load_stok()['total_stok']:,} R$ | Status: {STORE_STATUS.upper()}")

# ===== CHECK AVATAR =====
@bot.tree.command(name="checkavatar", description="Cek avatar Roblox")
async def checkavatar(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    try:
        headers = {"User-Agent": "Mozilla/5.0 MIPI-STORE"}
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.post("https://users.roproxy.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": True}) as r:
                data = await r.json()
                if not data.get("data"):
                    await interaction.followup.send(f"❌ Username `{username}` ga ketemu!"); return
                user = data["data"][0]; user_id = user["id"]; display = user.get("displayName", username); uname = user.get("name", username)
            async with s.get(f"https://users.roproxy.com/v1/users/{user_id}") as r:
                info = await r.json(); created = info.get("created", "")
                try: tgl = datetime.fromisoformat(created.replace("Z", "+00:00")).strftime("%d %B %Y")
                except: tgl = created
            async with s.get(f"https://thumbnails.roproxy.com/v1/users/avatar?userIds={user_id}&size=720x720&format=Png&isCircular=false") as r:
                thumb = await r.json(); avatar_url = thumb["data"][0]["imageUrl"] if thumb.get("data") else None
            profil_url = f"https://www.roblox.com/users/{user_id}/profile"
            desc = f"🔍 **Profil:** [{uname}]({profil_url})\n👤 **Display:** {display}\n🆔 **User ID:** {user_id}\n📅 **Dibuat:** {tgl}"
            e = discord.Embed(title=f"Profil Roblox: {uname}", description=desc, color=0xFF69B4)
            e.url = profil_url
            if avatar_url: e.set_image(url=avatar_url)
            e.set_footer(text="MIPI STORE • /checkavatar")
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="👤 Buka Profil", style=discord.ButtonStyle.link, url=profil_url))
            await interaction.followup.send(embed=e, view=view)
    except Exception as ex:
        await interaction.followup.send(f"❌ Gagal: {ex}")

@bot.tree.command(name="cekrbx", description="Cek riwayat transaksi Robux")
async def cekrbx(interaction: discord.Interaction, username: str = None):
    await interaction.response.defer(ephemeral=True)
    e = discord.Embed(title="🔍 CEK RIWAYAT ROBUX", description="Cek sendiri Robux kamu udah masuk / belum!", color=0xFF69B4)
    e.add_field(name="🔗 LINK RESMI", value="1. Transaksi:\nhttps://www.roblox.com/transactions\n\n2. Pending:\nhttps://www.roblox.com/transactions#pending-robux\n\n3. Saldo:\nhttps://www.roblox.com/my/account#!/info", inline=False)
    e.add_field(name="📖 CARA CEK", value="1. Login Roblox di browser\n2. Buka link Transaksi\n3. Kalo Pending, tunggu 3-7 hari (Hold Roblox)\n4. Kalo 7 hari belum masuk, buka ticket!", inline=False)
    if username:
        e.add_field(name="👤 Username yang dicek", value=username, inline=False)
    await interaction.followup.send(embed=e, ephemeral=True)

@bot.tree.command(name="setup-cek", description="Buat channel cek otomatis (Owner only)")
async def setup_cek(interaction: discord.Interaction):
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    cat = None
    for c in guild.categories:
        if "MIPI" in c.name.upper() and "CEK" in c.name.upper(): cat = c; break
    if not cat: cat = await guild.create_category("🌸・MIPI — CEK ROBLOX")
    ch1 = await guild.create_text_channel("🔍┆・check-avatar", category=cat)
    ch2 = await guild.create_text_channel("💰┆・cek-rbx", category=cat)
    await ch1.send(embed=discord.Embed(description="## 🌸 CHECK AVATAR\nKetik:\n```\n/checkavatar username: usernameKamu\n```", color=0xff69b4))
    await ch2.send(embed=discord.Embed(description="## 💰 CEK ROBUX\nKetik:\n```\n/cekrbx username: usernameKamu\n```\nLink: https://www.roblox.com/transactions", color=0xff69b4))
    await interaction.followup.send(f"✅ Berhasil!\n🔍 {ch1.mention}\n💰 {ch2.mention}", ephemeral=True)
    # ===== MIPI STORE - PART 4 + 5 FULL (REKBER PERSIS CHLOE) =====
import discord
from discord.ext import commands
import os, asyncio, random, string
from datetime import datetime

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ===== CONFIG - ISI PUNYA KAMU =====
WELCOME_URL = "https://link-gambar-welcome-kamu.png"
QRIS_URL = "https://link-gambar-qris-kamu.png"
STORE_STATUS = "open"  # open / closed
ticket_data = {}
blacklist_data = set()
rekber_data = {}
rekber_counter = 0
rekber_history = []

# ===== HELPER =====
def format_rp(n):
    try: return f"Rp {int(n):,}".replace(",", ".")
    except: return str(n)
def is_blacklisted(uid): return uid in blacklist_data
def is_admin_or_owner(user, guild):
    if guild and user.id == guild.owner_id: return True
    return user.guild_permissions.administrator if hasattr(user, 'guild_permissions') else False
def get_ticket_category(guild):
    for c in guild.categories:
        if "ticket" in c.name.lower(): return c
    return None

# ===== PART 4 - CORE / ORDER TICKET / BLACKLIST / SETUP =====
@bot.event
async def on_ready():
    print(f"✅ Login sebagai {bot.user} | MIPI STORE READY")
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} slash command sync")
    except Exception as e: print(e)

@bot.tree.command(name="status", description="Cek status toko")
async def status_cmd(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏪 MIPI STORE - Status: **{STORE_STATUS.upper()}**", ephemeral=True)

@bot.tree.command(name="blacklist", description="Blacklist user (Admin)")
async def blacklist_cmd(interaction: discord.Interaction, user: discord.Member):
    if not is_admin_or_owner(interaction.user, interaction.guild):
        await interaction.response.send_message("❌ Hanya Admin!", ephemeral=True); return
    blacklist_data.add(user.id)
    await interaction.response.send_message(f"⛔ {user.mention} di-blacklist!", ephemeral=True)

@bot.tree.command(name="unblacklist", description="Unblacklist user (Admin)")
async def unblacklist_cmd(interaction: discord.Interaction, user: discord.Member):
    if not is_admin_or_owner(interaction.user, interaction.guild):
        await interaction.response.send_message("❌ Hanya Admin!", ephemeral=True); return
    blacklist_data.discard(user.id)
    await interaction.response.send_message(f"✅ {user.mention} di-unblacklist!", ephemeral=True)

@bot.tree.command(name="open-toko", description="Buka toko (Owner)")
async def open_toko(interaction: discord.Interaction):
    global STORE_STATUS
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    STORE_STATUS = "open"
    await interaction.response.send_message("🟢 MIPI STORE DIBUKA!", ephemeral=True)

@bot.tree.command(name="close-toko", description="Tutup toko (Owner)")
async def close_toko(interaction: discord.Interaction):
    global STORE_STATUS
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    STORE_STATUS = "closed"
    await interaction.response.send_message("🔴 MIPI STORE DITUTUP!", ephemeral=True)

# ===== PART 5 - REKBER / MIDDLEMAN PERSIS CHLOE =====
REKBER_FEES = [
    ("Rp 1.000 - Rp 9.000", 1000, 9000, 1500),
    ("Rp 10.000 - Rp 49.000", 10000, 49000, 1500),
    ("Rp 50.000 - Rp 99.000", 50000, 99000, 1500),
    ("Rp 100.000 - Rp 199.000", 100000, 199000, 2500),
    ("Rp 200.000 - Rp 499.000", 200000, 499000, 4000),
    ("Rp 500.000 - Rp 1.000.000", 500000, 1000000, 7000),
    ("Di atas Rp 1.000.000", 1000001, 999999999, 10000),
]
def get_fee_rekber(harga):
    for label, mn, mx, fee in REKBER_FEES:
        if mn <= harga <= mx: return label, fee
    return "Di atas Rp 1.000.000", 10000
def get_rekber_state(user_id):
    if user_id not in rekber_data:
        rekber_data[user_id] = {"rentang": None, "fee": 0, "rentang_label": "-", "buyer_id": None, "seller_id": None, "fee_by": None, "jenis": "-", "harga": 0, "harga_text": "-"}
    return rekber_data[user_id]

# --- MODAL DETAIL BARANG ---
class RekberDetailModalV2(discord.ui.Modal, title="Detail Barang Middleman"):
    def __init__(self, user_id, parent_view):
        super().__init__()
        self.user_id = user_id
        self.parent_view = parent_view
    jenis = discord.ui.TextInput(label="Jenis Barang", placeholder="Contoh: Nama Item/Akun Roblox/Robux/Dll.", required=True, max_length=100)
    harga = discord.ui.TextInput(label="Harga Barang (angka saja)", placeholder="Contoh: 100000 atau 100.000", required=True, max_length=20)
    async def on_submit(self, interaction: discord.Interaction):
        harga_bersih = self.harga.value.replace(".", "").replace(",", "").replace("Rp", "").replace(" ", "")
        try: harga_int = int(harga_bersih)
        except:
            await interaction.response.send_message("❌ Harga harus angka!", ephemeral=True); return
        st = get_rekber_state(self.user_id)
        st["jenis"] = self.jenis.value; st["harga"] = harga_int; st["harga_text"] = format_rp(harga_int)
        self.parent_view.build()
        await interaction.response.edit_message(view=self.parent_view)

# --- STATUS VIEW DI DALAM TICKET REKBER ---
class RekberStatusView(discord.ui.View):
    def __init__(self, rekber_id, data):
        super().__init__(timeout=None)
        self.rekber_id = rekber_id
        self.data = data
    @discord.ui.button(label="💳 Buyer Sudah Bayar", style=discord.ButtonStyle.primary, custom_id="rekber_bayar")
    async def bayar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"✅ {interaction.user.mention} konfirmasi **Buyer Sudah Bayar**! Admin tolong cek mutasi ya!")
    @discord.ui.button(label="📦 Seller Sudah Kirim", style=discord.ButtonStyle.primary, custom_id="rekber_kirim")
    async def kirim(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"📦 {interaction.user.mention} konfirmasi **Seller Sudah Kirim**! Buyer tolong cek barangnya ya!")
    @discord.ui.button(label="✅ Barang Diterima", style=discord.ButtonStyle.success, custom_id="rekber_terima")
    async def terima(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"✅ {interaction.user.mention} konfirmasi **Barang Diterima**! Admin, bisa teruskan duit ke Seller! 💰")
    @discord.ui.button(label="🎉 Selesai / Close", style=discord.ButtonStyle.success, custom_id="rekber_done")
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_admin_or_owner(interaction.user, interaction.guild):
            await interaction.response.send_message("❌ Hanya Admin yang bisa close Rekber!", ephemeral=True); return
        data_hist = None
        for h in rekber_history:
            if h["id"] == self.rekber_id:
                h["status"] = "SELESAI"; data_hist = h; break
        if data_hist:
            guild = interaction.guild
            buyer = guild.get_member(data_hist["buyer_id"]) or data_hist["buyer"]
            seller = guild.get_member(data_hist["seller_id"]) or data_hist["seller"]
            ticket_id = await kirim_history_rekber(guild, self.rekber_id, buyer, seller, data_hist["jenis"], data_hist["harga"], data_hist["fee"], data_hist["fee_by"], interaction.user)
            await interaction.response.send_message(f"🎉 Rekber `REKBER-{self.rekber_id}` **SELESAI**!\n🎫 Ticket ID: `{ticket_id}`\n📜 History sudah di-post!\nTicket akan dihapus 10 detik lagi...")
        else:
            await interaction.response.send_message(f"🎉 Rekber `REKBER-{self.rekber_id}` SELESAI!")
        await asyncio.sleep(10)
        try: await interaction.channel.delete()
        except: pass

# --- FORM V2 PERSIS VIDEO CHLOE ---
class RekberFormV2(discord.ui.LayoutView):
    def __init__(self, user_id):
        super().__init__(timeout=600)
        self.user_id = user_id
        self.build()
    def build(self):
        st = get_rekber_state(self.user_id)
        self.clear_items()
        self.add_item(discord.ui.TextDisplay(
            f"• Rentang Transaksi: {st['rentang_label']}\n"
            f"• Fee Rekber: {format_rp(st['fee']) if st['fee'] else '-'}\n"
            f"• Buyer: {f'<@{st['buyer_id']}>' if st['buyer_id'] else '-'}\n"
            f"• Seller: {f'<@{st['seller_id']}>' if st['seller_id'] else '-'}\n"
            f"• Fee Ditanggung: {st['fee_by'] or '-'}\n"
            f"• Jenis Barang: {st['jenis']}\n"
            f"• Harga Barang: {st['harga_text']}"
        ))
        self.add_item(discord.ui.TextDisplay("Pilih rentang harga transaksi."))
        rentang = discord.ui.StringSelect(placeholder="Pilih rentang transaksi", custom_id="rekber_rentang", options=[
            discord.SelectOption(label="Rp 1.000 - Rp 9.000", description="Fee: Rp 1.500", value="0"),
            discord.SelectOption(label="Rp 10.000 - Rp 49.000", description="Fee: Rp 1.500", value="1"),
            discord.SelectOption(label="Rp 50.000 - Rp 99.000", description="Fee: Rp 1.500", value="2"),
            discord.SelectOption(label="Rp 100.000 - Rp 199.000", description="Fee: Rp 2.500", value="3"),
            discord.SelectOption(label="Rp 200.000 - Rp 499.000", description="Fee: Rp 4.000", value="4"),
            discord.SelectOption(label="Rp 500.000 - Rp 1.000.000", description="Fee: Rp 7.000", value="5"),
            discord.SelectOption(label="Di atas Rp 1.000.000", description="Fee: Rp 10.000", value="6"),
        ])
        rentang.callback = self.pilih_rentang
        self.add_item(discord.ui.ActionRow(rentang))
        self.add_item(discord.ui.TextDisplay("Klik jika pembelinya kamu ->"))
        b1 = discord.ui.Button(label="Saya", style=discord.ButtonStyle.primary, custom_id="saya_buyer")
        b1.callback = self.saya_buyer
        u1 = discord.ui.UserSelect(placeholder="Pilih buyer", custom_id="pilih_buyer")
        u1.callback = self.pilih_buyer_cb
        self.add_item(discord.ui.ActionRow(b1, u1))
        self.add_item(discord.ui.TextDisplay("Klik jika penjualnya kamu ->"))
        b2 = discord.ui.Button(label="Saya", style=discord.ButtonStyle.primary, custom_id="saya_seller")
        b2.callback = self.saya_seller
        u2 = discord.ui.UserSelect(placeholder="Pilih seller", custom_id="pilih_seller")
        u2.callback = self.pilih_seller_cb
        self.add_item(discord.ui.ActionRow(b2, u2))
        self.add_item(discord.ui.TextDisplay("Pilih yang bayar fee rekber."))
        fee_by = discord.ui.StringSelect(placeholder="Fee rekber ditanggung oleh...", custom_id="fee_by", options=[
            discord.SelectOption(label="Pembeli", value="Pembeli"),
            discord.SelectOption(label="Penjual", value="Penjual"),
            discord.SelectOption(label="Split (50:50)", value="Split (50:50)"),
        ])
        fee_by.callback = self.pilih_fee_by
        self.add_item(discord.ui.ActionRow(fee_by))
        btn_detail = discord.ui.Button(label="📝 Isi Detail Barang", style=discord.ButtonStyle.primary, custom_id="isi_detail")
        btn_detail.callback = self.isi_detail
        self.add_item(discord.ui.ActionRow(btn_detail))
        btn_buat = discord.ui.Button(label="✅ Buat Ticket", style=discord.ButtonStyle.success, custom_id="buat_ticket")
        btn_buat.callback = self.buat_ticket
        btn_batal = discord.ui.Button(label="❌ Batal", style=discord.ButtonStyle.danger, custom_id="batal")
        btn_batal.callback = self.batal
        self.add_item(discord.ui.ActionRow(btn_buat, btn_batal))
    async def refresh(self, interaction):
        self.build(); await interaction.response.edit_message(view=self)
    async def pilih_rentang(self, interaction):
        idx = int(interaction.data["values"][0])
        label, mn, mx, fee = REKBER_FEES[idx]
        st = get_rekber_state(self.user_id); st["rentang_label"] = label; st["fee"] = fee
        await self.refresh(interaction)
    async def saya_buyer(self, interaction):
        st = get_rekber_state(self.user_id); st["buyer_id"] = interaction.user.id; await self.refresh(interaction)
    async def pilih_buyer_cb(self, interaction):
        st = get_rekber_state(self.user_id); st["buyer_id"] = int(interaction.data["values"][0]); await self.refresh(interaction)
    async def saya_seller(self, interaction):
        st = get_rekber_state(self.user_id); st["seller_id"] = interaction.user.id; await self.refresh(interaction)
    async def pilih_seller_cb(self, interaction):
        st = get_rekber_state(self.user_id); st["seller_id"] = int(interaction.data["values"][0]); await self.refresh(interaction)
    async def pilih_fee_by(self, interaction):
        st = get_rekber_state(self.user_id); st["fee_by"] = interaction.data["values"][0]; await self.refresh(interaction)
    async def isi_detail(self, interaction):
        await interaction.response.send_modal(RekberDetailModalV2(self.user_id, self))
    async def buat_ticket(self, interaction):
        global rekber_counter
        st = get_rekber_state(self.user_id)
        if not st["rentang_label"] or st["rentang_label"] == "-" or not st["buyer_id"] or not st["seller_id"] or not st["fee_by"] or st["jenis"] == "-" or st["harga"] == 0:
            await interaction.response.send_message("❌ Lengkapi semua field dulu: rentang, buyer, seller, fee ditanggung oleh, jenis barang, dan harga barang.", ephemeral=True); return
        if st["buyer_id"] == st["seller_id"]:
            await interaction.response.send_message("❌ Buyer dan seller tidak boleh user yang sama.", ephemeral=True); return
        rekber_counter += 1
        guild = interaction.guild
        buyer = guild.get_member(st["buyer_id"]) or await guild.fetch_member(st["buyer_id"])
        seller = guild.get_member(st["seller_id"]) or await guild.fetch_member(st["seller_id"])
        overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False), buyer: discord.PermissionOverwrite(read_messages=True, send_messages=True), seller: discord.PermissionOverwrite(read_messages=True, send_messages=True), interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True), guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
        cat = get_ticket_category(guild)
        channel = await guild.create_text_channel(name=f"rekber-{rekber_counter}-{buyer.name}-{seller.name}", overwrites=overwrites, category=cat)
        fee = st["fee"]
        if st["fee_by"] == "Pembeli": total_buyer = st["harga"] + fee; terima_seller = st["harga"]
        elif st["fee_by"] == "Penjual": total_buyer = st["harga"]; terima_seller = st["harga"] - fee
        else: total_buyer = st["harga"] + fee//2; terima_seller = st["harga"] - fee//2
        embed = discord.Embed(title=f"🛡️ REKBER MIPI STORE - #{rekber_counter}", description=f"**👤 Buyer:** {buyer.mention}\n**👤 Seller:** {seller.mention}\n**📦 Jenis:** {st['jenis']}\n**💰 Harga:** {format_rp(st['harga'])}\n**💸 Fee:** {format_rp(fee)} ({st['fee_by']})\n**💳 Buyer Transfer:** {format_rp(total_buyer)}\n**💰 Seller Terima:** {format_rp(terima_seller)}", color=0xff69b4)
        embed.set_image(url=WELCOME_URL)
        await channel.send(f"{buyer.mention} {seller.mention} Ticket Rekber dibuat oleh {interaction.user.mention}!", embed=embed, view=RekberStatusView(rekber_counter, st))
        await channel.send(embed=discord.Embed(title="💳 Buyer Transfer Kesini", description=f"Total: {format_rp(total_buyer)}", color=0xff69b4).set_image(url=QRIS_URL))
        rekber_history.append({"id": rekber_counter, "buyer": buyer.name, "buyer_id": st["buyer_id"], "seller": seller.name, "seller_id": st["seller_id"], "jenis": st["jenis"], "harga": st["harga"], "fee": fee, "fee_by": st["fee_by"], "status": "BERJALAN", "waktu": datetime.now().isoformat(), "channel": channel.name})
        del rekber_data[self.user_id]
        await interaction.response.send_message(f"✅ Ticket Rekber dibuat! 🎫 {channel.mention}", ephemeral=True)
    async def batal(self, interaction):
        if self.user_id in rekber_data: del rekber_data[self.user_id]
        await interaction.response.edit_message(content="❌ Pembuatan Ticket Rekber dibatalkan.", view=None)

# --- PANEL UTAMA ---
class RekberPanelView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="📜 History Transaksi", style=discord.ButtonStyle.secondary, custom_id="rekber_history")
    async def history_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not rekber_history:
            await interaction.response.send_message("Belum ada transaksi Rekber!", ephemeral=True); return
        desc = "**📜 HISTORY TRANSAKSI REKBER - MIPI STORE**\n\n"
        for h in rekber_history[-10:]:
            desc += f"• `REKBER-{h['id']}` - {h['jenis']} - {format_rp(h['harga'])} - Fee {format_rp(h['fee'])} - {h['buyer']} ➡️ {h['seller']} - {h['status']}\n"
        await interaction.response.send_message(embed=discord.Embed(description=desc, color=0xff69b4), ephemeral=True)
    @discord.ui.button(label="🛡️ Buat Ticket Middleman", style=discord.ButtonStyle.success, custom_id="rekber_buat_ticket")
    async def buat_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if is_blacklisted(interaction.user.id):
            await interaction.response.send_message("❌ Kamu di-blacklist!", ephemeral=True); return
        if STORE_STATUS != "open":
            await interaction.response.send_message("🔴 MIPI lagi CLOSED! Rekber buka lagi pas OPEN ya!", ephemeral=True); return
        rekber_data[interaction.user.id] = {"rentang": None, "fee": 0, "rentang_label": "-", "buyer_id": None, "seller_id": None, "fee_by": None, "jenis": "-", "harga": 0, "harga_text": "-"}
        view = RekberFormV2(interaction.user.id)
        await interaction.response.send_message(view=view, ephemeral=True)

# --- HISTORY ---
def get_history_rekber_channel(guild):
    for ch in guild.text_channels:
        if "history" in ch.name.lower() and ("rekber" in ch.name.lower() or "midman" in ch.name.lower()): return ch
    return None
def buat_ticket_id_rekber():
    kode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"T-{kode[:4]}-{kode[4:]}"
async def kirim_history_rekber(guild, rekber_id, buyer, seller, jenis, harga, fee, fee_by, admin):
    ch = get_history_rekber_channel(guild)
    if not ch: ch = await guild.create_text_channel(name="history-midman-rekber")
    ticket_id = buat_ticket_id_rekber()
    tanggal = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    embed = discord.Embed(title=f"Transaksi Middleman Berhasil #{rekber_id}", description=f"**Detail Transaksi:**\n• Ticket ID: {ticket_id}\n• Pembeli: {buyer.mention if hasattr(buyer, 'mention') else buyer}\n• Penjual: {seller.mention if hasattr(seller, 'mention') else seller}\n• Jenis Barang: {jenis}\n• Nominal Transaksi: {format_rp(harga)}\n• Fee Rekber: {format_rp(fee)} ({fee_by})\n• Tanggal Transaksi: {tanggal}\n• Admin Midman: {admin.mention if hasattr(admin, 'mention') else admin}\n\nTerima kasih telah menggunakan layanan middleman MIPI STORE.", color=0x57f287)
    embed.set_footer(text="MIPI STORE • Rekber Aman 100% • Trusted")
    await ch.send(embed=embed)
    return ticket_id

@bot.tree.command(name="setup-rekber", description="Kirim panel Rekber (Owner only)")
async def setup_rekber(interaction: discord.Interaction):
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    embed = discord.Embed(title="Middleman/Rekber Service by MIPI STORE", description="━━━━━━━━━━━━━━━\n\n**Daftar Fee Middleman:**\n• Rp 1.000 - Rp 9.000 -> Fee 1.500\n• Rp 10.000 - Rp 49.000 -> Fee 1.500\n• Rp 50.000 - Rp 99.000 -> Fee 1.500\n• Rp 100.000 - Rp 199.000 -> Fee 2.500\n• Rp 200.000 - Rp 499.000 -> Fee 4.000\n• Rp 500.000 - Rp 1.000.000 -> Fee 7.000\n• Di atas Rp 1.000.000 -> Fee 10.000\n\n🔖 Fee dibayar 1x per transaksi\n🔖 Fee bisa ditanggung buyer / seller / split\n\nUntuk membuat ticket middleman, klik tombol dibawah lalu pilih buyer dan seller dari dropdown member Discord.", color=0x2b2d31)
    embed.set_footer(text="MIPI STORE • Rekber Aman 100%")
    await interaction.response.send_message(embed=embed, view=RekberPanelView())

@bot.tree.command(name="setup-history-rekber", description="Bikin channel history rekber (Owner)")
async def setup_history_rekber(interaction: discord.Interaction):
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True); return
    ch = get_history_rekber_channel(interaction.guild)
    if ch:
        await interaction.response.send_message(f"✅ Udah ada: {ch.mention}", ephemeral=True); return
    ch = await interaction.guild.create_text_channel(name="history-midman-rekber", topic="History Transaksi Middleman / Rekber MIPI STORE")
    await ch.send(embed=discord.Embed(title="📜 History Transaksi Middleman - MIPI STORE", description="Semua transaksi Rekber yang BERHASIL akan muncul disini otomatis! 💗", color=0x57f287))
    await interaction.response.send_message(f"✅ Channel history dibuat: {ch.mention}", ephemeral=True)

@bot.tree.command(name="cek-fee-rekber", description="Cek fee rekber")
async def cek_fee_rekber(interaction: discord.Interaction, harga: int):
    label, fee = get_fee_rekber(harga)
    await interaction.response.send_message(f"💰 Harga: {format_rp(harga)}\n📊 Rentang: {label}\n💸 Fee: **{format_rp(fee)}**", ephemeral=True)

@bot.tree.command(name="history-rekber", description="Lihat history rekber")
async def history_rekber_cmd(interaction: discord.Interaction):
    if not rekber_history:
        await interaction.response.send_message("Belum ada transaksi Rekber!", ephemeral=True); return
    desc = "**📜 HISTORY REKBER**\n\n"
    for h in rekber_history[-15:]:
        desc += f"• `REKBER-{h['id']}` - {h['jenis']} - {format_rp(h['harga'])} - Fee {format_rp(h['fee'])} - {h['status']}\n"
    await interaction.response.send_message(embed=discord.Embed(description=desc, color=0xff69b4), ephemeral=True)

bot.run(os.getenv("DISCORD_TOKEN"))
