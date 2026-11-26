import discord
from discord.ext import commands, tasks
import os, time, io, html, re, asyncio, json, random, string, traceback
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ================= URL GAMBAR =================
WELCOME_URL = "https://raw.githubusercontent.com/mipistore/mipi-store/main/97b3c2a7-b1e8-66b1-50e5-563dc75098ea.jpeg"
THANKYOU_URL = "https://raw.githubusercontent.com/mipistore/mipi-store/main/IMG_6021.jpeg"
QRIS_URL = "https://raw.githubusercontent.com/mipistore/mipi-store/main/IMG_5210.jpeg"
VIA_USERNAME_URL = "https://raw.githubusercontent.com/mipistore/mipi-store/main/864c8b52-4d57-770d-955f-6e16b985f6e0.jpeg"
VIA_LOGIN_URL = "https://raw.githubusercontent.com/mipistore/mipi-music-bot/main/bddf1ab5-866b-c73a-2ea1-db6ed86dcc7f.jpeg"
VIA_KOMUNITAS_URL = "https://raw.githubusercontent.com/mipistore/mipi-store/main/1b346831-9a9d-2db7-466e-e9428ceee394.jpeg"
PLUS_URL = "https://raw.githubusercontent.com/mipistore/mipi-store/main/5b214a07-38d3-e810-d036-13d6487029de.jpeg"
LIMITED_URL = "https://raw.githubusercontent.com/mipistore/mipi-store/main/3c1a8b02-4d92-ee3a-8cfd-854906585b1d.jpeg"
TOP_SULTAN_IMAGE = "https://raw.githubusercontent.com/mipistore/mipi-store/main/4ee2813b-3c4b-c291-86d0-38b8fe36132d.jpeg"

ticket_data = {}
ticket_counter = 0
user_ratings = {}
user_last_ticket = {}
STORE_STATUS = "open"
OPEN_CLOSE_CHANNEL_ID = 1569135504262299689

# ================= HELPER ANTI ERROR =================
async def safe_defer(interaction, ephemeral=False):
    try:
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=ephemeral)
            return True
    except Exception as e:
        print(f"Defer gagal: {e}")
    return False

async def safe_followup(interaction, content=None, embed=None, embeds=None, view=None, ephemeral=False):
    try:
        if interaction.response.is_done():
            return await interaction.followup.send(content=content, embed=embed, embeds=embeds, view=view, ephemeral=ephemeral)
        else:
            return await interaction.response.send_message(content=content, embed=embed, embeds=embeds, view=view, ephemeral=ephemeral)
    except Exception as e:
        print(f"Followup gagal: {e}")
        try:
            return await interaction.channel.send(content=content, embed=embed, embeds=embeds, view=view)
        except Exception as e2:
            print(f"Channel send gagal: {e2}")
            return None

async def safe_send(channel, content=None, embed=None, embeds=None, view=None):
    try:
        return await channel.send(content=content, embed=embed, embeds=embeds, view=view)
    except Exception as e:
        print(f"Send gagal: {e}")
        return None

@bot.tree.error
async def on_app_command_error(interaction, error):
    print(f"=== SLASH ERROR {interaction.command.name if interaction.command else '?'} ===")
    traceback.print_exception(type(error), error, error.__traceback__)
    try:
        msg = f"❌ Error: {str(error)[:400]}\nCoba lagi ya, kalo masih error SS ke owner!"
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)
    except:
        try:
            await interaction.channel.send(f"❌ Error di {interaction.command.name if interaction.command else 'command'}: {error}")
        except:
            pass

# ================= PRICELIST PER KATEGORI - SAMPE 10000 ROBUX - BEDA-BEDA =================
PRICELIST_FILE = "pricelist.json"

def _harga_base(nominal, rate_per_100):
    # rate_per_100 = harga per 100 robux, misal 160 = Rp 16.000 per 100
    return int(nominal * rate_per_100 / 100)

def _build_pricelist(rate_per_100, diskon_besar=0.0):
    # Buat pricelist 100 sampe 10000 otomatis, biar lengkap sampe 1000+ dan gak error
    out = {}
    for nominal in [100,200,300,400,500,600,700,800,900,1000,1200,1500,2000,2500,3000,4000,5000,6000,7000,8000,9000,10000]:
        harga = _harga_base(nominal, rate_per_100)
        # Diskon dikit buat nominal gede biar menarik
        if nominal >= 5000:
            harga = int(harga * 0.97)
        elif nominal >= 1000:
            harga = int(harga * 0.98)
        # Bulatin ke 500 terdekat biar rapi
        harga = int(round(harga / 500) * 500)
        out[nominal] = harga
    return out

# HARGA UDAH DIATUR BEDA-BEDA:
# Username: 160 per 100, Login: 180 per 100 (paling mahal), Komunitas: 140 per 100 (paling murah)
DEFAULT_PRICELIST_PER_KATEGORI = {
    "via_username": _build_pricelist(160),
    "via_login": _build_pricelist(180),
    "via_komunitas": _build_pricelist(140),
    "plus": _build_pricelist(160),
    "limited": _build_pricelist(160),
}
DEFAULT_PRICELIST = DEFAULT_PRICELIST_PER_KATEGORI["via_username"].copy()

def _load_all_pricelist_raw():
    try:
        with open(PRICELIST_FILE, "r") as f:
            d = json.load(f)
            if isinstance(d, dict):
                return d
    except Exception as e:
        print(f"Load pricelist gagal: {e}")
    return {}

def load_pricelist(kategori="via_username"):
    try:
        raw = _load_all_pricelist_raw()
        if raw and raw.keys() and list(raw.keys())[0].isdigit():
            if kategori == "via_username":
                try:
                    return {int(k): int(v) for k, v in raw.items()}
                except:
                    pass
            return DEFAULT_PRICELIST_PER_KATEGORI.get(kategori, DEFAULT_PRICELIST).copy()
        if kategori in raw and isinstance(raw[kategori], dict):
            try:
                return {int(k): int(v) for k, v in raw[kategori].items()}
            except:
                pass
        return DEFAULT_PRICELIST_PER_KATEGORI.get(kategori, DEFAULT_PRICELIST).copy()
    except Exception as e:
        print(f"load_pricelist error: {e}")
        return DEFAULT_PRICELIST_PER_KATEGORI.get(kategori, DEFAULT_PRICELIST).copy()

def save_pricelist(data, kategori="via_username"):
    try:
        raw = _load_all_pricelist_raw()
        if raw and raw.keys() and list(raw.keys())[0].isdigit():
            old = {}
            try:
                old = {int(k): int(v) for k, v in raw.items()}
            except:
                pass
            raw = {"via_username": {str(k): v for k, v in old.items()}}
            for kat in ["via_login", "via_komunitas", "plus", "limited"]:
                if kat not in raw:
                    raw[kat] = {str(k): v for k, v in DEFAULT_PRICELIST_PER_KATEGORI[kat].items()}
        if not raw:
            for kat in ["via_username", "via_login", "via_komunitas", "plus", "limited"]:
                raw[kat] = {str(k): v for k, v in DEFAULT_PRICELIST_PER_KATEGORI[kat].items()}
        raw[kategori] = {str(k): int(v) for k, v in data.items()}
        with open(PRICELIST_FILE, "w") as f:
            json.dump(raw, f, indent=2)
        return True
    except Exception as e:
        print(f"save_pricelist error: {e}")
        return False

def get_harga(robux, kategori="via_username"):
    try:
        data = load_pricelist(kategori)
        robux = int(robux)
        if robux in data:
            return int(data[robux])
        # Kalo nominal gak ada di list (misal 550), hitung pake rate kategori itu, biar gak error
        base = DEFAULT_PRICELIST_PER_KATEGORI.get(kategori, DEFAULT_PRICELIST)
        rate = 160
        if kategori == "via_login":
            rate = 180
        elif kategori == "via_komunitas":
            rate = 140
        return int(robux * rate / 100)
    except Exception as e:
        print(f"get_harga error: {e}")
        return int(robux) * 150

def format_rp(n):
    try:
        return f"Rp {int(n):,}".replace(",", ".")
    except:
        return f"Rp {n}"

def build_pricelist_text(kategori="via_username"):
    try:
        data = load_pricelist(kategori)
        fast = ""
        ecer = ""
        for rbx in sorted(data.keys()):
            h = format_rp(data[rbx])
            if rbx >= 500:
                fast += f"{rbx} = {h}\n"
            else:
                ecer += f"{rbx} = {h}\n"
        return f"{fast}\nRobux Eceran\n{ecer}\nCara Order\nClick tombol ORDER dibawah, isi formulir, lalu tunggu admin. Pembayaran hanya QRIS."
    except Exception as e:
        print(f"build_pricelist_text error: {e}")
        return "Pricelist lagi error, coba /lihat-harga lagi ya!"

CATEGORY_PRICELIST = {
    "via_username": {"title": "PRICELIST ROBUX VIA USERNAME", "image": VIA_USERNAME_URL, "desc": "Fast Process - Aman - Instan\nSyarat: SUDAH 18+ & SUDAH 2 LANGKAH"},
    "via_login": {"title": "PRICELIST ROBUX VLOG / VIA LOGIN", "image": VIA_LOGIN_URL, "desc": "Via Login / Vlog - Proses Cepat\nAkun harus sudah 18+"},
    "via_komunitas": {"title": "PRICELIST ROBUX VIA KOMUNITAS", "image": VIA_KOMUNITAS_URL, "desc": "Via Komunitas / Group\nMasuk grup dulu, robux cair 14 hari"},
    "plus": {"title": "PRICELIST ROBLOX PLUS", "image": PLUS_URL, "desc": "Roblox Plus Monthly\nAktif 30 hari, full garansi"},
    "limited": {"title": "PRICELIST LIMITED ITEM", "image": LIMITED_URL, "desc": "Beli / Jual Limited Via Trade\nHarga sesuai pasaran, tanya admin dulu"},
}

def build_pricelist_embed(kategori="via_username"):
    info = CATEGORY_PRICELIST.get(kategori, CATEGORY_PRICELIST["via_username"])
    e = discord.Embed(title=info["title"], description=info["desc"] + "\n\n" + build_pricelist_text(kategori), color=0xff69b4)
    e.set_image(url=info["image"])
    e.set_footer(text="Mipi Store - Rafi Store | Harga bisa berubah sewaktu-waktu")
    return e

def build_all_pricelist_embeds():
    return [build_pricelist_embed(k) for k in ["via_username", "via_login", "via_komunitas", "plus", "limited"]]

def jenis_to_kategori(jenis):
    try:
        j = str(jenis).upper()
        if "VIA LOGIN" in j:
            return "via_login"
        if "VIA KOMUNITAS" in j:
            return "via_komunitas"
        if "PLUSS" in j or "PLUS" in j:
            return "plus"
        if "LIMITED" in j or "OFFSALE" in j:
            return "limited"
        return "via_username"
    except:
        return "via_username"

# ================= LEADERBOARD =================
LEADERBOARD_FILE = "leaderboard.json"
def load_leaderboard():
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)
    except:
        return {}
def save_leaderboard(d):
    try:
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(d, f, indent=2)
    except Exception as e:
        print(f"save leaderboard error: {e}")
def add_to_leaderboard(user_id, username, paket_text, kategori="via_username"):
    try:
        m = re.search(r'(\d+)', str(paket_text).replace('.', '').replace(',', ''))
        if not m:
            return
        jumlah = int(m.group(1))
        harga = get_harga(jumlah, kategori)
        data = load_leaderboard()
        bulan = datetime.now().strftime("%Y-%m")
        if bulan not in data:
            data[bulan] = {}
        uid = str(user_id)
        if uid not in data[bulan]:
            data[bulan][uid] = {"username": username, "total": 0, "transaksi": 0, "total_rp": 0}
        if "total_rp" not in data[bulan][uid]:
            data[bulan][uid]["total_rp"] = 0
        data[bulan][uid]["username"] = username
        data[bulan][uid]["total"] += jumlah
        data[bulan][uid]["transaksi"] += 1
        data[bulan][uid]["total_rp"] += harga
        save_leaderboard(data)
    except Exception as e:
        print(f"add leaderboard error: {e}")
def get_total_belanja(user_id):
    try:
        data = load_leaderboard()
        tr = tro = tt = 0
        for bulan, users in data.items():
            uid = str(user_id)
            if uid in users:
                tr += users[uid].get("total_rp", 0)
                tro += users[uid].get("total", 0)
                tt += users[uid].get("transaksi", 0)
        return tr, tro, tt
    except:
        return 0, 0, 0

PENDING_FILE = "pending_saldo.json"
def load_pending():
    try:
        with open(PENDING_FILE, "r") as f:
            return json.load(f)
    except:
        return {}
def save_pending(d):
    try:
        with open(PENDING_FILE, "w") as f:
            json.dump(d, f, indent=2)
    except Exception as e:
        print(f"save pending error: {e}")
def add_to_pending(user_id, username, paket_text, ticket_number, channel_name="", kategori="via_username"):
    try:
        m = re.search(r'(\d+)', str(paket_text).replace('.', '').replace(',', ''))
        if not m:
            return None
        jumlah = int(m.group(1))
        harga = get_harga(jumlah, kategori)
        data = load_pending()
        oid = f"ORDER-{ticket_number:06d}"
        data[oid] = {"user_id": str(user_id), "username": username, "paket": paket_text, "robux": jumlah, "harga": harga, "ticket_number": ticket_number, "channel": channel_name, "kategori": kategori, "waktu": datetime.now().strftime("%d %b %Y %H:%M")}
        save_pending(data)
        return oid
    except Exception as e:
        print(f"add pending error: {e}")
        return None

def get_top_sultan_channel(guild):
    try:
        for ch in guild.text_channels:
            if "top-sultan" in ch.name.lower() or "top-leaderboard" in ch.name.lower():
                return ch
    except:
        pass
    return None

def build_top_sultan_embed_bulanan():
    try:
        data = load_leaderboard()
        bulan_ini = datetime.now().strftime("%Y-%m")
        users = data.get(bulan_ini, {})
        s = sorted(users.items(), key=lambda x: x[1].get("total_rp", 0), reverse=True)[:10]
        tp = len(users)
        tpes = sum(v.get("transaksi", 0) for v in users.values())
        tom = sum(v.get("total_rp", 0) for v in users.values())
        nama_bulan = datetime.now().strftime("%B %Y")
        desc = f"MIPI STORE • LEADERBOARD BULANAN - {nama_bulan}\nDaftar peringkat bulan ini aja! Bulan depan ke-reset lagi dari 0!\n\n"
        if not s:
            desc += "> Belum ada Sultan bulan ini! Order dulu, jadi #1 bulan ini!\n\n"
        else:
            medals = ["🥇","🥈","🥉"]
            for i, (uid, info) in enumerate(s):
                medal = medals[i] if i < 3 else "🏅"
                desc += f"{medal} **Peringkat #{i+1} - <@{uid}>** ({info.get('username','User')})\n"
                desc += f"└ Rp {info.get('total_rp',0):,} • {info.get('transaksi',0)}x Transaksi\n".replace(",", ".")
        desc += f"\n📊 **STATISTIK BULAN INI ({nama_bulan})**\n• Pembeli: {tp} Pembeli\n• Pesanan: {tpes} Pesanan\n• Omset: Rp {tom:,}\n".replace(",", ".")
        desc += f"\n⚡ Ke-reset tiap tanggal 1! Papan ini cuma buat bulan {nama_bulan} aja!\n🕒 Terakhir diperbarui: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB"
        e = discord.Embed(title=f"🏆 TOP 10 SULTAN BULANAN - {nama_bulan}", description=desc, color=0xff69b4)
        e.set_image(url=TOP_SULTAN_IMAGE)
        e.set_footer(text="MIPI STORE - TOP SULTAN BULANAN • Auto Update")
        return e
    except Exception as e:
        print(f"top bulanan error: {e}")
        return discord.Embed(title="Top Sultan Bulanan", description="Lagi error, coba lagi ya!", color=0xff0000)

def build_top_sultan_embed_semua():
    try:
        data = load_leaderboard()
        gabung = {}
        for bulan, users in data.items():
            for uid, info in users.items():
                if uid not in gabung:
                    gabung[uid] = {"username": info.get("username","User"), "total_rp": 0, "total": 0, "transaksi": 0}
                gabung[uid]["total_rp"] += info.get("total_rp", 0)
                gabung[uid]["total"] += info.get("total", 0)
                gabung[uid]["transaksi"] += info.get("transaksi", 0)
                gabung[uid]["username"] = info.get("username", gabung[uid]["username"])
        s = sorted(gabung.items(), key=lambda x: x[1]["total_rp"], reverse=True)[:10]
        tp = len(gabung)
        tpes = sum(v["transaksi"] for v in gabung.values())
        tom = sum(v["total_rp"] for v in gabung.values())
        desc = "MIPI STORE • LEADERBOARD SEMUA / ALL TIME\nDaftar peringkat dari pertama toko buka sampe sekarang! GA PERNAH KE-RESET!\n\n"
        if not s:
            desc += "> Belum ada Sultan! Order dulu, jadi #1 sepanjang masa!\n\n"
        else:
            medals = ["🥇","🥈","🥉"]
            for i, (uid, info) in enumerate(s):
                medal = medals[i] if i < 3 else "🏅"
                desc += f"{medal} **Peringkat #{i+1} - <@{uid}>** ({info['username']})\n"
                desc += f"└ Rp {info['total_rp']:,} • {info['transaksi']}x Transaksi\n".replace(",", ".")
        desc += f"\n📊 **STATISTIK ALL TIME**\n• Pembeli: {tp} Pembeli\n• Pesanan: {tpes} Pesanan\n• Omset: Rp {tom:,}\n".replace(",", ".")
        desc += f"\n👑 Ini Sultan sepanjang masa! Ga ke-reset walau ganti bulan!\n🕒 Terakhir diperbarui: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB"
        e = discord.Embed(title="👑 TOP 10 SULTAN SEMUA / ALL TIME", description=desc, color=0x2B2D31)
        e.set_image(url=TOP_SULTAN_IMAGE)
        e.set_footer(text="MIPI STORE - TOP SULTAN ALL TIME • Auto Update")
        return e
    except Exception as e:
        print(f"top semua error: {e}")
        return discord.Embed(title="Top Sultan", description="Lagi error, coba lagi ya!", color=0xff0000)

def build_top_sultan_embed():
    return build_top_sultan_embed_semua()

async def update_top_sultan(guild):
    try:
        ch = get_top_sultan_channel(guild)
        if not ch:
            return
        embed = build_top_sultan_embed_semua()
        try:
            async for msg in ch.history(limit=20):
                if msg.author == guild.me and msg.embeds and "TOP 10 SULTAN" in str(msg.embeds[0].title):
                    await msg.edit(embed=embed)
                    return
            await ch.send(embed=embed)
        except Exception as e:
            print(f"Gagal update top-sultan: {e}")
    except Exception as e:
        print(f"update_top_sultan error: {e}")

@tasks.loop(minutes=1)
async def auto_update_top_sultan():
    for guild in bot.guilds:
        try:
            await update_top_sultan(guild)
        except:
            pass

def is_admin_or_owner(user, guild):
    try:
        if user.id == guild.owner_id:
            return True
        if user.guild_permissions.administrator:
            return True
        rn = [r.name.lower() for r in user.roles]
        return any(x in rn for x in ["admin", "owner", "staff", "moderator", "adm"])
    except:
        return False

class KonfirmasiSaldoView(discord.ui.View):
    def __init__(self, order_id):
        super().__init__(timeout=None)
        self.order_id = order_id
    @discord.ui.button(label="✅ Konfirmasi Masuk Saldo", style=discord.ButtonStyle.success, custom_id="saldo_confirm_btn")
    async def confirm_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if not is_admin_or_owner(interaction.user, interaction.guild):
                await interaction.response.send_message("❌ Hanya Admin / Owner!", ephemeral=True)
                return
            pend = load_pending()
            if self.order_id not in pend:
                await interaction.response.send_message("❌ Udah dikonfirmasi / ditolak!", ephemeral=True)
                return
            d = pend[self.order_id]
            add_to_leaderboard(int(d["user_id"]), d["username"], d["paket"], kategori=d.get("kategori", "via_username"))
            del pend[self.order_id]
            save_pending(pend)
            await interaction.response.send_message(f"✅ **SALDO DIKONFIRMASI!**\nBuyer: <@{d['user_id']}>\nPaket: {d['paket']}\n+{d['robux']} R$ udah masuk saldo + Top Sultan!", ephemeral=False)
            for item in self.children:
                item.disabled = True
            try:
                await interaction.message.edit(view=self)
            except:
                pass
            try:
                await update_top_sultan(interaction.guild)
            except:
                pass
            try:
                u = await bot.fetch_user(int(d["user_id"]))
                await u.send(f"🎉 Saldo kamu ditambah! +{d['robux']} R$ dari {d['paket']} udah dikonfirmasi admin!")
            except:
                pass
        except Exception as e:
            print(f"confirm saldo error: {e}")
            try:
                await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)
            except:
                pass
    @discord.ui.button(label="❌ Tolak / Order Palsu", style=discord.ButtonStyle.danger, custom_id="saldo_reject_btn")
    async def reject_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if not is_admin_or_owner(interaction.user, interaction.guild):
                await interaction.response.send_message("❌ Hanya Admin / Owner!", ephemeral=True)
                return
            pend = load_pending()
            if self.order_id not in pend:
                await interaction.response.send_message("❌ Udah diproses!", ephemeral=True)
                return
            d = pend[self.order_id]
            del pend[self.order_id]
            save_pending(pend)
            await interaction.response.send_message(f"❌ Order {self.order_id} ({d['paket']} - <@{d['user_id']}>) **DITOLAK**, ga masuk saldo!", ephemeral=False)
            for item in self.children:
                item.disabled = True
            try:
                await interaction.message.edit(view=self)
            except:
                pass
            try:
                await update_top_sultan(interaction.guild)
            except:
                pass
        except Exception as e:
            print(f"reject saldo error: {e}")

# ================= PROMO =================
PROMO_FILE = "promo.json"
def load_promo():
    try:
        with open(PROMO_FILE, "r") as f:
            return json.load(f)
    except:
        return {}
def save_promo(d):
    try:
        with open(PROMO_FILE, "w") as f:
            json.dump(d, f, indent=2)
    except Exception as e:
        print(f"save promo error: {e}")
def cek_promo(kode, harga_awal, jumlah_robux=0):
    try:
        if not kode or not str(kode).strip():
            return harga_awal, 0, None
        kode = str(kode).upper().strip()
        data = load_promo()
        if kode not in data:
            return harga_awal, 0, "Kode promo tidak ditemukan!"
        p = data[kode]
        if jumlah_robux < 500:
            return harga_awal, 0, "Minimal belanja 500 Robux untuk pakai promo ini!"
        if p.get("dipakai", 0) >= p.get("max", 999):
            return harga_awal, 0, "Kode promo sudah habis dipakai!"
        diskon = int(harga_awal * p["diskon"] / 100) if p["tipe"] == "persen" else int(p["diskon"])
        return max(0, harga_awal - diskon), diskon, None
    except Exception as e:
        print(f"cek promo error: {e}")
        return harga_awal, 0, None

# ================= GIVEAWAY =================
giveaway_data = {}
class GiveawayView(discord.ui.View):
    def __init__(self, giveaway_id):
        super().__init__(timeout=None)
        self.giveaway_id = giveaway_id
    @discord.ui.button(label="JOIN GIVEAWAY", style=discord.ButtonStyle.success, custom_id="join_giveaway", emoji="🎉")
    async def join_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            data = giveaway_data.get(self.giveaway_id)
            if not data:
                await interaction.response.send_message("Giveaway ini sudah berakhir!", ephemeral=True)
                return
            if data["ended"]:
                await interaction.response.send_message("Giveaway sudah berakhir Wal!", ephemeral=True)
                return
            uid = interaction.user.id
            if uid in data["peserta"]:
                await interaction.response.send_message("Kamu udah join Wal!", ephemeral=True)
                return
            data["peserta"].append(uid)
            try:
                embed = interaction.message.embeds[0]
                embed.description = "Hadiah: " + str(data["hadiah"]) + "\nHost: " + str(data["host_mention"]) + "\nPeserta: " + str(len(data["peserta"])) + " orang"
                await interaction.message.edit(embed=embed, view=self)
            except:
                pass
            await interaction.response.send_message("Berhasil join giveaway " + str(data["hadiah"]) + "! Good luck!", ephemeral=True)
        except Exception as e:
            print(f"join giveaway error: {e}")

async def end_giveaway(guild, channel_id, message_id, giveaway_id):
    try:
        data = giveaway_data.get(giveaway_id)
        if not data or data["ended"]:
            return
        data["ended"] = True
        channel = guild.get_channel(channel_id)
        if not channel:
            return
        try:
            msg = await channel.fetch_message(message_id)
        except:
            msg = None
        if len(data["peserta"]) == 0:
            if msg:
                embed = discord.Embed(title="GIVEAWAY BERAKHIR - GAK ADA PESERTA", description="Hadiah: " + str(data["hadiah"]), color=0xff0000)
                await msg.edit(embed=embed, view=None)
            await channel.send("Giveaway berakhir tapi gak ada yang join!")
            return
        winners = random.sample(data["peserta"], min(data["pemenang"], len(data["peserta"])))
        wm = ", ".join([f"<@{w}>" for w in winners])
        if msg:
            embed = discord.Embed(title="GIVEAWAY BERAKHIR - PEMENANG TERPILIH!", description="Hadiah: " + str(data["hadiah"]) + "\n\nPemenang:\n" + wm + "\n\nTotal Peserta: " + str(len(data["peserta"])) + " orang", color=0x57f287)
            await msg.edit(embed=embed, view=None)
        await channel.send("GIVEAWAY BERAKHIR!\n\nHadiah: " + str(data["hadiah"]) + "\nPemenang: " + wm)
    except Exception as e:
        print(f"Gagal end giveaway: {e}")

# ================= FILTER MARKET =================
BANNED_WORDS = ["wts robux", "jual robux", "sell robux", "jual rb", "wts rb", "jual limited", "wts limited", "sell limited", "jual robux murah", "robux murah", "top up robux", "jual akun robux", "wts akun robux", "wtt robux", "wtb robux", "jual robux via", "robux via username murah"]
ALLOWED_IF_HAS = ["akun pribadi", "akun roblox", "akun pribadi secepatnya"]
def is_banned_selling(text):
    try:
        low = str(text).lower()
        if any(a in low for a in ALLOWED_IF_HAS) and "robux" not in low and "limited" not in low:
            return False
        return any(w in low for w in BANNED_WORDS)
    except:
        return False

def hitung_harga(paket_text, kategori="via_username"):
    try:
        m = re.search(r'(\d+)', str(paket_text).replace('.', '').replace(',', ''))
        if not m:
            return "500", "Rp 75.000"
        jumlah = int(m.group(1))
        return str(jumlah), f"Rp {get_harga(jumlah, kategori):,}".replace(",", ".")
    except:
        return "500", "Rp 75.000"

def get_status_channel(guild):
    try:
        for ch in guild.text_channels:
            if "order-status" in ch.name.lower():
                return ch
    except:
        pass
    return None
def get_history_channel(guild):
    try:
        for ch in guild.text_channels:
            if "history" in ch.name.lower():
                return ch
    except:
        pass
    return None
def get_ticket_category(guild):
    try:
        for cat in guild.categories:
            if "TICKET" in cat.name.upper():
                return cat
    except:
        pass
    return None
def get_vouch_channel(guild):
    try:
        for ch in guild.channels:
            if "vouch" in ch.name.lower():
                return ch
    except:
        pass
    return None

def make_html_transcript(number, messages, username, paket, duration):
    try:
        rows = ""
        for m in messages:
            rows += "<div style=\"margin:6px 0;padding:8px;background:#2b2d31;border-radius:8px;\"><b style=\"color:#fff;\">" + html.escape(str(m["author"])) + "</b> <span style=\"color:#949ba4;font-size:12px;\">" + m["time"] + "</span><br><span style=\"color:#dbdee1;\">" + html.escape(m["content"] or "(gambar / embed)") + "</span></div>"
        return "<!DOCTYPE html><html><head><meta charset=\"utf-8\"><title>Ticket #" + str(number) + " Transcript - MIPI STORE</title></head><body style=\"background:#1e1f22;font-family:sans-serif;padding:20px;\"><h2 style=\"color:white;\">MIPI STORE - Ticket #" + str(number) + "</h2><p style=\"color:#949ba4;\">Created by " + html.escape(username) + " | Subject: " + html.escape(paket) + " | Duration: " + str(duration) + " minutes | " + str(len(messages)) + " messages</p>" + rows + "</body></html>"
    except:
        return "<html><body>Transcript error</body></html>"

async def send_status_update(guild, number, username, user_id, paket, status_text, color):
    try:
        ch = get_status_channel(guild)
        if not ch:
            return
        embed = discord.Embed(title="Order Status - Ticket #" + str(number), description="Customer: <@" + str(user_id) + "> (" + username + ")\nPaket: " + paket + "\nStatus: " + status_text, color=color)
        embed.set_footer(text="MIPI STORE - Order Status")
        await ch.send(embed=embed)
    except Exception as e:
        print(f"send status error: {e}")

async def send_history_log(guild, channel, data, admin_user):
    try:
        ch = get_history_channel(guild)
        if not ch:
            return
        number = data["number"]
        user_id = data["user_id"]
        roblox_user = data.get("roblox_username", data.get("username", "-"))
        nickname = data.get("nickname", "-")
        paket = data.get("paket", "500 Robux")
        pembayaran = data.get("pembayaran", "Qris")
        jumlah, harga = hitung_harga(paket, data.get("kategori", "via_username"))
        ticket_name = channel.name if channel else "ticket-" + str(number)
        admin_text = admin_user.mention if admin_user else "Auto-Close"
        embed = discord.Embed(color=0x2b2d31)
        embed.description = "Ticket Log\n\nTicket\n" + ticket_name + "\nAction\nClosed\nPanel\nMipi Store Ticket\nMember\n<@" + str(user_id) + ">\nNickname Roblox\n" + nickname + "\nUsername Roblox\n" + roblox_user + "\nJumlah Robux\n" + jumlah + "\nTotal Harga\n" + harga + "\nPayment\n" + pembayaran + "\nAdmin\n" + admin_text
        embed.set_image(url=THANKYOU_URL)
        await ch.send(embed=embed)
    except Exception as e:
        print(f"send history error: {e}")

async def send_vouch(guild, user, paket, stars, komentar, ticket_number=0, ticket_name=""):
    try:
        ch = get_vouch_channel(guild)
        if not ch:
            return
        jumlah, harga = hitung_harga(paket)
        star_str = "⭐" * stars
        seller = guild.owner.mention if guild.owner else "MIPI STORE"
        if not ticket_name:
            ticket_name = "ticket-" + str(ticket_number) + "-" + user.name
        embed = discord.Embed(color=0x2b2d31)
        embed.description = "VOUCH RECEIVED\n\nTicket ID\n" + str(ticket_number) + "\nNominal\n" + harga + "\nSeller\n" + seller + "\nBuyer\n<@" + str(user.id) + ">\nHandled by\n" + seller + "\nRating\n" + star_str + "\nKomentar\n" + komentar + " 💗\nSource\n" + ticket_name
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="MIPI STORE Vouch System | " + datetime.now().strftime("%B %d, %Y at %I:%M %p"))
        msg = await ch.send(embed=embed)
        try:
            thread_name = "Vouch - " + user.name + " | Ticket #" + str(ticket_number)
            if isinstance(ch, discord.ForumChannel):
                await ch.create_thread(name=thread_name, content="Vouch dari " + user.mention + " - Ticket #" + str(ticket_number) + " - " + paket + " - " + star_str + " - " + komentar)
            else:
                thread = await msg.create_thread(name=thread_name, auto_archive_duration=1440)
                await thread.send("Vouch dari " + user.mention + "\n\nPaket: " + paket + " (" + harga + ")\nRating: " + star_str + "\nKomentar: " + komentar + "\nTicket: " + ticket_name)
        except Exception as e:
            print(f"Gagal buat thread vouch: {e}")
    except Exception as e:
        print(f"send vouch error: {e}")

async def do_auto_close(guild, channel, data, reason="auto-closed due to inactivity", admin_user=None):
    try:
        number = data["number"]
        user_id = data["user_id"]
        paket = data.get("paket", "ORDER ROBUX")
        created = data["created_at"]
        duration = int((time.time() - created)//60)
        if duration < 1:
            duration = 1
        user_last_ticket[user_id] = {"number": number, "paket": paket, "ticket_name": channel.name if channel else "", "seller_id": guild.owner_id}
        try:
            await send_history_log(guild, channel, data, admin_user)
        except Exception as e:
            print(f"Gagal history: {e}")
        messages = []
        try:
            async for m in channel.history(limit=200, oldest_first=True):
                messages.append({"author": str(m.author), "time": m.created_at.strftime("%H:%M"), "content": m.content})
        except:
            pass
        status_ch = get_status_channel(guild)
        if status_ch:
            try:
                embed1 = discord.Embed(title="Ticket Auto-Closed", description="#" + str(number) + " " + reason + "\nTicket ID\n" + str(number), color=0xfee75c)
                embed1.set_footer(text=datetime.now().strftime("%B %d, %Y at %I:%M %p"))
                await status_ch.send(embed=embed1)
                html_text = make_html_transcript(number, messages, data.get("username", "User"), paket, duration)
                file = discord.File(io.BytesIO(html_text.encode()), filename="ticket-" + str(number) + "-auto-transcript.html")
                embed2 = discord.Embed(title="Auto-Generated Transcript (Auto-Closed)", description="Transcript automatically generated for auto-closed ticket #" + str(number) + "\n\nTicket\nTicket #" + str(number) + "\nCreated by <@" + str(user_id) + ">\n" + str(len(messages)) + " messages\n\nGeneration\nDuration: " + str(duration) + " minutes\nStatus: Auto-Closed -> Auto-Transcript\n\nSubject\n" + paket, color=0x5865f2)
                embed2.set_footer(text=datetime.now().strftime("%B %d, %Y at %I:%M %p"))
                await status_ch.send(embed=embed2, file=file)
            except Exception as e:
                print(f"send status transcript error: {e}")
        try:
            user = await bot.fetch_user(user_id)
            closer = admin_user.name if admin_user else "MIPI STORE (Auto-Close)"
            embed = discord.Embed(title="Rate Your Experience", description="Hi " + user.name + "! Your support ticket has been resolved.\nPlease rate your experience by clicking a star below.\n\nTicket #" + str(number) + " in MIPI STORE\nResolved in\n" + str(duration) + " minutes\n\nClosed by\n" + closer, color=0x2b2d31)
            await user.send(embed=embed, view=RatingView(number))
        except:
            pass
        try:
            order_id = add_to_pending(user_id, data.get("username", "User"), paket, number, channel.name if channel else "", kategori=data.get("kategori", "via_username"))
            if order_id:
                ch_pending = get_history_channel(guild) or get_status_channel(guild)
                if ch_pending:
                    jumlah_tmp, harga_tmp = hitung_harga(paket, data.get("kategori", "via_username"))
                    embed_p = discord.Embed(title=f"⏳ PENDING SALDO - {order_id}", description=f"Buyer: <@{user_id}>\nPaket: {paket}\nRobux: {jumlah_tmp} R$\nHarga: {harga_tmp}\nTicket: #{number}\n\n**Order ini BELUM masuk leaderboard!**\nAdmin harus pencet ✅ dulu baru masuk saldo!", color=0xfee75c)
                    await ch_pending.send(embed=embed_p, view=KonfirmasiSaldoView(order_id))
        except Exception as e:
            print(f"Gagal pending saldo: {e}")
        if channel.id in ticket_data:
            del ticket_data[channel.id]
        try:
            await channel.delete()
        except:
            pass
    except Exception as e:
        print(f"do_auto_close error: {e}")
        traceback.print_exc()

@tasks.loop(minutes=1)
async def check_inactive():
    try:
        now = time.time()
        for channel_id, data in list(ticket_data.items()):
            last = data.get("last_activity", data["created_at"])
            if now - last > 15*60:
                ch = bot.get_channel(channel_id)
                if not ch:
                    del ticket_data[channel_id]
                    continue
                await do_auto_close(ch.guild, ch, data)
    except Exception as e:
        print(f"check_inactive error: {e}")

class RatingView(discord.ui.View):
    def __init__(self, ticket_number):
        super().__init__(timeout=None)
        self.ticket_number = ticket_number
    async def send_thanks(self, interaction, stars):
        try:
            user_ratings[interaction.user.id] = stars
            star_str = "⭐" * stars
            embed = discord.Embed(title="Terima Kasih! 💗", description="Kamu memberi rating " + star_str + " (" + str(stars) + "/5) untuk MIPI STORE!\n\nTerima kasih sudah order di Mipi Store! Ditunggu order berikutnya ya 🌸", color=0xff69b4)
            embed.set_image(url=THANKYOU_URL)
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            print(f"rating error: {e}")
    @discord.ui.button(label="⭐ 1", style=discord.ButtonStyle.secondary, custom_id="rate1")
    async def r1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_thanks(interaction, 1)
    @discord.ui.button(label="⭐ 2", style=discord.ButtonStyle.secondary, custom_id="rate2")
    async def r2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_thanks(interaction, 2)
    @discord.ui.button(label="⭐ 3", style=discord.ButtonStyle.primary, custom_id="rate3")
    async def r3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_thanks(interaction, 3)
    @discord.ui.button(label="⭐ 4", style=discord.ButtonStyle.success, custom_id="rate4")
    async def r4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_thanks(interaction, 4)
    @discord.ui.button(label="⭐ 5", style=discord.ButtonStyle.success, custom_id="rate5")
    async def r5(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_thanks(interaction, 5)
    @discord.ui.button(label="📝 Add Comment", style=discord.ButtonStyle.secondary, custom_id="add_comment", row=1)
    async def comment(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_modal(CommentModal(ticket_number=self.ticket_number))
        except Exception as e:
            print(f"comment modal error: {e}")
    @discord.ui.button(label="❌ No Thanks", style=discord.ButtonStyle.secondary, custom_id="no_thanks", row=1)
    async def no_thanks(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.edit_message(content="Oke! Terima kasih sudah order di MIPI STORE 💗", embed=None, view=None)
        except:
            pass

class CommentModal(discord.ui.Modal, title="Komentar / Testimoni"):
    def __init__(self, ticket_number):
        super().__init__()
        self.ticket_number = ticket_number
    komentar = discord.ui.TextInput(label="Komentar kamu", placeholder="satset poll", style=discord.TextStyle.paragraph, required=True)
    async def on_submit(self, interaction: discord.Interaction):
        try:
            stars = user_ratings.get(interaction.user.id, 5)
            last = user_last_ticket.get(interaction.user.id, {})
            paket = last.get("paket", "500 Robux")
            ticket_name = last.get("ticket_name", "ticket-" + str(self.ticket_number) + "-" + interaction.user.name)
            try:
                guild = None
                for g in bot.guilds:
                    ch = get_vouch_channel(g)
                    if ch:
                        guild = g
                        break
                if guild:
                    await send_vouch(guild, interaction.user, paket, stars, self.komentar.value, ticket_number=self.ticket_number, ticket_name=ticket_name)
            except Exception as e:
                print(f"Gagal vouch: {e}")
            await interaction.response.send_message("Terima kasih komentarnya! 💗\n> " + self.komentar.value + "\n\nVouch kamu sudah muncul di vouch + jadi thread! 🎉\nRating: " + ("⭐"*stars) + " (" + str(stars) + "/5)", ephemeral=True)
        except Exception as e:
            print(f"comment submit error: {e}")
            try:
                await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)
            except:
                pass

class StatusView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="⏳ Menunggu Pembayaran", style=discord.ButtonStyle.secondary, custom_id="status_waiting")
    async def waiting(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
            if not is_admin_or_owner(interaction.user, interaction.guild):
                await interaction.followup.send("Hanya Admin & Owner!", ephemeral=True)
                return
            data = ticket_data.get(interaction.channel.id, {})
            if data:
                data["last_activity"] = time.time()
            await interaction.followup.send("Status diubah: Menunggu Pembayaran")
            await send_status_update(interaction.guild, data.get("number", "?"), data.get("username", interaction.user.name), data.get("user_id", interaction.user.id), data.get("paket", "ORDER"), "Menunggu Pembayaran", 0xfee75c)
        except Exception as e:
            print(f"status waiting error: {e}")
    @discord.ui.button(label="🔄 Diproses", style=discord.ButtonStyle.primary, custom_id="status_process")
    async def process(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
            if not is_admin_or_owner(interaction.user, interaction.guild):
                await interaction.followup.send("Hanya Admin & Owner!", ephemeral=True)
                return
            data = ticket_data.get(interaction.channel.id, {})
            if data:
                data["last_activity"] = time.time()
            await interaction.followup.send("Status diubah: Sedang Diproses")
            await send_status_update(interaction.guild, data.get("number", "?"), data.get("username", interaction.user.name), data.get("user_id", interaction.user.id), data.get("paket", "ORDER"), "Sedang Diproses", 0x5865f2)
        except Exception as e:
            print(f"status process error: {e}")
    @discord.ui.button(label="✅ Selesai", style=discord.ButtonStyle.success, custom_id="status_done")
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
            if not is_admin_or_owner(interaction.user, interaction.guild):
                await interaction.followup.send("Hanya Admin & Owner!", ephemeral=True)
                return
            data = ticket_data.get(interaction.channel.id, {})
            if data:
                data["last_activity"] = time.time()
            await interaction.followup.send("Status diubah: Selesai!")
            await send_status_update(interaction.guild, data.get("number", "?"), data.get("username", interaction.user.name), data.get("user_id", interaction.user.id), data.get("paket", "ORDER"), "Selesai / Done", 0x57f287)
        except Exception as e:
            print(f"status done error: {e}")

class CloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="🔒 CLOSE TICKET", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
            if not is_admin_or_owner(interaction.user, interaction.guild):
                await interaction.followup.send("Hanya Admin & Owner!", ephemeral=True)
                return
            channel = interaction.channel
            data = ticket_data.get(channel.id)
            if not data:
                await interaction.followup.send("Ticket ditutup...")
                await channel.delete()
                return
            await interaction.followup.send("Ticket ditutup oleh " + interaction.user.mention + ". Membuat transcript...")
            await do_auto_close(interaction.guild, channel, data, reason="closed by owner", admin_user=interaction.user)
        except Exception as e:
            print(f"close error: {e}")

class SaldoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="💳 CEK SALDO SAYA", style=discord.ButtonStyle.primary, custom_id="cek_saldo_btn")
    async def cek_saldo(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            tr, tro, tt = get_total_belanja(interaction.user.id)
            embed = discord.Embed(color=0xff1493)
            embed.description = "INFORMASI SALDO / TOTAL TRANSAKSI\n\nHalo " + interaction.user.mention + ",\n\nTotal Belanja: " + format_rp(tr) + "\nTotal Robux: " + str(tro) + " R$\nTotal Transaksi: " + str(tt) + "x\n\nMIPI STORE - CHECK SALDO"
            embed.set_footer(text="Mipi Store - Rafi Store")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"saldo view error: {e}")
            try:
                await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)
            except:
                pass

# === EMOJI ATAS (EMBED) - UNICODE - DIJAMIN MUNCUL ===
E_VIA = "💎"; E_VLOG = "💎"; E_BELI_LIMITED = "💠"; E_JUAL_LIMITED = "💰"; E_OFFSALE = "🎁"; E_PLUS = "⭐"; E_REKBER = "🛡️"; E_NANYA = "🐱"; E_KOMUNITAS = "👥"; E_AKUN = "💃"

def build_ticket_panel_baru_embed():
    e = discord.Embed(title="🎫 Mipi Store - Ticket Order", description=f"{E_VIA} **Robux Via Username** - Beli Robux Via Username\n{E_VLOG} **Robux Vlog** - Beli Robux melalui via login\n{E_BELI_LIMITED} **Beli Limited Item** - Beli Item Via Trade\n{E_JUAL_LIMITED} **Jual Limited Item** - Dapatkan Uang (Cashout)\n{E_OFFSALE} **Beli Item Offsale** - Via Redeem Code\n{E_PLUS} **Beli Roblox Plus** - Roblox Plus Monthly\n{E_REKBER} **Rekber/MM** - Rekber, Akun, Jasa, dll\n{E_NANYA} **Other/Nanya** - Pertanyaan & bantuan lainnya\n{E_KOMUNITAS} **Via Komunitas** - Beli Robux Via Komunitas / Group\n{E_AKUN} **Beli Akun** - Beli Akun Roblox Sultan / Stok\n\nMipi Store Powered by MIPI 💗", color=0x2B2D31)
    e.set_image(url=WELCOME_URL)
    e.set_footer(text="Mipi Store - Pilih tombol di bawah sesuai kebutuhan kamu!")
    return e

class OrderModalBaru(discord.ui.Modal):
    def __init__(self, jenis: str):
        super().__init__(title=f"Order - {jenis}")
        self.jenis = jenis
        try:
            if jenis in ["BELI LIMITED", "JUAL LIMITED", "BELI ITEM OFFSALE"]:
                self.f1 = discord.ui.TextInput(label="Username Roblox", placeholder="Username Roblox kamu", required=True)
                self.f2 = discord.ui.TextInput(label="Nama Item", placeholder="Contoh: Domino Crown", required=True)
                self.f3 = discord.ui.TextInput(label="Harga / Budget", placeholder="Contoh: 500k / QRIS", required=True)
            elif jenis == "BELI AKUN":
                self.f1 = discord.ui.TextInput(label="Username Discord / Roblox", placeholder="Username kamu", required=True)
                self.f2 = discord.ui.TextInput(label="Akun Yang Dicari", placeholder="Contoh: Akun Sultan, Korblox", required=True)
                self.f3 = discord.ui.TextInput(label="Budget", placeholder="Contoh: 1jt / QRIS", required=True)
            elif jenis == "REKBER":
                self.f1 = discord.ui.TextInput(label="Username Kamu", placeholder="Username kamu", required=True)
                self.f2 = discord.ui.TextInput(label="Barang / Jasa Rekber", placeholder="Contoh: Rekber Akun 500k", required=True)
                self.f3 = discord.ui.TextInput(label="Username Lawan Transaksi", placeholder="@ lawan transaksi kamu", required=True)
            elif jenis in ["OTHER", "VIA KOMUNITAS", "ROBLOX PLUSS"]:
                self.f1 = discord.ui.TextInput(label="Username Roblox", placeholder="Username kamu", required=True)
                self.f2 = discord.ui.TextInput(label="Keperluan", placeholder="Jelasin mau apa", style=discord.TextStyle.paragraph, required=True)
                self.f3 = discord.ui.TextInput(label="Metode Pembayaran", placeholder="QRIS / DANA", required=True, default="QRIS")
            else:
                self.f1 = discord.ui.TextInput(label="Nickname Roblox", placeholder="Nickname Roblox kamu", required=True)
                self.f2 = discord.ui.TextInput(label="Username", placeholder="Username Roblox", required=True)
                self.f3 = discord.ui.TextInput(label="Paket yang dipilih", placeholder="Contoh: 500 Robux", required=True)
            self.add_item(self.f1)
            self.add_item(self.f2)
            self.add_item(self.f3)
            if jenis in ["VIA SEND", "VIA LOGIN", "VIA KOMUNITAS"]:
                self.promo = discord.ui.TextInput(label="Kode Promo (Opsional)", placeholder="Kosongin aja kalau gak ada", required=False)
                self.add_item(self.promo)
            else:
                self.promo = None
        except Exception as e:
            print(f"modal init error: {e}")
            self.promo = None
    async def on_submit(self, interaction: discord.Interaction):
        try:
            global ticket_counter
            ticket_counter += 1
            guild = interaction.guild
            overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False), interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True), guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
            category = get_ticket_category(guild)
            prefix = self.jenis.lower().replace(" ", "-").replace("/", "-")
            channel = await guild.create_text_channel(name=f"{prefix}-{ticket_counter}-{interaction.user.name}", overwrites=overwrites, category=category)
            paket_text = f"{self.jenis} - {self.f2.value}"
            harga_akhir = 0
            kategori = jenis_to_kategori(self.jenis)
            if self.jenis in ["VIA SEND", "VIA LOGIN", "VIA KOMUNITAS"]:
                m_temp = re.search(r'(\d+)', str(self.f3.value).replace('.', ''))
                jumlah_int = int(m_temp.group(1)) if m_temp else 500
                harga_awal = get_harga(jumlah_int, kategori)
                kode_input = self.promo.value.strip() if self.promo and self.promo.value else ""
                harga_akhir, diskon, err_promo = cek_promo(kode_input, harga_awal, jumlah_int)
                if kode_input and not err_promo and diskon > 0:
                    pdata = load_promo()
                    k_up = kode_input.upper()
                    if k_up in pdata:
                        pdata[k_up]["dipakai"] = pdata[k_up].get("dipakai", 0) + 1
                        save_promo(pdata)
            ticket_data[channel.id] = {"user_id": interaction.user.id, "username": interaction.user.name, "nickname": self.f1.value, "roblox_username": self.f1.value, "pembayaran": "QRIS", "created_at": time.time(), "last_activity": time.time(), "number": ticket_counter, "paket": paket_text, "promo": (self.promo.value if self.promo else ""), "harga_akhir": harga_akhir, "kategori": kategori}
            embed = discord.Embed(title=f"Ticket Baru - {self.jenis} - {interaction.user.name}", description=f"**Jenis:** {self.jenis}\n**Data 1:** {self.f1.value}\n**Data 2:** {self.f2.value}\n**Data 3:** {self.f3.value}\n" + (f"**Promo:** {self.promo.value}\n" if self.promo and self.promo.value else "") + f"\nTicket #{ticket_counter}\n\nSilahkan kirim bukti / detail disini ya 💗", color=0xff69b4)
            embed.set_image(url=WELCOME_URL)
            await channel.send(interaction.user.mention + " Halo! Selamat datang di MIPI STORE! 🌸", embed=embed, view=CloseView())
            embed_qris = discord.Embed(title="Scan QRIS Disini", description="Silahkan scan QRIS ini untuk pembayaran ya 💗", color=0xff69b4)
            embed_qris.set_image(url=QRIS_URL)
            await channel.send(embed=embed_qris)
            await channel.send("STATUS ORDER - Owner only:", view=StatusView())
            await send_status_update(guild, ticket_counter, interaction.user.name, interaction.user.id, paket_text, "Ticket Baru Dibuat", 0xff69b4)
            go_view = discord.ui.View()
            go_view.add_item(discord.ui.Button(label="BUKA TICKET SAYA", style=discord.ButtonStyle.link, url=f"https://discord.com/channels/{guild.id}/{channel.id}", emoji="🚀"))
            await interaction.response.send_message(f"Ticket **{self.jenis}** kamu sudah dibuat!\nPencet tombol dibawah 👇\n{channel.mention}", view=go_view, ephemeral=True)
            try:
                await interaction.user.send(f"Ticket MIPI STORE kamu sudah dibuat!\nJenis: {self.jenis}\nData: {self.f1.value} | {self.f2.value}\nLink: https://discord.com/channels/{guild.id}/{channel.id}\n\nKirim bukti QRIS kamu disana ya 💗")
            except:
                pass
        except Exception as e:
            print(f"modal submit error: {e}")
            traceback.print_exc()
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"❌ Gagal buat ticket: {e}", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ Gagal buat ticket: {e}", ephemeral=True)
            except:
                pass
    async def on_error(self, interaction, error):
        print(f"modal on_error: {error}")
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Error modal: {error}", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Error modal: {error}", ephemeral=True)
        except:
            pass

# === TOMBOL - RAPET DIJAMIN - EMOJI TETEP LAMA ===
class ButtonTicket(discord.ui.Button):
    def __init__(self, label, custom_id, row, emoji):
        super().__init__(label=label, style=discord.ButtonStyle.primary, custom_id=custom_id, row=row, emoji=emoji)
        self.jenis_map = {"t_via_send": "VIA SEND", "t_via_login": "VIA LOGIN", "t_beli_limited": "BELI LIMITED", "t_jual_limited": "JUAL LIMITED", "t_pluss": "ROBLOX PLUSS", "t_offsale": "BELI ITEM OFFSALE", "t_rekber": "REKBER", "t_other": "OTHER", "t_komunitas": "VIA KOMUNITAS", "t_beli_akun": "BELI AKUN"}
    async def callback(self, interaction: discord.Interaction):
        try:
            view = TicketTypeView()
            if not await view.cek_store(interaction):
                return
            await interaction.response.send_modal(OrderModalBaru(self.jenis_map[self.custom_id]))
        except Exception as e:
            print(f"ButtonTicket callback error: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)
            except:
                pass

class TicketTypeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ButtonTicket("Robux Via Username", "t_via_send", row=0, emoji="<a:robux:1563387482182254725>"))
        self.add_item(ButtonTicket("Robux Vlog", "t_via_login", row=0, emoji="<:emoji_10:1431192496876027975>"))
        self.add_item(ButtonTicket("Beli Limited Item", "t_beli_limited", row=1, emoji="<a:diamond:1516624681585869041>"))
        self.add_item(ButtonTicket("Jual Limited Item", "t_jual_limited", row=1, emoji="<a:moneybag:1512329138172596265>"))
        self.add_item(ButtonTicket("Beli Roblox Plus", "t_pluss", row=2, emoji="<:b_RobloxPlus:1499160341983006730>"))
        self.add_item(ButtonTicket("Beli Item Offsale", "t_offsale", row=2, emoji="<a:emoji_20:1550165111333986354>"))
        self.add_item(ButtonTicket("Rekber/MM", "t_rekber", row=3, emoji="<a:emoji_39:1555770513907916822>"))
        self.add_item(ButtonTicket("Other/Nanya", "t_other", row=3, emoji="<a:b_bluequestion:1345684551502008340>"))
        self.add_item(ButtonTicket("Via Komunitas", "t_komunitas", row=4, emoji="<a:rbx:1530537752729223308>"))
        self.add_item(ButtonTicket("Beli Akun", "t_beli_akun", row=4, emoji="<a:star_purple:1303353812374913035>"))
    async def cek_store(self, interaction):
        try:
            if STORE_STATUS == "break":
                embed = discord.Embed(color=0xfee75c)
                embed.description = "MIPI STORE LAGI BREAK! ☕\n\nMimin break sebentar yaa, 15-30 menit aja!"
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return False
            if STORE_STATUS == "closed":
                embed = discord.Embed(color=0xff0000)
                embed.description = "MIPI STORE UDAH TUTUP! 💤\n\nBalik besok yaa!"
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return False
            return True
        except Exception as e:
            print(f"cek_store error: {e}")
            return False

OrderView = TicketTypeView

@bot.event
async def on_message(message):
    try:
        if message.author.bot:
            return
        if message.guild and "market" in message.channel.name.lower():
            if message.author.id != message.guild.owner_id and not message.author.guild_permissions.administrator:
                if is_banned_selling(message.content):
                    try:
                        await message.delete()
                    except:
                        pass
                    embed = discord.Embed(title="Stickied Message:", description="DILARANG MENJUAL PRODUK YANG KAMI JUAL SEPERTI ROBUX DAN LIMITED ITEM", color=0xff0000)
                    warn = await message.channel.send(message.author.mention, embed=embed)
                    await asyncio.sleep(10)
                    try:
                        await warn.delete()
                    except:
                        pass
                    try:
                        await message.author.send("Pesan kamu di #" + message.channel.name + " dihapus!\n\nAlasan: Dilarang menjual produk yang kami jual seperti Robux dan Limited Item di MIPI STORE!")
                    except:
                        pass
                    return
        if message.channel.id in ticket_data:
            ticket_data[message.channel.id]["last_activity"] = time.time()
        await bot.process_commands(message)
    except Exception as e:
        print(f"on_message error: {e}")

@bot.event
async def on_ready():
    try:
        print(f"Login {bot.user}")
        bot.add_view(OrderView())
        bot.add_view(TicketTypeView())
        bot.add_view(CloseView())
        bot.add_view(StatusView())
        bot.add_view(RatingView(0))
        bot.add_view(SaldoView())
        bot.add_view(GiveawayView("dummy"))
        for oid in load_pending().keys():
            try:
                bot.add_view(KonfirmasiSaldoView(oid))
            except:
                pass
        if not check_inactive.is_running():
            check_inactive.start()
        if not auto_update_top_sultan.is_running():
            auto_update_top_sultan.start()
        for g in bot.guilds:
            try:
                await update_top_sultan(g)
            except:
                pass
        try:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} commands")
        except Exception as e:
            print(f"Sync error: {e}")
    except Exception as e:
        print(f"on_ready error: {e}")
        traceback.print_exc()

PANEL_FILE = "panel.json"
def load_panel():
    try:
        with open(PANEL_FILE, "r") as f:
            return json.load(f)
    except:
        return {}
def save_panel(d):
    try:
        with open(PANEL_FILE, "w") as f:
            json.dump(d, f, indent=2)
    except Exception as e:
        print(f"save panel error: {e}")

async def update_all_panels(guild):
    try:
        panels = load_panel()
        for key, info in list(panels.items()):
            try:
                ch = guild.get_channel(int(info["channel_id"]))
                if not ch:
                    continue
                msg = await ch.fetch_message(int(info["message_id"]))
                if key == "ticket":
                    await msg.edit(embed=build_ticket_panel_baru_embed(), view=TicketTypeView())
                elif key == "pricelist":
                    await msg.edit(embeds=build_all_pricelist_embeds())
            except Exception as e:
                print(f"update panel {key} error: {e}")
    except Exception as e:
        print(f"update_all_panels error: {e}")

# ================= SLASH COMMANDS - SEMUA UDAH ANTI ERROR =================
@bot.tree.command(name="ticket", description="Tampilkan panel order MIPI STORE")
async def ticket(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=False)
    try:
        if STORE_STATUS != "open":
            st = "BREAK - Mimin break 15-30 menit!" if STORE_STATUS == "break" else "CLOSED - Toko tutup, balik besok yaa!"
            await safe_followup(interaction, content=st + "\n\nTicket lagi dikunci sementara! Tunggu OPEN lagi yaa! 💗", ephemeral=True)
            return
        panels = load_panel()
        if "ticket" in panels:
            try:
                ch = interaction.guild.get_channel(int(panels["ticket"]["channel_id"]))
                msg = await ch.fetch_message(int(panels["ticket"]["message_id"]))
                await msg.edit(embed=build_ticket_panel_baru_embed(), view=TicketTypeView())
                await safe_followup(interaction, content=f"✅ Panel udah di-update jadi 10 tombol baru! Cek {ch.mention}", ephemeral=True)
                return
            except Exception as e:
                print(f"edit old panel gagal, kirim baru: {e}")
        msg = await safe_followup(interaction, embed=build_ticket_panel_baru_embed(), view=TicketTypeView())
        if msg:
            try:
                panels["ticket"] = {"channel_id": str(msg.channel.id), "message_id": str(msg.id)}
                save_panel(panels)
            except:
                pass
    except Exception as e:
        print(f"ERROR /ticket: {e}")
        traceback.print_exc()
        await safe_followup(interaction, content=f"❌ Error /ticket: {e}", ephemeral=True)

@bot.tree.command(name="setup-ticket", description="Kirim panel ticket order (Owner only)")
async def setup_ticket(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=True)
    try:
        if interaction.user.id != interaction.guild.owner_id:
            await safe_followup(interaction, content="Hanya Owner!", ephemeral=True)
            return
        await safe_followup(interaction, embed=build_ticket_panel_baru_embed(), view=TicketTypeView())
    except Exception as e:
        print(f"ERROR /setup-ticket: {e}")
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="open", description="Buka toko")
async def open_cmd(interaction: discord.Interaction):
    global STORE_STATUS
    await safe_defer(interaction, ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user, interaction.guild):
            await safe_followup(interaction, content="Cuma admin!", ephemeral=True)
            return
        STORE_STATUS = "open"
        await safe_followup(interaction, content="✅ Mipi Store **DIBUKA**! Ticket bisa dipencet lagi!")
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="break", description="Toko break sebentar")
async def break_cmd(interaction: discord.Interaction):
    global STORE_STATUS
    await safe_defer(interaction, ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user, interaction.guild):
            await safe_followup(interaction, content="Cuma admin!", ephemeral=True)
            return
        STORE_STATUS = "break"
        await safe_followup(interaction, content="☕ Mipi Store **BREAK** 15-30 menit! Ticket dikunci sementara!")
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="close", description="Tutup toko")
async def close_cmd(interaction: discord.Interaction):
    global STORE_STATUS
    await safe_defer(interaction, ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user, interaction.guild):
            await safe_followup(interaction, content="Cuma admin!", ephemeral=True)
            return
        STORE_STATUS = "closed"
        await safe_followup(interaction, content="💤 Mipi Store **TUTUP**! Balik besok yaa!")
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="close-ticket", description="Tutup ticket ini")
async def close_ticket_cmd(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user, interaction.guild):
            await safe_followup(interaction, content="Hanya Admin / Owner!", ephemeral=True)
            return
        data = ticket_data.get(interaction.channel.id)
        if not data:
            await safe_followup(interaction, content="Ini bukan channel ticket!", ephemeral=True)
            return
        await safe_followup(interaction, content="Ticket ditutup oleh " + interaction.user.mention + ". Membuat transcript...")
        await do_auto_close(interaction.guild, interaction.channel, data, reason="closed by owner", admin_user=interaction.user)
    except Exception as e:
        print(f"close-ticket error: {e}")
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

# ----- PRICELIST -----
@bot.tree.command(name="pricelist", description="Lihat semua pricelist + gambarnya")
async def pricelist_cmd(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=False)
    try:
        await safe_followup(interaction, embeds=build_all_pricelist_embeds())
    except Exception as e:
        print(f"ERROR /pricelist: {e}")
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="setup-pricelist", description="Kirim panel pricelist lengkap + gambar (Owner)")
async def setup_pricelist(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=True)
    try:
        if interaction.user.id != interaction.guild.owner_id:
            await safe_followup(interaction, content="Hanya Owner!", ephemeral=True)
            return
        msg = await interaction.channel.send(embeds=build_all_pricelist_embeds())
        panels = load_panel()
        panels["pricelist"] = {"channel_id": str(msg.channel.id), "message_id": str(msg.id)}
        save_panel(panels)
        await safe_followup(interaction, content=f"✅ Panel pricelist udah dikirim ke {interaction.channel.mention}!", ephemeral=True)
    except Exception as e:
        print(f"setup-pricelist error: {e}")
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="pricelist-visend", description="Lihat pricelist Robux Via Username")
async def pricelist_visend(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=False)
    try:
        await safe_followup(interaction, embed=build_pricelist_embed("via_username"))
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="pricelist-vilog", description="Lihat pricelist Robux Vlog / Via Login")
async def pricelist_vilog(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=False)
    try:
        await safe_followup(interaction, embed=build_pricelist_embed("via_login"))
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="pricelist-via-komunitas", description="Lihat pricelist Robux Via Komunitas")
async def pricelist_komunitas(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=False)
    try:
        await safe_followup(interaction, embed=build_pricelist_embed("via_komunitas"))
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="pricelist-plus", description="Lihat pricelist Roblox Plus")
async def pricelist_plus(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=False)
    try:
        await safe_followup(interaction, embed=build_pricelist_embed("plus"))
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="pricelist-limited", description="Lihat pricelist Item Limited")
async def pricelist_limited(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=False)
    try:
        await safe_followup(interaction, embed=build_pricelist_embed("limited"))
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="pricelist-pay", description="Lihat cara pembayaran / QRIS Mipi Store")
async def pricelist_pay(interaction: discord.Interaction):
    # INI YANG KEMARIN ERROR - UDAH DIPERBAIKI PAKE safe_defer
    await safe_defer(interaction, ephemeral=False)
    try:
        e = discord.Embed(title="💳 PEMBAYARAN - MIPI STORE", description="**Cara Bayar:**\n\n1. Order dulu lewat tombol di #ticket\n2. Scan QRIS di bawah ini\n3. Kirim bukti di ticket kamu\n4. Tunggu admin konfirmasi\n\n**Yang diterima:**\n• QRIS (DANA / GOPAY / OVO / ShopeePay / dll)\n• DANA\n• GOPAY\n\n⚠️ **JANGAN transfer ke selain QRIS ini!**", color=0xff69b4)
        e.set_image(url=QRIS_URL)
        e.set_footer(text="Mipi Store - Rafi Store | Pembayaran hanya QRIS")
        await safe_followup(interaction, embed=e)
    except Exception as e:
        print(f"ERROR /pricelist-pay: {e}")
        traceback.print_exc()
        await safe_followup(interaction, content=f"❌ Error pricelist-pay: {e}", ephemeral=True)

@bot.tree.command(name="pricelist-top-sultan", description="Lihat Top Sultan Mipi Store")
async def pricelist_top_sultan(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=False)
    try:
        await safe_followup(interaction, embed=build_top_sultan_embed_semua())
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

# ----- EDIT HARGA PER KATEGORI -----
class EditHargaModal(discord.ui.Modal, title="Ubah Harga"):
    def __init__(self, robux_lama, kategori):
        super().__init__()
        self.robux_lama = robux_lama
        self.kategori = kategori
        self.harga_input = discord.ui.TextInput(label=f"Harga Baru [{kategori}] {robux_lama} Robux", placeholder="Contoh: 80000", required=True)
        self.add_item(self.harga_input)
    async def on_submit(self, interaction: discord.Interaction):
        try:
            harga_baru = int(self.harga_input.value.replace(".", "").replace(",", "").replace("Rp", "").strip())
            data = load_pricelist(self.kategori)
            data[self.robux_lama] = harga_baru
            save_pricelist(data, self.kategori)
            await update_all_panels(interaction.guild)
            await interaction.response.send_message(f"✅ BERHASIL!\n[{self.kategori}] {self.robux_lama} Robux ➡️ {format_rp(harga_baru)}\nYang lain GAK KEUBAH! Cuma {self.kategori} doang!", ephemeral=True)
        except Exception as e:
            try:
                await interaction.response.send_message(f"❌ Harga harus angka! Contoh: 80000\nError: {e}", ephemeral=True)
            except:
                pass
    async def on_error(self, interaction, error):
        print(f"EditHargaModal error: {error}")

class TambahPaketModal(discord.ui.Modal, title="Tambah Paket Baru"):
    def __init__(self, kategori):
        super().__init__()
        self.kategori = kategori
        self.robux_input = discord.ui.TextInput(label="Jumlah Robux", placeholder="Contoh: 600", required=True)
        self.harga_input = discord.ui.TextInput(label="Harga", placeholder="Contoh: 90000", required=True)
        self.add_item(self.robux_input)
        self.add_item(self.harga_input)
    async def on_submit(self, interaction: discord.Interaction):
        try:
            rbx = int(self.robux_input.value.strip())
            harga = int(self.harga_input.value.replace(".", "").replace("Rp", "").strip())
            data = load_pricelist(self.kategori)
            data[rbx] = harga
            save_pricelist(data, self.kategori)
            await update_all_panels(interaction.guild)
            await interaction.response.send_message(f"✅ Paket baru ditambah!\n[{self.kategori}] {rbx} Robux = {format_rp(harga)}", ephemeral=True)
        except Exception as e:
            try:
                await interaction.response.send_message(f"❌ Harus angka semua! Error: {e}", ephemeral=True)
            except:
                pass

class PricelistEditView(discord.ui.View):
    def __init__(self, kategori="via_username"):
        super().__init__(timeout=None)
        self.kategori = kategori
        try:
            data = load_pricelist(kategori)
            options = []
            for rbx in sorted(data.keys()):
                options.append(discord.SelectOption(label=f"{rbx} Robux - {format_rp(data[rbx])}", value=str(rbx)))
            select = discord.ui.Select(placeholder=f"Pilih paket [{kategori}] yang mau diubah...", options=options[:25], custom_id="pilih_paket_edit")
            select.callback = self.pilih_paket
            self.add_item(select)
        except Exception as e:
            print(f"PricelistEditView init error: {e}")
    async def pilih_paket(self, interaction: discord.Interaction):
        try:
            if interaction.user.id != interaction.guild.owner_id:
                await interaction.response.send_message("Hanya Owner!", ephemeral=True)
                return
            await interaction.response.send_modal(EditHargaModal(int(interaction.data["values"][0]), self.kategori))
        except Exception as e:
            print(f"pilih paket error: {e}")
    @discord.ui.button(label="➕ Tambah Paket Baru", style=discord.ButtonStyle.success, custom_id="tambah_paket_btn")
    async def tambah_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != interaction.guild.owner_id:
                await interaction.response.send_message("Hanya Owner!", ephemeral=True)
                return
            await interaction.response.send_modal(TambahPaketModal(self.kategori))
        except Exception as e:
            print(f"tambah btn error: {e}")
    @discord.ui.button(label="👀 Lihat Pricelist Ini", style=discord.ButtonStyle.primary, custom_id="lihat_pricelist_btn")
    async def lihat_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_message(embed=build_pricelist_embed(self.kategori), ephemeral=True)
        except Exception as e:
            print(f"lihat btn error: {e}")

class PricelistKategoriSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Via Username", style=discord.ButtonStyle.primary, custom_id="edit_via_username")
    async def b1(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_message(embed=discord.Embed(title="✏️ EDIT - VIA USERNAME", description=build_pricelist_text("via_username"), color=0xff69b4), view=PricelistEditView("via_username"), ephemeral=True)
        except Exception as e:
            print(f"b1 error: {e}")
    @discord.ui.button(label="Via Login / Vlog", style=discord.ButtonStyle.primary, custom_id="edit_via_login")
    async def b2(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_message(embed=discord.Embed(title="✏️ EDIT - VIA LOGIN", description=build_pricelist_text("via_login"), color=0xff69b4), view=PricelistEditView("via_login"), ephemeral=True)
        except Exception as e:
            print(f"b2 error: {e}")
    @discord.ui.button(label="Via Komunitas", style=discord.ButtonStyle.primary, custom_id="edit_via_komunitas")
    async def b3(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_message(embed=discord.Embed(title="✏️ EDIT - VIA KOMUNITAS", description=build_pricelist_text("via_komunitas"), color=0xff69b4), view=PricelistEditView("via_komunitas"), ephemeral=True)
        except Exception as e:
            print(f"b3 error: {e}")
    @discord.ui.button(label="Plus", style=discord.ButtonStyle.primary, custom_id="edit_plus")
    async def b4(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_message(embed=discord.Embed(title="✏️ EDIT - PLUS", description=build_pricelist_text("plus"), color=0xff69b4), view=PricelistEditView("plus"), ephemeral=True)
        except Exception as e:
            print(f"b4 error: {e}")
    @discord.ui.button(label="Limited", style=discord.ButtonStyle.primary, custom_id="edit_limited")
    async def b5(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_message(embed=discord.Embed(title="✏️ EDIT - LIMITED", description=build_pricelist_text("limited"), color=0xff69b4), view=PricelistEditView("limited"), ephemeral=True)
        except Exception as e:
            print(f"b5 error: {e}")

@bot.tree.command(name="edit-pricelist", description="Edit pricelist per kategori (Owner)")
async def edit_pricelist(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=True)
    try:
        if interaction.user.id != interaction.guild.owner_id:
            await safe_followup(interaction, content="Hanya Owner!", ephemeral=True)
            return
        embed = discord.Embed(title="✏️ EDIT PRICELIST - PILIH KATEGORI DULU!", description="Sekarang udah beda-beda!\n\nPencet dulu mau ngedit yang mana:\n• Via Username\n• Via Login / Vlog\n• Via Komunitas\n• Plus\n• Limited\n\nGanti 1 kategori, yang lain GAK KEUBAH!", color=0xff69b4)
        await safe_followup(interaction, embed=embed, view=PricelistKategoriSelectView(), ephemeral=True)
    except Exception as e:
        print(f"ERROR /edit-pricelist: {e}")
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="set-harga", description="Ubah harga per kategori (Owner)")
async def set_harga(interaction: discord.Interaction, kategori: str, robux: int, harga_baru: int):
    await safe_defer(interaction, ephemeral=True)
    try:
        if interaction.user.id != interaction.guild.owner_id:
            await safe_followup(interaction, content="Hanya Owner!", ephemeral=True)
            return
        kategori = kategori.lower().replace(" ", "_")
        if kategori not in ["via_username", "via_login", "via_komunitas", "plus", "limited"]:
            await safe_followup(interaction, content="Kategori harus: via_username / via_login / via_komunitas / plus / limited", ephemeral=True)
            return
        data = load_pricelist(kategori)
        hl = data.get(robux, 0)
        data[robux] = harga_baru
        save_pricelist(data, kategori)
        await update_all_panels(interaction.guild)
        await safe_followup(interaction, content=f"✅ Harga berubah!\n[{kategori}] {robux} Robux: {format_rp(hl)} ➡️ {format_rp(harga_baru)}\nKategori lain GAK KEUBAH!")
    except Exception as e:
        print(f"set-harga error: {e}")
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="tambah-harga", description="Tambah paket per kategori (Owner)")
async def tambah_harga(interaction: discord.Interaction, kategori: str, robux: int, harga: int):
    await safe_defer(interaction, ephemeral=True)
    try:
        if interaction.user.id != interaction.guild.owner_id:
            await safe_followup(interaction, content="Hanya Owner!", ephemeral=True)
            return
        kategori = kategori.lower().replace(" ", "_")
        if kategori not in ["via_username", "via_login", "via_komunitas", "plus", "limited"]:
            await safe_followup(interaction, content="Kategori harus: via_username / via_login / via_komunitas / plus / limited", ephemeral=True)
            return
        data = load_pricelist(kategori)
        data[robux] = harga
        save_pricelist(data, kategori)
        await update_all_panels(interaction.guild)
        await safe_followup(interaction, content=f"✅ Paket baru ditambah!\n[{kategori}] {robux} = {format_rp(harga)}")
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="hapus-harga", description="Hapus paket per kategori (Owner)")
async def hapus_harga(interaction: discord.Interaction, kategori: str, robux: int):
    await safe_defer(interaction, ephemeral=True)
    try:
        if interaction.user.id != interaction.guild.owner_id:
            await safe_followup(interaction, content="Hanya Owner!", ephemeral=True)
            return
        kategori = kategori.lower().replace(" ", "_")
        data = load_pricelist(kategori)
        if robux not in data:
            await safe_followup(interaction, content="Paket ga ketemu di kategori itu!", ephemeral=True)
            return
        del data[robux]
        save_pricelist(data, kategori)
        await update_all_panels(interaction.guild)
        await safe_followup(interaction, content=f"✅ [{kategori}] {robux} Robux udah dihapus!")
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="lihat-harga", description="Lihat semua pricelist (udah beda-beda)")
async def lihat_harga(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=True)
    try:
        await safe_followup(interaction, embeds=build_all_pricelist_embeds(), ephemeral=True)
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="leaderboard", description="Lihat Top Sultan BULAN INI")
async def leaderboard(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=False)
    try:
        await safe_followup(interaction, embed=build_top_sultan_embed_bulanan())
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="leaderboard-bulanan", description="Lihat Top Sultan BULAN INI")
async def leaderboard_bulanan(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=False)
    try:
        await safe_followup(interaction, embed=build_top_sultan_embed_bulanan())
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="leaderboard-semua", description="Lihat Top Sultan SEMUA / ALL TIME")
async def leaderboard_semua(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=False)
    try:
        await safe_followup(interaction, embed=build_top_sultan_embed_semua())
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="top-sultan", description="Lihat Top Sultan SEMUA / ALL TIME")
async def top_sultan_cmd(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=False)
    try:
        await safe_followup(interaction, embed=build_top_sultan_embed_semua())
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="setup-top-sultan", description="Bikin channel top-sultan auto-update (Owner)")
async def setup_top_sultan(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=True)
    try:
        if interaction.user.id != interaction.guild.owner_id:
            await safe_followup(interaction, content="Hanya Owner!", ephemeral=True)
            return
        guild = interaction.guild
        ch = get_top_sultan_channel(guild)
        if not ch:
            ch = await guild.create_text_channel("🏆┆・top-sultan")
        await ch.set_permissions(guild.default_role, view_channel=True, send_messages=False, add_reactions=False)
        await update_top_sultan(guild)
        await safe_followup(interaction, content=f"✅ Channel Top Sultan auto-update udah jadi! {ch.mention}", ephemeral=True)
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="saldo", description="Cek total belanja kamu")
async def saldo_slash(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=True)
    try:
        tr, tro, tt = get_total_belanja(interaction.user.id)
        embed = discord.Embed(color=0xff1493)
        embed.description = "INFORMASI SALDO / TOTAL TRANSAKSI\n\nHalo " + interaction.user.mention + ",\n\nTotal Belanja: " + format_rp(tr) + "\nTotal Robux: " + str(tro) + " R$\nTotal Transaksi: " + str(tt) + "x\n\nMIPI STORE - CHECK SALDO"
        embed.set_footer(text="Mipi Store - Rafi Store")
        await safe_followup(interaction, embed=embed, ephemeral=True)
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.command(name="saldo")
async def saldo_prefix(ctx):
    try:
        tr, tro, tt = get_total_belanja(ctx.author.id)
        embed = discord.Embed(color=0xff1493)
        embed.description = "INFORMASI SALDO / TOTAL TRANSAKSI\n\nHalo " + ctx.author.mention + ",\n\nTotal Belanja: " + format_rp(tr) + "\nTotal Robux: " + str(tro) + " R$\nTotal Transaksi: " + str(tt) + "x"
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"saldo prefix error: {e}")

@bot.tree.command(name="setup-saldo", description="Kirim panel cek saldo (Owner only)")
async def setup_saldo(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=True)
    try:
        if interaction.user.id != interaction.guild.owner_id:
            await safe_followup(interaction, content="Hanya Owner!", ephemeral=True)
            return
        embed = discord.Embed(title="CEK SALDO - MIPI STORE", description="MAU TAU UDAH HABIS BERAPA DI MIPI STORE?\n\nPencet tombol CEK SALDO SAYA dibawah ini!", color=0xff69b4)
        await safe_followup(interaction, embed=embed, view=SaldoView())
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="add-saldo", description="Tambah saldo manual (Admin / Owner)")
async def add_saldo(interaction: discord.Interaction, user: discord.User, robux: int, kategori: str = "via_username"):
    await safe_defer(interaction, ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user, interaction.guild):
            await safe_followup(interaction, content="Hanya Admin / Owner!", ephemeral=True)
            return
        if robux <= 0:
            await safe_followup(interaction, content="Jumlah Robux harus lebih dari 0!", ephemeral=True)
            return
        kategori = kategori.lower().replace(" ", "_")
        if kategori not in ["via_username", "via_login", "via_komunitas", "plus", "limited"]:
            kategori = "via_username"
        harga = get_harga(robux, kategori)
        add_to_leaderboard(user.id, user.name, f"{robux} Robux", kategori=kategori)
        await safe_followup(interaction, content=f"✅ Saldo ditambah!\nBuyer: {user.mention}\n+{robux} R$ ({format_rp(harga)}) [{kategori}]")
        try:
            await update_top_sultan(interaction.guild)
        except:
            pass
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

# ================= PROMO COMMANDS =================
@bot.tree.command(name="buat-promo", description="Buat kode promo (Owner)")
async def buat_promo(interaction: discord.Interaction, kode: str, diskon: int, tipe: str = "persen", max_pakai: int = 10):
    await safe_defer(interaction, ephemeral=True)
    try:
        if interaction.user.id != interaction.guild.owner_id:
            await safe_followup(interaction, content="Hanya Owner!", ephemeral=True)
            return
        data = load_promo()
        data[kode.upper()] = {"diskon": diskon, "tipe": tipe, "max": max_pakai, "dipakai": 0}
        save_promo(data)
        await safe_followup(interaction, content=f"✅ Promo dibuat!\nKode: `{kode.upper()}`\nDiskon: {diskon} {tipe}\nMax: {max_pakai}x\nMin: 500 Robux")
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="hapus-promo", description="Hapus kode promo (Owner)")
async def hapus_promo(interaction: discord.Interaction, kode: str):
    await safe_defer(interaction, ephemeral=True)
    try:
        if interaction.user.id != interaction.guild.owner_id:
            await safe_followup(interaction, content="Hanya Owner!", ephemeral=True)
            return
        data = load_promo()
        if kode.upper() not in data:
            await safe_followup(interaction, content="Promo ga ketemu!", ephemeral=True)
            return
        del data[kode.upper()]
        save_promo(data)
        await safe_followup(interaction, content=f"✅ Promo `{kode.upper()}` dihapus!")
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="list-promo", description="Lihat semua promo (Owner)")
async def list_promo(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=True)
    try:
        if interaction.user.id != interaction.guild.owner_id:
            await safe_followup(interaction, content="Hanya Owner!", ephemeral=True)
            return
        data = load_promo()
        if not data:
            await safe_followup(interaction, content="Belum ada promo!", ephemeral=True)
            return
        txt = "🎁 **LIST PROMO**\n\n"
        for k, v in data.items():
            txt += f"`{k}` - {v['diskon']} {v['tipe']} - Dipakai {v.get('dipakai',0)}/{v.get('max',999)}\n"
        await safe_followup(interaction, content=txt, ephemeral=True)
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

@bot.tree.command(name="giveaway", description="Buat giveaway (Owner)")
async def giveaway_cmd(interaction: discord.Interaction, hadiah: str, pemenang: int = 1, durasi_menit: int = 60):
    await safe_defer(interaction, ephemeral=False)
    try:
        if interaction.user.id != interaction.guild.owner_id:
            await safe_followup(interaction, content="Hanya Owner!", ephemeral=True)
            return
        gid = f"gw-{int(time.time())}"
        giveaway_data[gid] = {"hadiah": hadiah, "pemenang": pemenang, "peserta": [], "ended": False, "host_mention": interaction.user.mention}
        embed = discord.Embed(title="🎉 GIVEAWAY MIPI STORE 🎉", description=f"Hadiah: {hadiah}\nHost: {interaction.user.mention}\nPeserta: 0 orang\n\nPencet JOIN dibawah!", color=0xff69b4)
        msg = await safe_followup(interaction, embed=embed, view=GiveawayView(gid))
        if msg:
            try:
                asyncio.create_task(_end_giveaway_delayed(interaction.guild, interaction.channel.id, msg.id, gid, durasi_menit))
            except:
                pass
            await safe_followup(interaction, content=f"✅ Giveaway dibuat! Berakhir dalam {durasi_menit} menit.", ephemeral=True)
    except Exception as e:
        print(f"giveaway error: {e}")
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

async def _end_giveaway_delayed(guild, channel_id, message_id, gid, menit):
    try:
        await asyncio.sleep(menit * 60)
        await end_giveaway(guild, channel_id, message_id, gid)
    except Exception as e:
        print(f"delayed giveaway error: {e}")

@bot.tree.command(name="cek-bot", description="Cek bot masih hidup / versi kode")
async def cek_bot(interaction: discord.Interaction):
    await safe_defer(interaction, ephemeral=True)
    try:
        # Ini buat buktiin kode baru udah ke-deploy atau belum
        # Kalo muncul VERSI 1000, berarti kode baru udah jalan. Kalo gak muncul, berarti masih kode lama!
        await safe_followup(interaction, content=f"✅ BOT HIDUP! VERSI 1000 - FIX ALL SYSTEM\nHarga Via Username 100 = {format_rp(get_harga(100, 'via_username'))}\nHarga Via Login 100 = {format_rp(get_harga(100, 'via_login'))}\nHarga Via Komunitas 100 = {format_rp(get_harga(100, 'via_komunitas'))}\n\nKalo harga di atas udah beda-beda (16k / 18k / 14k), berarti kode baru UDAH KE-DEPLOY! 🎉", ephemeral=True)
    except Exception as e:
        await safe_followup(interaction, content=f"❌ Error: {e}", ephemeral=True)

bot.run(os.getenv("TOKEN"))
