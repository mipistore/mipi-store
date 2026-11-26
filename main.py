# ============================================================================
# MIPI STORE V4 - SUPER STORE - BAGIAN 1 / 2 - 2K BARIS
# "WOW MIPI STORE SEKARANG JADI CANGGIH BANGET, BAHKAN STORE BESAR SAJA KALAH"
# ============================================================================
# SISTEM BARU DI V4:
# 1. Auto Role Sultan / VIP - Otomatis naik role kalo belanja banyak
# 2. Referral - Ajak temen = 5% komisi otomatis
# 3. Voucher - Redeem kode dapet diskon
# 4. Daily Reward - Claim tiap hari dapet poin
# 5. Level Buyer - Newbie > Regular > VIP > Sultan > LEGEND
# 6. Anti-Scam Scanner - Hapus link phising otomatis
# 7. Auto Rekap Omset Harian - Jam 12 malem kirim ke owner
# 8. Statistik Real-Time - Omset hari / minggu / bulan
# 9. Notif Restock - Buyer di-DM kalo stok dibuka lagi
# 10. Auto Reminder Ticket - Tag admin kalo ticket sepi 10 menit
# 11. Mini Game Tebak Harga - Menang dapet voucher
# 12. Showcase Sultan - Umumumin #1 All Time otomatis
# + SEMUA SISTEM LAMA: Visend Modern, Vilog, Plus, Komunitas, Rekber Elegan,
#   Pending Anti-Tipu, Tutup/Buka Tombol, Pricelist 100-10000, Promo, Giveaway,
#   Filter Market, Transcript, Vouch, Rating, Top Sultan Bulanan + All Time
# ============================================================================
import discord
from discord.ext import commands, tasks
import os, time, io, html, re, asyncio, json, random, string, traceback
from datetime import datetime, timedelta
intents=discord.Intents.default();intents.message_content=True;intents.members=True;intents.guilds=True
bot=commands.Bot(command_prefix="!",intents=intents)
WELCOME_URL="https://raw.githubusercontent.com/mipistore/mipi-store/main/97b3c2a7-b1e8-66b1-50e5-563dc75098ea.jpeg"
THANKYOU_URL="https://raw.githubusercontent.com/mipistore/mipi-store/main/IMG_6021.jpeg"
QRIS_URL="https://raw.githubusercontent.com/mipistore/mipi-store/main/IMG_5210.jpeg"
VIA_USERNAME_URL="https://raw.githubusercontent.com/mipistore/mipi-store/main/864c8b52-4d57-770d-955f-6e16b985f6e0.jpeg"
VIA_LOGIN_URL="https://raw.githubusercontent.com/mipistore/mipi-music-bot/main/bddf1ab5-866b-c73a-2ea1-db6ed86dcc7f.jpeg"
VIA_KOMUNITAS_URL="https://raw.githubusercontent.com/mipistore/mipi-store/main/1b346831-9a9d-2db7-466e-e9428ceee394.jpeg"
PLUS_URL="https://raw.githubusercontent.com/mipistore/mipi-store/main/5b214a07-38d3-e810-d036-13d6487029de.jpeg"
LIMITED_URL="https://raw.githubusercontent.com/mipistore/mipi-store/main/3c1a8b02-4d92-ee3a-8cfd-854906585b1d.jpeg"
TOP_SULTAN_IMAGE="https://raw.githubusercontent.com/mipistore/mipi-store/main/4ee2813b-3c4b-c291-86d0-38b8fe36132d.jpeg"
ticket_data={};ticket_counter=0;user_ratings={};user_last_ticket={};STORE_STATUS="open";OPEN_CLOSE_CHANNEL_ID=1569135504262299689;OPEN_TICKET_CHANNEL_ID=1569711323653083279
# === CONFIG V4 ===
REFERRAL_RATE=0.05;DAILY_POIN=10;POIN_TO_ROBUX=100;LEVELS=[("🌱 Newbie",0),("💎 Regular",100000),("⭐ VIP",500000),("👑 Sultan",1000000),("🔥 LEGEND",5000000)]
async def safe_defer(interaction,ephemeral=False):
    try:
        if not interaction.response.is_done(): await interaction.response.defer(ephemeral=ephemeral);return True
    except Exception as e: print(f"Defer gagal: {e}")
    return False
async def safe_followup(interaction,content=None,embed=None,embeds=None,view=None,ephemeral=False):
    try:
        if interaction.response.is_done(): return await interaction.followup.send(content=content,embed=embed,embeds=embeds,view=view,ephemeral=ephemeral)
        else: return await interaction.response.send_message(content=content,embed=embed,embeds=embeds,view=view,ephemeral=ephemeral)
    except Exception as e:
        print(f"Followup gagal: {e}")
        try: return await interaction.channel.send(content=content,embed=embed,embeds=embeds,view=view)
        except Exception as e2: print(f"Channel send gagal: {e2}");return None
async def safe_send(channel,content=None,embed=None,embeds=None,view=None):
    try: return await channel.send(content=content,embed=embed,embeds=embeds,view=view)
    except Exception as e: print(f"Send gagal: {e}");return None
@bot.tree.error
async def on_app_command_error(interaction,error):
    print(f"=== SLASH ERROR {interaction.command.name if interaction.command else '?'} ===");traceback.print_exception(type(error),error,error.__traceback__)
    try:
        msg=f"❌ Error: {str(error)[:400]}\nCoba lagi ya, kalo masih error SS ke owner!"
        if interaction.response.is_done(): await interaction.followup.send(msg,ephemeral=True)
        else: await interaction.response.send_message(msg,ephemeral=True)
    except:
        try: await interaction.channel.send(f"❌ Error di {interaction.command.name if interaction.command else 'command'}: {error}")
        except: pass
# === GENERIC JSON HELPER - RAPET ===
def _load(fn,default):
    try:
        with open(fn,"r") as f: return json.load(f)
    except: return default
def _save(fn,d):
    try:
        with open(fn,"w") as f: json.dump(d,f,indent=2)
    except Exception as e: print(f"save {fn} error: {e}")
def load_stock(): return _load("stock.json",{})
def save_stock(d): _save("stock.json",d)
def is_open(k): return load_stock().get(str(k),True)
def set_stock(k,b):
    d=load_stock();d[str(k)]=bool(b);save_stock(d);return d
def kategori_alias(k):
    k=str(k).lower().replace(" ","_").replace("-","_")
    m={"visend":"via_username","via_send":"via_username","via_username":"via_username","vilog":"via_login","via_login":"via_login","vlog":"via_login","komunitas":"via_komunitas","via_komunitas":"via_komunitas","plus":"plus","roblox_plus":"plus","roblox_pluss":"plus","pluss":"plus","limited":"limited","beli_limited":"limited","jual_limited":"limited","offsale":"limited","beli_item_offsale":"limited","rekber":"rekber","mm":"rekber","middleman":"rekber","beli_akun":"beli_akun","other":"other","nanya":"other"}
    return m.get(k,k)
# === PRICELIST ===
PRICELIST_FILE="pricelist.json"
def _harga_base(n,r): return int(n*r/100)
def _build_pricelist(rate):
    out={}
    for nominal in [100,200,300,400,500,600,700,800,900,1000,1200,1500,2000,2500,3000,4000,5000,6000,7000,8000,9000,10000]:
        h=_harga_base(nominal,rate)
        if nominal>=5000: h=int(h*0.97)
        elif nominal>=1000: h=int(h*0.98)
        h=int(round(h/500)*500);out[nominal]=h
    return out
DEFAULT_PRICELIST_PER_KATEGORI={"via_username":_build_pricelist(160),"via_login":_build_pricelist(180),"via_komunitas":_build_pricelist(140),"plus":_build_pricelist(160),"limited":_build_pricelist(160)}
DEFAULT_PRICELIST=DEFAULT_PRICELIST_PER_KATEGORI["via_username"].copy()
def _load_all_pricelist_raw():
    try:
        with open(PRICELIST_FILE,"r") as f:
            d=json.load(f)
            if isinstance(d,dict): return d
    except Exception as e: print(f"Load pricelist gagal: {e}")
    return {}
def load_pricelist(kategori="via_username"):
    try:
        raw=_load_all_pricelist_raw()
        if raw and raw.keys() and list(raw.keys())[0].isdigit():
            if kategori=="via_username":
                try: return {int(k):int(v) for k,v in raw.items()}
                except: pass
            return DEFAULT_PRICELIST_PER_KATEGORI.get(kategori,DEFAULT_PRICELIST).copy()
        if kategori in raw and isinstance(raw[kategori],dict):
            try: return {int(k):int(v) for k,v in raw[kategori].items()}
            except: pass
        return DEFAULT_PRICELIST_PER_KATEGORI.get(kategori,DEFAULT_PRICELIST).copy()
    except Exception as e: print(f"load_pricelist error: {e}");return DEFAULT_PRICELIST_PER_KATEGORI.get(kategori,DEFAULT_PRICELIST).copy()
def save_pricelist(data,kategori="via_username"):
    try:
        raw=_load_all_pricelist_raw()
        if raw and raw.keys() and list(raw.keys())[0].isdigit():
            old={}
            try: old={int(k):int(v) for k,v in raw.items()}
            except: pass
            raw={"via_username":{str(k):v for k,v in old.items()}}
            for kat in ["via_login","via_komunitas","plus","limited"]:
                if kat not in raw: raw[kat]={str(k):v for k,v in DEFAULT_PRICELIST_PER_KATEGORI[kat].items()}
        if not raw:
            for kat in ["via_username","via_login","via_komunitas","plus","limited"]: raw[kat]={str(k):v for k,v in DEFAULT_PRICELIST_PER_KATEGORI[kat].items()}
        raw[kategori]={str(k):int(v) for k,v in data.items()}
        with open(PRICELIST_FILE,"w") as f: json.dump(raw,f,indent=2)
        return True
    except Exception as e: print(f"save_pricelist error: {e}");return False
def get_harga(robux,kategori="via_username"):
    try:
        data=load_pricelist(kategori);robux=int(robux)
        if robux in data: return int(data[robux])
        rate=160
        if kategori=="via_login": rate=180
        elif kategori=="via_komunitas": rate=140
        return int(robux*rate/100)
    except Exception as e: print(f"get_harga error: {e}");return int(robux)*150
def format_rp(n):
    try: return f"Rp {int(n):,}".replace(",",".")
    except: return f"Rp {n}"
def get_level(total_rp):
    lvl="🌱 Newbie"
    for nama,min_rp in LEVELS:
        if total_rp>=min_rp: lvl=nama
    return lvl
def get_next_level(total_rp):
    for nama,min_rp in LEVELS:
        if total_rp<min_rp: return nama,min_rp-total_rp
    return "🔥 MAX LEVEL",0
# === PRICELIST TEXT MODERN ELEGAN ===
def build_pricelist_text(kategori="via_username"):
    try:
        if not is_open(kategori): return f"🔴 **{str(kategori).upper()} LAGI HABIS!**\n\nMaaf ya, stok {kategori} lagi habis / tutup sementara!\nCoba kategori lain dulu atau tunggu restock ya 💗\n\n💗 Mipi Store — Rafi Store"
        data=load_pricelist(kategori)
        def h(n):
            try: return format_rp(data.get(int(n),get_harga(n,kategori)))
            except: return format_rp(get_harga(n,kategori))
        if kategori=="via_username": return ("✨ Robux dikirim langsung ke akun kamu, tanpa login, tanpa ribet!\n💎 Aman • Cepat • Terpercaya • Garansi 100%\n\n━━━━━━━━━━━━━━━━━━\n🌸  ECERAN  —  Buat Coba-Coba\n━━━━━━━━━━━━━━━━━━\n"+f"💠  100 Robux  —  {h(100)}\n💠  200 Robux  —  {h(200)}\n💠  300 Robux  —  {h(300)}\n💠  400 Robux  —  {h(400)}\n\n━━━━━━━━━━━━━━━━━━\n💎  HEMAT  —  Paling Laris!\n━━━━━━━━━━━━━━━━━━\n"+f"✨  500 Robux  —  {h(500)}\n✨  600 Robux  —  {h(600)}\n✨  700 Robux  —  {h(700)}\n✨  800 Robux  —  {h(800)}\n✨  900 Robux  —  {h(900)}\n✨  1000 Robux  —  {h(1000)}\n\n━━━━━━━━━━━━━━━━━━\n👑  SULTAN  —  Buat Yang Mau Borong\n━━━━━━━━━━━━━━━━━━\n"+f"👑  1500 Robux  —  {h(1500)}\n👑  2000 Robux  —  {h(2000)}\n👑  3000 Robux  —  {h(3000)}\n👑  5000 Robux  —  {h(5000)}\n👑  10000 Robux  —  {h(10000)}\n\n━━━━━━━━━━━━━━━━━━\n🛍️  CARA ORDER\n━━━━━━━━━━━━━━━━━━\n"+f"1️⃣  Klik tombol ORDER di <#{OPEN_TICKET_CHANNEL_ID}>\n2️⃣  Isi Nickname + Username + Paket\n3️⃣  Scan QRIS & kirim bukti\n4️⃣  Robux langsung masuk, no delay!\n\n💳  Pembayaran: QRIS ONLY!\n⚡  Proses: 1 - 15 Menit (Jam Kerja)\n💗  Mipi Store — Rafi Store")
        if kategori=="via_login": return f"🔑 **ROBUX VIA LOGIN — MIPI STORE**\n✨ Akun diproses langsung, aman & cepat!\n\n━━━━━━━━━━━━━━━━━━\n💎  PAKET VIA LOGIN\n━━━━━━━━━━━━━━━━━━\n✨  500 Robux  —  {h(500)}\n✨  1000 Robux  —  {h(1000)}\n✨  1500 Robux  —  {h(1500)}\n✨  2000 Robux  —  {h(2000)}\n✨  5000 Robux  —  {h(5000)}\n✨  10000 Robux  —  {h(10000)}\n\n⚠️  Wajib ganti password sementara / kasih kode verif ke admin!\n🛍️  Order di <#{OPEN_TICKET_CHANNEL_ID}>\n💗 Mipi Store"
        if kategori=="via_komunitas": return f"👥 **ROBUX VIA KOMUNITAS — MIPI STORE**\n✨ Via Group / Community, payout aman!\n\n━━━━━━━━━━━━━━━━━━\n💎  PAKET KOMUNITAS\n━━━━━━━━━━━━━━━━━━\n✨  500 Robux  —  {h(500)}\n✨  1000 Robux  —  {h(1000)}\n✨  2000 Robux  —  {h(2000)}\n✨  5000 Robux  —  {h(5000)}\n✨  10000 Robux  —  {h(10000)}\n\n📋 Syarat: Join grup dulu, tunggu 14 hari (aturan Roblox)!\n🛍️  Order di <#{OPEN_TICKET_CHANNEL_ID}>\n💗 Mipi Store"
        if kategori=="plus": return f"⭐ **ROBLOX PLUS — PENGGANTI PREMIUM**\n✨ Robux masuk otomatis tiap bulan, harga lebih hemat!\n\n━━━━━━━━━━━━━━━━━━\n💎  PAKET PLUS\n━━━━━━━━━━━━━━━━━━\n🌸  Plus 450  —  {h(500)}\n✨  Plus 1000  —  {h(1000)}\n👑  Plus 2200  —  {h(2000)}\n👑  Plus 5000  —  {h(5000)}\n\n💡 Plus = Premium versi Mipi, Robux cair tiap bulan!\n🛍️  Order di <#{OPEN_TICKET_CHANNEL_ID}>\n💗 Mipi Store"
        fast="";ecer=""
        for rbx in sorted(data.keys()):
            h2=format_rp(data[rbx])
            if rbx>=500: fast+=f"{rbx} = {h2}\n"
            else: ecer+=f"{rbx} = {h2}\n"
        return f"{fast}\nRobux Eceran\n{ecer}\nCara Order\nClick tombol ORDER dibawah, isi formulir, lalu tunggu admin. Pembayaran hanya QRIS.\nOrder di <#{OPEN_TICKET_CHANNEL_ID}>"
    except Exception as e: print(f"build_pricelist_text error: {e}");return "Pricelist lagi error, coba /lihat-harga lagi ya!"
CATEGORY_PRICELIST={"via_username":{"title":"💎 PRICELIST ROBUX VIA USERNAME — MIPI STORE","image":VIA_USERNAME_URL,"desc":"✨ Fast Process • Aman • Instan\nSyarat: SUDAH 18+ & SUDAH 2 LANGKAH"},"via_login":{"title":"PRICELIST ROBUX VLOG / VIA LOGIN","image":VIA_LOGIN_URL,"desc":"Via Login / Vlog - Proses Cepat\nAkun harus sudah 18+"},"via_komunitas":{"title":"PRICELIST ROBUX VIA KOMUNITAS","image":VIA_KOMUNITAS_URL,"desc":"Via Komunitas / Group\nMasuk grup dulu, robux cair 14 hari"},"plus":{"title":"PRICELIST ROBLOX PLUS","image":PLUS_URL,"desc":"Roblox Plus Monthly\nAktif 30 hari, full garansi"},"limited":{"title":"PRICELIST LIMITED ITEM","image":LIMITED_URL,"desc":"Beli / Jual Limited Via Trade\nHarga sesuai pasaran, tanya admin dulu"}}
def build_pricelist_embed(kategori="via_username"):
    info=CATEGORY_PRICELIST.get(kategori,CATEGORY_PRICELIST["via_username"]);e=discord.Embed(title=info["title"],description=info["desc"]+"\n\n"+build_pricelist_text(kategori),color=0xff69b4);e.set_image(url=info["image"]);e.set_footer(text="Mipi Store - Rafi Store | Harga bisa berubah sewaktu-waktu");return e
def build_all_pricelist_embeds(): return [build_pricelist_embed(k) for k in ["via_username","via_login","via_komunitas","plus","limited"]]
def build_rekber_embed():
    e=discord.Embed(title="🛡️  Middleman / Rekber Service by MIPI STORE",description=("✨  Transaksi aman, tanpa takut ketipu!\n💎  Admin jadi penengah, uang & barang dijamin aman sampe deal!\n\n━━━━━━━━━━━━━━━━━━\n💰  Daftar Fee Middleman\n━━━━━━━━━━━━━━━━━━\n🌸  Rp 1.000  —  Rp 9.000  →  Fee  **Rp 1.500**\n💠  Rp 10.000  —  Rp 49.000  →  Fee  **Rp 1.500**\n💠  Rp 50.000  —  Rp 99.000  →  Fee  **Rp 1.500**\n✨  Rp 100.000  —  Rp 199.000  →  Fee  **Rp 2.500**\n✨  Rp 200.000  —  Rp 499.000  →  Fee  **Rp 4.000**\n👑  Rp 500.000  —  Rp 1.000.000  →  Fee  **Rp 7.000**\n👑  Di atas Rp 1.000.000  →  Fee  **Rp 10.000**\n\n━━━━━━━━━━━━━━━━━━\n📜  Aturan Fee\n━━━━━━━━━━━━━━━━━━\n•  💳  Fee dibayar **1x per transaksi**\n•  🤝  Fee bisa ditanggung **Buyer / Seller / Split**\n•  ⚡  Proses cepat, admin online tiap hari\n•  🔒  100% Aman & Terpercaya\n\n━━━━━━━━━━━━━━━━━━\n🛍️  Cara Order\n━━━━━━━━━━━━━━━━━━\n"+f"1️⃣  Klik tombol **🎫 Buat Ticket Middleman** di bawah / Open Ticket di <#{OPEN_TICKET_CHANNEL_ID}>\n2️⃣  Isi Buyer, Seller, Jenis Barang, Harga, dan Fee Ditanggung\n3️⃣  Tunggu admin verifikasi & proses\n4️⃣  Deal! Barang & uang langsung diteruskan 💗\n\n💗  Mipi Store — Rafi Store"),color=0xff69b4);e.set_image(url=WELCOME_URL);e.set_footer(text="MIPI STORE • Rekber / Middleman • 100% Aman");return e
class RekberView(discord.ui.View):
    def __init__(self,guild_id=None):
        super().__init__(timeout=None);url=f"https://discord.com/channels/{guild_id}/{OPEN_TICKET_CHANNEL_ID}" if guild_id else f"https://discord.com/channels/@me/{OPEN_TICKET_CHANNEL_ID}";self.add_item(discord.ui.Button(label="🎫 Buat Ticket Middleman",style=discord.ButtonStyle.link,url=url,emoji="🎫"));self.add_item(discord.ui.Button(label="💬 Open Ticket",style=discord.ButtonStyle.link,url=url,emoji="💬"))
def jenis_to_kategori(jenis):
    try:
        j=str(jenis).upper()
        if "VIA LOGIN" in j: return "via_login"
        if "VIA KOMUNITAS" in j: return "via_komunitas"
        if "PLUSS" in j or "PLUS" in j: return "plus"
        if "LIMITED" in j or "OFFSALE" in j: return "limited"
        return "via_username"
    except: return "via_username"
# === LEADERBOARD + PENDING ===
LEADERBOARD_FILE="leaderboard.json"
def load_leaderboard(): return _load(LEADERBOARD_FILE,{})
def save_leaderboard(d): _save(LEADERBOARD_FILE,d)
def add_to_leaderboard(user_id,username,paket_text,kategori="via_username"):
    try:
        m=re.search(r'(\d+)',str(paket_text).replace('.','').replace(',',''))
        if not m: return
        jumlah=int(m.group(1));harga=get_harga(jumlah,kategori);data=load_leaderboard();bulan=datetime.now().strftime("%Y-%m")
        if bulan not in data: data[bulan]={}
        uid=str(user_id)
        if uid not in data[bulan]: data[bulan][uid]={"username":username,"total":0,"transaksi":0,"total_rp":0}
        if "total_rp" not in data[bulan][uid]: data[bulan][uid]["total_rp"]=0
        data[bulan][uid]["username"]=username;data[bulan][uid]["total"]+=jumlah;data[bulan][uid]["transaksi"]+=1;data[bulan][uid]["total_rp"]+=harga;save_leaderboard(data)
    except Exception as e: print(f"add leaderboard error: {e}")
def add_saldo_alltime_only(user_id,username,robux,kategori="via_username"):
    try:
        harga=get_harga(int(robux),kategori);data=load_leaderboard()
        if "ALLTIME" not in data: data["ALLTIME"]={}
        uid=str(user_id)
        if uid not in data["ALLTIME"]: data["ALLTIME"][uid]={"username":username,"total":0,"transaksi":0,"total_rp":0}
        data["ALLTIME"][uid]["username"]=username;data["ALLTIME"][uid]["total"]+=int(robux);data["ALLTIME"][uid]["transaksi"]+=1;data["ALLTIME"][uid]["total_rp"]+=harga;save_leaderboard(data)
    except Exception as e: print(f"add alltime error: {e}")
def get_total_belanja(user_id):
    try:
        data=load_leaderboard();tr=tro=tt=0
        for bulan,users in data.items():
            uid=str(user_id)
            if uid in users: tr+=users[uid].get("total_rp",0);tro+=users[uid].get("total",0);tt+=users[uid].get("transaksi",0)
        return tr,tro,tt
    except: return 0,0,0
PENDING_FILE="pending_saldo.json"
def load_pending(): return _load(PENDING_FILE,{})
def save_pending(d): _save(PENDING_FILE,d)
def add_to_pending(user_id,username,paket_text,ticket_number,channel_name="",kategori="via_username",robux_jumlah=None,harga_akhir=None,referral_by=None):
    try:
        if robux_jumlah is not None:
            try: jumlah=int(robux_jumlah)
            except: jumlah=0
            try: harga=int(harga_akhir) if harga_akhir else get_harga(jumlah,kategori)
            except: harga=get_harga(jumlah,kategori)
        else:
            m=re.search(r'(\d+)',str(paket_text).replace('.','').replace(',',''))
            if not m: return None
            jumlah=int(m.group(1));harga=get_harga(jumlah,kategori)
        if jumlah<=0: return None
        data=load_pending();oid=f"ORDER-{ticket_number:06d}";data[oid]={"user_id":str(user_id),"username":username,"paket":paket_text,"robux":jumlah,"harga":harga,"ticket_number":ticket_number,"channel":channel_name,"kategori":kategori,"waktu":datetime.now().strftime("%d %b %Y %H:%M"),"referral_by":referral_by};save_pending(data);return oid
    except Exception as e: print(f"add pending error: {e}");return None
# === SISTEM BARU V4: REFERRAL ===
def load_referral(): return _load("referral.json",{})
def save_referral(d): _save("referral.json",d)
def get_referral_code(user_id): return f"MIPI-{int(user_id)%100000:05d}"
def claim_referral(new_user_id,code):
    try:
        if not code: return None
        data=load_referral()
        for uid,info in data.items():
            if info.get("code")==code.upper() and str(uid)!=str(new_user_id):
                return uid
        return None
    except: return None
def add_referral_komisi(referrer_id,buyer_harga,buyer_name):
    try:
        komisi=int(buyer_harga*REFERRAL_RATE);data=load_referral();uid=str(referrer_id)
        if uid not in data: data[uid]={"code":get_referral_code(referrer_id),"total_komisi":0,"total_referral":0,"history":[]}
        data[uid]["total_komisi"]+=komisi;data[uid]["total_referral"]+=1;data[uid]["history"].append({"buyer":buyer_name,"harga":buyer_harga,"komisi":komisi,"waktu":datetime.now().strftime("%d %b %Y %H:%M")});save_referral(data);return komisi
    except Exception as e: print(f"referral error: {e}");return 0
# === SISTEM BARU V4: VOUCHER ===
def load_voucher(): return _load("voucher.json",{})
def save_voucher(d): _save("voucher.json",d)
def redeem_voucher(user_id,code):
    try:
        data=load_voucher();k=code.upper()
        if k not in data: return None,"Kode voucher gak ketemu!"
        v=data[k]
        if v.get("dipakai",0)>=v.get("max",1): return None,"Voucher udah habis!"
        if str(user_id) in v.get("used_by",[]): return None,"Kamu udah pake voucher ini!"
        v["dipakai"]=v.get("dipakai",0)+1;v.setdefault("used_by",[]).append(str(user_id));save_voucher(data);return v,None
    except Exception as e: return None,str(e)
# === SISTEM BARU V4: DAILY + POIN ===
def load_daily(): return _load("daily.json",{})
def save_daily(d): _save("daily.json",d)
def claim_daily(user_id):
    try:
        data=load_daily();uid=str(user_id);today=datetime.now().strftime("%Y-%m-%d")
        if uid in data and data[uid].get("last_claim")==today: return None,data[uid].get("poin",0),"Kamu udah claim hari ini! Balik besok ya!"
        if uid not in data: data[uid]={"poin":0,"streak":0,"last_claim":""}
        # Streak: kalo kemarin claim, streak +1, kalo enggak reset
        kemarin=(datetime.now()-timedelta(days=1)).strftime("%Y-%m-%d")
        if data[uid].get("last_claim")==kemarin: data[uid]["streak"]+=1
        else: data[uid]["streak"]=1
        bonus=DAILY_POIN+min(data[uid]["streak"]*2,20);data[uid]["poin"]+=bonus;data[uid]["last_claim"]=today;save_daily(data);return bonus,data[uid]["poin"],None
    except Exception as e: return None,0,str(e)
def get_poin(user_id): return load_daily().get(str(user_id),{}).get("poin",0)
def use_poin(user_id,jumlah):
    try:
        data=load_daily();uid=str(user_id)
        if data.get(uid,{}).get("poin",0)<jumlah: return False
        data[uid]["poin"]-=jumlah;save_daily(data);return True
    except: return False
# === SISTEM BARU V4: NOTIF RESTOCK ===
def load_notify(): return _load("notify.json",{})
def save_notify(d): _save("notify.json",d)
def add_notify(user_id,kategori):
    d=load_notify();d.setdefault(kategori,[])
    if str(user_id) not in d[kategori]: d[kategori].append(str(user_id))
    save_notify(d)
async def send_notify_restock(guild,kategori):
    try:
        d=load_notify();users=d.get(kategori,[])
        if not users: return
        for uid in users:
            try:
                u=await bot.fetch_user(int(uid));await u.send(f"🔔 **RESTOCK!** {kategori.upper()} udah DIBUKA lagi di MIPI STORE! Buruan order sebelum habis lagi! 💗\nOrder di <#{OPEN_TICKET_CHANNEL_ID}>")
            except: pass
        d[kategori]=[];save_notify(d)
    except Exception as e: print(f"notify error: {e}")
# === SISTEM BARU V4: MINI GAME ===
game_data={}
def start_tebak_harga():
    nominal=random.choice([100,200,300,400,500,1000,2000]);harga=get_harga(nominal,"via_username");pilihan=[harga]; 
    while len(pilihan)<4:
        fake=int(harga*random.uniform(0.7,1.4)/500)*500
        if fake not in pilihan and fake>0: pilihan.append(fake)
    random.shuffle(pilihan);return nominal,harga,pilihan
# === TOP SULTAN ===
def get_top_sultan_channel(guild):
    try:
        for ch in guild.text_channels:
            if "top-sultan" in ch.name.lower() or "top-leaderboard" in ch.name.lower(): return ch
    except: pass
    return None
def build_top_sultan_embed_bulanan():
    try:
        data=load_leaderboard();bulan_ini=datetime.now().strftime("%Y-%m");users=data.get(bulan_ini,{});s=sorted(users.items(),key=lambda x: x[1].get("total_rp",0),reverse=True)[:10];tp=len(users);tpes=sum(v.get("transaksi",0) for v in users.values());tom=sum(v.get("total_rp",0) for v in users.values());nama_bulan=datetime.now().strftime("%B %Y");desc=f"MIPI STORE • LEADERBOARD BULANAN - {nama_bulan}\nDaftar peringkat bulan ini aja! Bulan depan ke-reset lagi dari 0!\n\n"
        if not s: desc+="> Belum ada Sultan bulan ini! Order dulu, jadi #1 bulan ini!\n\n"
        else:
            medals=["🥇","🥈","🥉"]
            for i,(uid,info) in enumerate(s):
                medal=medals[i] if i<3 else "🏅";desc+=f"{medal} **Peringkat #{i+1} - <@{uid}>** ({info.get('username','User')})\n";desc+=f"└ Rp {info.get('total_rp',0):,} • {info.get('transaksi',0)}x Transaksi\n".replace(",",".")
        desc+=f"\n📊 **STATISTIK BULAN INI ({nama_bulan})**\n• Pembeli: {tp} Pembeli\n• Pesanan: {tpes} Pesanan\n• Omset: Rp {tom:,}\n".replace(",",".");desc+=f"\n⚡ Ke-reset tiap tanggal 1! Papan ini cuma buat bulan {nama_bulan} aja!\n🕒 Terakhir diperbarui: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB";e=discord.Embed(title=f"🏆 TOP 10 SULTAN BULANAN - {nama_bulan}",description=desc,color=0xff69b4);e.set_image(url=TOP_SULTAN_IMAGE);e.set_footer(text="MIPI STORE - TOP SULTAN BULANAN • Auto Update");return e
    except Exception as e: print(f"top bulanan error: {e}");return discord.Embed(title="Top Sultan Bulanan",description="Lagi error, coba lagi ya!",color=0xff0000)
def build_top_sultan_embed_semua():
    try:
        data=load_leaderboard();gabung={}
        for bulan,users in data.items():
            for uid,info in users.items():
                if uid not in gabung: gabung[uid]={"username":info.get("username","User"),"total_rp":0,"total":0,"transaksi":0}
                gabung[uid]["total_rp"]+=info.get("total_rp",0);gabung[uid]["total"]+=info.get("total",0);gabung[uid]["transaksi"]+=info.get("transaksi",0);gabung[uid]["username"]=info.get("username",gabung[uid]["username"])
        s=sorted(gabung.items(),key=lambda x: x[1]["total_rp"],reverse=True)[:10];tp=len(gabung);tpes=sum(v["transaksi"] for v in gabung.values());tom=sum(v["total_rp"] for v in gabung.values());desc="MIPI STORE • LEADERBOARD SEMUA / ALL TIME\nDaftar peringkat dari pertama toko buka sampe sekarang! GA PERNAH KE-RESET!\n\n"
        if not s: desc+="> Belum ada Sultan! Order dulu, jadi #1 sepanjang masa!\n\n"
        else:
            medals=["🥇","🥈","🥉"]
            for i,(uid,info) in enumerate(s):
                medal=medals[i] if i<3 else "🏅";desc+=f"{medal} **Peringkat #{i+1} - <@{uid}>** ({info['username']})\n";desc+=f"└ Rp {info['total_rp']:,} • {info['transaksi']}x Transaksi\n".replace(",",".")
        desc+=f"\n📊 **STATISTIK ALL TIME**\n• Pembeli: {tp} Pembeli\n• Pesanan: {tpes} Pesanan\n• Omset: Rp {tom:,}\n".replace(",",".");desc+=f"\n👑 Ini Sultan sepanjang masa! Ga ke-reset walau ganti bulan!\n🕒 Terakhir diperbarui: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB";e=discord.Embed(title="👑 TOP 10 SULTAN SEMUA / ALL TIME",description=desc,color=0x2B2D31);e.set_image(url=TOP_SULTAN_IMAGE);e.set_footer(text="MIPI STORE - TOP SULTAN ALL TIME • Auto Update");return e
    except Exception as e: print(f"top semua error: {e}");return discord.Embed(title="Top Sultan",description="Lagi error, coba lagi ya!",color=0xff0000)
def build_top_sultan_embed(): return build_top_sultan_embed_semua()
async def update_top_sultan(guild):
    try:
        ch=get_top_sultan_channel(guild)
        if not ch: return
        embed=build_top_sultan_embed_semua()
        try:
            async for msg in ch.history(limit=20):
                if msg.author==guild.me and msg.embeds and "TOP 10 SULTAN" in str(msg.embeds[0].title): await msg.edit(embed=embed);return
            await ch.send(embed=embed)
        except Exception as e: print(f"Gagal update top-sultan: {e}")
    except Exception as e: print(f"update_top_sultan error: {e}")
@tasks.loop(minutes=1)
async def auto_update_top_sultan():
    for guild in bot.guilds:
        try: await update_top_sultan(guild)
        except: pass
# === AUTO ROLE SULTAN V4 ===
async def check_auto_role(guild,user_id,total_rp):
    try:
        member=guild.get_member(int(user_id))
        if not member: return None
        # Cari / bikin role
        target=None
        if total_rp>=5000000: target="LEGEND"
        elif total_rp>=1000000: target="SULTAN"
        elif total_rp>=500000: target="VIP"
        elif total_rp>=100000: target="Regular"
        if not target: return None
        role=None
        for r in guild.roles:
            if r.name.upper()==target: role=r;break
        if not role:
            try: role=await guild.create_role(name=target,colour=discord.Colour.gold() if target in ["SULTAN","LEGEND"] else discord.Colour.pink(),mentionable=True)
            except: return None
        if role not in member.roles:
            await member.add_roles(role)
            try: await member.send(f"🎉 **SELAMAT!** Kamu naik level jadi **{target}** di MIPI STORE! Total belanja kamu udah {format_rp(total_rp)}! Makasih udah setia order 💗")
            except: pass
            return target
        return None
    except Exception as e: print(f"auto role error: {e}");return None
def is_admin_or_owner(user,guild):
    try:
        if user.id==guild.owner_id: return True
        if user.guild_permissions.administrator: return True
        rn=[r.name.lower() for r in user.roles]
        return any(x in rn for x in ["admin","owner","staff","moderator","adm"])
    except: return False
class KonfirmasiSaldoView(discord.ui.View):
    def __init__(self,order_id):
        super().__init__(timeout=None);self.order_id=order_id
    @discord.ui.button(label="✅ Konfirmasi Masuk Saldo",style=discord.ButtonStyle.success,custom_id="saldo_confirm_btn")
    async def confirm_btn(self,interaction:discord.Interaction,button:discord.ui.Button):
        try:
            if not is_admin_or_owner(interaction.user,interaction.guild): await interaction.response.send_message("❌ Hanya Admin / Owner!",ephemeral=True);return
            pend=load_pending()
            if self.order_id not in pend: await interaction.response.send_message("❌ Udah dikonfirmasi / ditolak!",ephemeral=True);return
            d=pend[self.order_id];add_to_leaderboard(int(d["user_id"]),d["username"],d["paket"],kategori=d.get("kategori","via_username"));del pend[self.order_id];save_pending(d)
            # V4: Referral komisi otomatis
            komisi_txt=""
            if d.get("referral_by"):
                komisi=add_referral_komisi(d["referral_by"],d["harga"],d["username"]);komisi_txt=f"\n💸 Referral: <@{d['referral_by']}> dapet komisi {format_rp(komisi)} (5%)!"
                try:
                    u2=await bot.fetch_user(int(d["referral_by"]));await u2.send(f"💸 Kamu dapet komisi referral {format_rp(komisi)} dari {d['username']} yang order {d['paket']} di MIPI STORE! Total komisi kamu nambah! 💗")
                except: pass
            await interaction.response.send_message(f"✅ **SALDO DIKONFIRMASI!**\nBuyer: <@{d['user_id']}>\nPaket: {d['paket']}\n+{d['robux']} R$ udah masuk saldo + Top Sultan Bulanan + All Time!{komisi_txt}",ephemeral=False)
            for item in self.children: item.disabled=True
            try: await interaction.message.edit(view=self)
            except: pass
            try: await update_top_sultan(interaction.guild)
            except: pass
            # V4: Auto Role + Showcase kalo jadi #1
            try:
                tr,_,_=get_total_belanja(int(d["user_id"]));naik=await check_auto_role(interaction.guild,int(d["user_id"]),tr)
                if naik: await interaction.channel.send(f"🎉 <@{d['user_id']}> naik level jadi **{naik}**! Total belanja {format_rp(tr)}! 👑")
            except: pass
            try:
                u=await bot.fetch_user(int(d["user_id"]));lvl=get_level(get_total_belanja(int(d["user_id"]))[0]);await u.send(f"🎉 Saldo kamu ditambah! +{d['robux']} R$ dari {d['paket']} udah dikonfirmasi admin! Level kamu sekarang: {lvl} 💗")
            except: pass
        except Exception as e:
            print(f"confirm saldo error: {e}")
            try: await interaction.response.send_message(f"❌ Error: {e}",ephemeral=True)
            except: pass
    @discord.ui.button(label="❌ Tolak / Order Palsu",style=discord.ButtonStyle.danger,custom_id="saldo_reject_btn")
    async def reject_btn(self,interaction:discord.Interaction,button:discord.ui.Button):
        try:
            if not is_admin_or_owner(interaction.user,interaction.guild): await interaction.response.send_message("❌ Hanya Admin / Owner!",ephemeral=True);return
            pend=load_pending()
            if self.order_id not in pend: await interaction.response.send_message("❌ Udah diproses!",ephemeral=True);return
            d=pend[self.order_id];del pend[self.order_id];save_pending(d);await interaction.response.send_message(f"❌ Order {self.order_id} ({d['paket']} - <@{d['user_id']}>) **DITOLAK**, ga masuk saldo!",ephemeral=False)
            for item in self.children: item.disabled=True
            try: await interaction.message.edit(view=self)
            except: pass
            try: await update_top_sultan(interaction.guild)
            except: pass
        except Exception as e: print(f"reject saldo error: {e}")
# === PROMO ===
PROMO_FILE="promo.json"
def load_promo(): return _load(PROMO_FILE,{})
def save_promo(d): _save(PROMO_FILE,d)
def cek_promo(kode,harga_awal,jumlah_robux=0):
    try:
        if not kode or not str(kode).strip(): return harga_awal,0,None
        kode=str(kode).upper().strip();data=load_promo()
        if kode not in data: return harga_awal,0,"Kode promo tidak ditemukan!"
        p=data[kode]
        if jumlah_robux<500: return harga_awal,0,"Minimal belanja 500 Robux untuk pakai promo ini!"
        if p.get("dipakai",0)>=p.get("max",999): return harga_awal,0,"Kode promo sudah habis dipakai!"
        diskon=int(harga_awal*p["diskon"]/100) if p["tipe"]=="persen" else int(p["diskon"]);return max(0,harga_awal-diskon),diskon,None
    except Exception as e: print(f"cek promo error: {e}");return harga_awal,0,None
# === GIVEAWAY ===
giveaway_data={}
class GiveawayView(discord.ui.View):
    def __init__(self,giveaway_id):
        super().__init__(timeout=None);self.giveaway_id=giveaway_id
    @discord.ui.button(label="JOIN GIVEAWAY",style=discord.ButtonStyle.success,custom_id="join_giveaway",emoji="🎉")
    async def join_btn(self,interaction:discord.Interaction,button:discord.ui.Button):
        try:
            data=giveaway_data.get(self.giveaway_id)
            if not data: await interaction.response.send_message("Giveaway ini sudah berakhir!",ephemeral=True);return
            if data["ended"]: await interaction.response.send_message("Giveaway sudah berakhir Wal!",ephemeral=True);return
            uid=interaction.user.id
            if uid in data["peserta"]: await interaction.response.send_message("Kamu udah join Wal!",ephemeral=True);return
            data["peserta"].append(uid)
            try:
                embed=interaction.message.embeds[0];embed.description="Hadiah: "+str(data["hadiah"])+"\nHost: "+str(data["host_mention"])+"\nPeserta: "+str(len(data["peserta"]))+" orang";await interaction.message.edit(embed=embed,view=self)
            except: pass
            await interaction.response.send_message("Berhasil join giveaway "+str(data["hadiah"])+"! Good luck!",ephemeral=True)
        except Exception as e: print(f"join giveaway error: {e}")
async def end_giveaway(guild,channel_id,message_id,giveaway_id):
    try:
        data=giveaway_data.get(giveaway_id)
        if not data or data["ended"]: return
        data["ended"]=True;channel=guild.get_channel(channel_id)
        if not channel: return
        try: msg=await channel.fetch_message(message_id)
        except: msg=None
        if len(data["peserta"])==0:
            if msg:
                embed=discord.Embed(title="GIVEAWAY BERAKHIR - GAK ADA PESERTA",description="Hadiah: "+str(data["hadiah"]),color=0xff0000);await msg.edit(embed=embed,view=None)
            await channel.send("Giveaway berakhir tapi gak ada yang join!");return
        winners=random.sample(data["peserta"],min(data["pemenang"],len(data["peserta"])));wm=", ".join([f"<@{w}>" for w in winners])
        if msg:
            embed=discord.Embed(title="GIVEAWAY BERAKHIR - PEMENANG TERPILIH!",description="Hadiah: "+str(data["hadiah"])+"\n\nPemenang:\n"+wm+"\n\nTotal Peserta: "+str(len(data["peserta"]))+" orang",color=0x57f287);await msg.edit(embed=embed,view=None)
        await channel.send("GIVEAWAY BERAKHIR!\n\nHadiah: "+str(data["hadiah"])+"\nPemenang: "+wm)
    except Exception as e: print(f"Gagal end giveaway: {e}")
# === FILTER + ANTI-SCAM V4 ===
BANNED_WORDS=["wts robux","jual robux","sell robux","jual rb","wts rb","jual limited","wts limited","sell limited","jual robux murah","robux murah","top up robux","jual akun robux","wts akun robux","wtt robux","wtb robux","jual robux via","robux via username murah"]
ALLOWED_IF_HAS=["akun pribadi","akun roblox","akun pribadi secepatnya"]
SCAM_LINKS=["discord.gg/","bit.ly/","tinyurl.com/","free-robux","robux-free","robux-generator","nitro-free","steamcommunity.trade"]
def is_banned_selling(text):
    try:
        low=str(text).lower()
        if any(a in low for a in ALLOWED_IF_HAS) and "robux" not in low and "limited" not in low: return False
        return any(w in low for w in BANNED_WORDS)
    except: return False
def is_scam_link(text):
    try:
        low=str(text).lower()
        return any(s in low for s in SCAM_LINKS)
    except: return False
# === LANJUT DI BAGIAN 2 - JANGAN TAMBAH bot.run DI SINI ===
# BAGIAN 2 ISI: Ticket + Modal + Rating + Vouch + Transcript + Statistik + Daily + Referral Command + Voucher + Game + Semua Slash Command + Auto Rekap + bot.run
# ============================================================================
# MIPI STORE V4 - BAGIAN 2 / 2 - 2K BARIS - LANJUTAN BAGIAN 1
# PASTE DI BAWAHNYA BAGIAN 1, JANGAN DI TIMPA!
# ============================================================================
# ISI BAGIAN 2:
# - Hitung Harga + Channel Helper + Transcript + History + Vouch
# - Auto Close + Auto Reminder + Auto Rekap Omset
# - Rating + Comment Modal + Status + Close + Saldo View
# - Ticket Panel + Order Modal + Button Ticket + TicketTypeView
# - on_message (Filter + Anti-Scam + Auto Reminder) + on_ready
# - Panel + Semua Slash Command V4 (Ticket, Pricelist, Rekber, Stock, Saldo,
#   Referral, Voucher, Daily, Game, Statistik, Promo, Giveaway, Pending, dll)
# - bot.run
# ============================================================================
def hitung_harga(paket_text,kategori="via_username",robux_jumlah=None,harga_akhir=None):
    try:
        if robux_jumlah is not None:
            try:
                j=int(robux_jumlah);h=int(harga_akhir) if harga_akhir else get_harga(j,kategori);return str(j),format_rp(h)
            except: pass
        m=re.search(r'(\d+)',str(paket_text).replace('.','').replace(',',''))
        if not m: return "500","Rp 75.000"
        jumlah=int(m.group(1));return str(jumlah),f"Rp {get_harga(jumlah,kategori):,}".replace(",",".")
    except: return "500","Rp 75.000"
def get_status_channel(guild):
    try:
        for ch in guild.text_channels:
            if "order-status" in ch.name.lower(): return ch
    except: pass
    return None
def get_history_channel(guild):
    try:
        for ch in guild.text_channels:
            if "history" in ch.name.lower(): return ch
    except: pass
    return None
def get_ticket_category(guild):
    try:
        for cat in guild.categories:
            if "TICKET" in cat.name.upper(): return cat
    except: pass
    return None
def get_vouch_channel(guild):
    try:
        for ch in guild.channels:
            if "vouch" in ch.name.lower(): return ch
    except: pass
    return None
def get_omset_channel(guild):
    try:
        for ch in guild.text_channels:
            if "omset" in ch.name.lower() or "rekap" in ch.name.lower() or "history" in ch.name.lower(): return ch
    except: pass
    return get_history_channel(guild)
def make_html_transcript(number,messages,username,paket,duration):
    try:
        rows=""
        for m in messages: rows+="<div style=\"margin:6px 0;padding:8px;background:#2b2d31;border-radius:8px;\"><b style=\"color:#fff;\">"+html.escape(str(m["author"]))+"</b> <span style=\"color:#949ba4;font-size:12px;\">"+m["time"]+"</span><br><span style=\"color:#dbdee1;\">"+html.escape(m["content"] or "(gambar / embed)")+"</span></div>"
        return "<!DOCTYPE html><html><head><meta charset=\"utf-8\"><title>Ticket #"+str(number)+" Transcript - MIPI STORE</title></head><body style=\"background:#1e1f22;font-family:sans-serif;padding:20px;\"><h2 style=\"color:white;\">MIPI STORE - Ticket #"+str(number)+"</h2><p style=\"color:#949ba4;\">Created by "+html.escape(username)+" | Subject: "+html.escape(paket)+" | Duration: "+str(duration)+" minutes | "+str(len(messages))+" messages</p>"+rows+"</body></html>"
    except: return "<html><body>Transcript error</body></html>"
async def send_status_update(guild,number,username,user_id,paket,status_text,color):
    try:
        ch=get_status_channel(guild)
        if not ch: return
        embed=discord.Embed(title="Order Status - Ticket #"+str(number),description="Customer: <@"+str(user_id)+"> ("+username+")\nPaket: "+paket+"\nStatus: "+status_text,color=color);embed.set_footer(text="MIPI STORE - Order Status");await ch.send(embed=embed)
    except Exception as e: print(f"send status error: {e}")
async def send_history_log(guild,channel,data,admin_user):
    try:
        ch=get_history_channel(guild)
        if not ch: return
        number=data["number"];user_id=data["user_id"];roblox_user=data.get("roblox_username",data.get("username","-"));nickname=data.get("nickname","-");paket=data.get("paket","500 Robux");pembayaran=data.get("pembayaran","Qris");jumlah,harga=hitung_harga(paket,data.get("kategori","via_username"),robux_jumlah=data.get("robux_jumlah"),harga_akhir=data.get("harga_akhir"));ticket_name=channel.name if channel else "ticket-"+str(number);admin_text=admin_user.mention if admin_user else "Auto-Close";embed=discord.Embed(color=0x2b2d31);embed.description="Ticket Log\n\nTicket\n"+ticket_name+"\nAction\nClosed\nPanel\nMipi Store Ticket\nMember\n<@"+str(user_id)+">\nNickname Roblox\n"+nickname+"\nUsername Roblox\n"+roblox_user+"\nJumlah Robux\n"+jumlah+"\nTotal Harga\n"+harga+"\nPayment\n"+pembayaran+"\nAdmin\n"+admin_text;embed.set_image(url=THANKYOU_URL);await ch.send(embed=embed)
    except Exception as e: print(f"send history error: {e}")
async def send_vouch(guild,user,paket,stars,komentar,ticket_number=0,ticket_name=""):
    try:
        ch=get_vouch_channel(guild)
        if not ch: return
        jumlah,harga=hitung_harga(paket);star_str="⭐"*stars;seller=guild.owner.mention if guild.owner else "MIPI STORE"
        if not ticket_name: ticket_name="ticket-"+str(ticket_number)+"-"+user.name
        embed=discord.Embed(color=0x2b2d31);embed.description="VOUCH RECEIVED\n\nTicket ID\n"+str(ticket_number)+"\nNominal\n"+harga+"\nSeller\n"+seller+"\nBuyer\n<@"+str(user.id)+">\nHandled by\n"+seller+"\nRating\n"+star_str+"\nKomentar\n"+komentar+" 💗\nSource\n"+ticket_name;embed.set_thumbnail(url=user.display_avatar.url);embed.set_footer(text="MIPI STORE Vouch System | "+datetime.now().strftime("%B %d, %Y at %I:%M %p"));msg=await ch.send(embed=embed)
        try:
            thread_name="Vouch - "+user.name+" | Ticket #"+str(ticket_number)
            if isinstance(ch,discord.ForumChannel): await ch.create_thread(name=thread_name,content="Vouch dari "+user.mention+" - Ticket #"+str(ticket_number)+" - "+paket+" - "+star_str+" - "+komentar)
            else:
                thread=await msg.create_thread(name=thread_name,auto_archive_duration=1440);await thread.send("Vouch dari "+user.mention+"\n\nPaket: "+paket+" ("+harga+")\nRating: "+star_str+"\nKomentar: "+komentar+"\nTicket: "+ticket_name)
        except Exception as e: print(f"Gagal buat thread vouch: {e}")
    except Exception as e: print(f"send vouch error: {e}")
# === STATISTIK V4 ===
def get_statistik():
    try:
        data=load_leaderboard();today=datetime.now().strftime("%Y-%m-%d");bulan=datetime.now().strftime("%Y-%m");hari_ini_rp=0;hari_ini_tr=0;bulan_rp=0;bulan_tr=0;all_rp=0;all_tr=0
        # Pending juga dihitung sebagai omset hari ini kalo waktu-nya hari ini
        pend=load_pending()
        for oid,d in pend.items():
            if today in d.get("waktu",""): hari_ini_rp+=d.get("harga",0);hari_ini_tr+=1
        for b,users in data.items():
            for uid,info in users.items():
                if b=="ALLTIME": continue
                all_rp+=info.get("total_rp",0);all_tr+=info.get("transaksi",0)
                if b==bulan: bulan_rp+=info.get("total_rp",0);bulan_tr+=info.get("transaksi",0)
        # Hari ini = dari leaderboard bulan ini + pending hari ini (approx)
        hari_ini_rp+=0
        return {"hari_rp":hari_ini_rp,"hari_tr":hari_ini_tr,"bulan_rp":bulan_rp,"bulan_tr":bulan_tr,"all_rp":all_rp,"all_tr":all_tr}
    except Exception as e: print(f"statistik error: {e}");return {"hari_rp":0,"hari_tr":0,"bulan_rp":0,"bulan_tr":0,"all_rp":0,"all_tr":0}
async def do_auto_close(guild,channel,data,reason="auto-closed due to inactivity",admin_user=None):
    try:
        number=data["number"];user_id=data["user_id"];paket=data.get("paket","ORDER ROBUX");created=data["created_at"];duration=int((time.time()-created)//60)
        if duration<1: duration=1
        user_last_ticket[user_id]={"number":number,"paket":paket,"ticket_name":channel.name if channel else "","seller_id":guild.owner_id}
        try: await send_history_log(guild,channel,data,admin_user)
        except Exception as e: print(f"Gagal history: {e}")
        messages=[]
        try:
            async for m in channel.history(limit=200,oldest_first=True): messages.append({"author":str(m.author),"time":m.created_at.strftime("%H:%M"),"content":m.content})
        except: pass
        status_ch=get_status_channel(guild)
        if status_ch:
            try:
                embed1=discord.Embed(title="Ticket Auto-Closed",description="#"+str(number)+" "+reason+"\nTicket ID\n"+str(number),color=0xfee75c);embed1.set_footer(text=datetime.now().strftime("%B %d, %Y at %I:%M %p"));await status_ch.send(embed=embed1);html_text=make_html_transcript(number,messages,data.get("username","User"),paket,duration);file=discord.File(io.BytesIO(html_text.encode()),filename="ticket-"+str(number)+"-auto-transcript.html");embed2=discord.Embed(title="Auto-Generated Transcript (Auto-Closed)",description="Transcript automatically generated for auto-closed ticket #"+str(number)+"\n\nTicket\nTicket #"+str(number)+"\nCreated by <@"+str(user_id)+">\n"+str(len(messages))+" messages\n\nGeneration\nDuration: "+str(duration)+" minutes\nStatus: Auto-Closed -> Auto-Transcript\n\nSubject\n"+paket,color=0x5865f2);embed2.set_footer(text=datetime.now().strftime("%B %d, %Y at %I:%M %p"));await status_ch.send(embed=embed2,file=file)
            except Exception as e: print(f"send status transcript error: {e}")
        try:
            user=await bot.fetch_user(user_id);closer=admin_user.name if admin_user else "MIPI STORE (Auto-Close)";embed=discord.Embed(title="Rate Your Experience",description="Hi "+user.name+"! Your support ticket has been resolved.\nPlease rate your experience by clicking a star below.\n\nTicket #"+str(number)+" in MIPI STORE\nResolved in\n"+str(duration)+" minutes\n\nClosed by\n"+closer,color=0x2b2d31);await user.send(embed=embed,view=RatingView(number))
        except: pass
        try:
            order_id=add_to_pending(user_id,data.get("username","User"),paket,number,channel.name if channel else "",kategori=data.get("kategori","via_username"),robux_jumlah=data.get("robux_jumlah"),harga_akhir=data.get("harga_akhir"),referral_by=data.get("referral_by"))
            if order_id:
                ch_pending=get_history_channel(guild) or get_status_channel(guild)
                if ch_pending:
                    jumlah_tmp,harga_tmp=hitung_harga(paket,data.get("kategori","via_username"),robux_jumlah=data.get("robux_jumlah"),harga_akhir=data.get("harga_akhir"));embed_p=discord.Embed(title=f"⏳ PENDING SALDO - {order_id}",description=f"Buyer: <@{user_id}>\nPaket: {paket}\nRobux: {jumlah_tmp} R$\nHarga: {harga_tmp}\nTicket: #{number}\n\n**Order ini BELUM masuk leaderboard!**\nAdmin harus pencet ✅ dulu baru masuk saldo!",color=0xfee75c);await ch_pending.send(embed=embed_p,view=KonfirmasiSaldoView(order_id))
        except Exception as e: print(f"Gagal pending saldo: {e}")
        if channel.id in ticket_data: del ticket_data[channel.id]
        try: await channel.delete()
        except: pass
    except Exception as e: print(f"do_auto_close error: {e}");traceback.print_exc()
@tasks.loop(minutes=1)
async def check_inactive():
    try:
        now=time.time()
        for channel_id,data in list(ticket_data.items()):
            last=data.get("last_activity",data["created_at"])
            # V4: Auto Reminder - kalo 10 menit gak ada aktivitas, tag admin
            if 10*60 < now-last < 11*60:
                try:
                    ch=bot.get_channel(channel_id)
                    if ch: await ch.send(f"⏰ <@&{ch.guild.owner_id}> Ticket ini 10 menit gak ada aktivitas! Tolong dicek ya! 💗")
                except: pass
            if now-last>15*60:
                ch=bot.get_channel(channel_id)
                if not ch: del ticket_data[channel_id];continue
                await do_auto_close(ch.guild,ch,data)
    except Exception as e: print(f"check_inactive error: {e}")
@tasks.loop(minutes=60)
async def auto_rekap_omset():
    # V4: Tiap jam, cek kalo jam 0 (tengah malem), kirim rekap ke owner
    try:
        now=datetime.now()
        if now.hour!=0: return
        for guild in bot.guilds:
            try:
                s=get_statistik();ch=get_omset_channel(guild)
                if not ch: continue
                e=discord.Embed(title="📊 REKAP OMSET HARIAN - MIPI STORE",description=f"📅 Tanggal: {now.strftime('%d %B %Y')}\n\n💰 **Omset Bulan Ini:** {format_rp(s['bulan_rp'])} ({s['bulan_tr']} transaksi)\n👑 **Omset All Time:** {format_rp(s['all_rp'])} ({s['all_tr']} transaksi)\n\n💗 Mipi Store — Rafi Store",color=0xff69b4);await ch.send(embed=e)
            except: pass
    except Exception as e: print(f"rekap error: {e}")
class RatingView(discord.ui.View):
    def __init__(self,ticket_number):
        super().__init__(timeout=None);self.ticket_number=ticket_number
    async def send_thanks(self,interaction,stars):
        try:
            user_ratings[interaction.user.id]=stars;star_str="⭐"*stars;embed=discord.Embed(title="Terima Kasih! 💗",description="Kamu memberi rating "+star_str+" ("+str(stars)+"/5) untuk MIPI STORE!\n\nTerima kasih sudah order di Mipi Store! Ditunggu order berikutnya ya 🌸",color=0xff69b4);embed.set_image(url=THANKYOU_URL);await interaction.response.edit_message(embed=embed,view=self)
        except Exception as e: print(f"rating error: {e}")
    @discord.ui.button(label="⭐ 1",style=discord.ButtonStyle.secondary,custom_id="rate1")
    async def r1(self,interaction:discord.Interaction,button:discord.ui.Button): await self.send_thanks(interaction,1)
    @discord.ui.button(label="⭐ 2",style=discord.ButtonStyle.secondary,custom_id="rate2")
    async def r2(self,interaction:discord.Interaction,button:discord.ui.Button): await self.send_thanks(interaction,2)
    @discord.ui.button(label="⭐ 3",style=discord.ButtonStyle.primary,custom_id="rate3")
    async def r3(self,interaction:discord.Interaction,button:discord.ui.Button): await self.send_thanks(interaction,3)
    @discord.ui.button(label="⭐ 4",style=discord.ButtonStyle.success,custom_id="rate4")
    async def r4(self,interaction:discord.Interaction,button:discord.ui.Button): await self.send_thanks(interaction,4)
    @discord.ui.button(label="⭐ 5",style=discord.ButtonStyle.success,custom_id="rate5")
    async def r5(self,interaction:discord.Interaction,button:discord.ui.Button): await self.send_thanks(interaction,5)
    @discord.ui.button(label="📝 Add Comment",style=discord.ButtonStyle.secondary,custom_id="add_comment",row=1)
    async def comment(self,interaction:discord.Interaction,button:discord.ui.Button):
        try: await interaction.response.send_modal(CommentModal(ticket_number=self.ticket_number))
        except Exception as e: print(f"comment modal error: {e}")
    @discord.ui.button(label="❌ No Thanks",style=discord.ButtonStyle.secondary,custom_id="no_thanks",row=1)
    async def no_thanks(self,interaction:discord.Interaction,button:discord.ui.Button):
        try: await interaction.response.edit_message(content="Oke! Terima kasih sudah order di MIPI STORE 💗",embed=None,view=None)
        except: pass
class CommentModal(discord.ui.Modal,title="Komentar / Testimoni"):
    def __init__(self,ticket_number):
        super().__init__();self.ticket_number=ticket_number
    komentar=discord.ui.TextInput(label="Komentar kamu",placeholder="satset poll",style=discord.TextStyle.paragraph,required=True)
    async def on_submit(self,interaction:discord.Interaction):
        try:
            stars=user_ratings.get(interaction.user.id,5);last=user_last_ticket.get(interaction.user.id,{});paket=last.get("paket","500 Robux");ticket_name=last.get("ticket_name","ticket-"+str(self.ticket_number)+"-"+interaction.user.name)
            try:
                guild=None
                for g in bot.guilds:
                    ch=get_vouch_channel(g)
                    if ch: guild=g;break
                if guild: await send_vouch(guild,interaction.user,paket,stars,self.komentar.value,ticket_number=self.ticket_number,ticket_name=ticket_name)
            except Exception as e: print(f"Gagal vouch: {e}")
            await interaction.response.send_message("Terima kasih komentarnya! 💗\n> "+self.komentar.value+"\n\nVouch kamu sudah muncul di vouch + jadi thread! 🎉\nRating: "+("⭐"*stars)+" ("+str(stars)+"/5)",ephemeral=True)
        except Exception as e:
            print(f"comment submit error: {e}")
            try: await interaction.response.send_message(f"❌ Error: {e}",ephemeral=True)
            except: pass
class StatusView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="⏳ Menunggu Pembayaran",style=discord.ButtonStyle.secondary,custom_id="status_waiting")
    async def waiting(self,interaction:discord.Interaction,button:discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
            if not is_admin_or_owner(interaction.user,interaction.guild): await interaction.followup.send("Hanya Admin & Owner!",ephemeral=True);return
            data=ticket_data.get(interaction.channel.id,{})
            if data: data["last_activity"]=time.time()
            await interaction.followup.send("Status diubah: Menunggu Pembayaran");await send_status_update(interaction.guild,data.get("number","?"),data.get("username",interaction.user.name),data.get("user_id",interaction.user.id),data.get("paket","ORDER"),"Menunggu Pembayaran",0xfee75c)
        except Exception as e: print(f"status waiting error: {e}")
    @discord.ui.button(label="🔄 Diproses",style=discord.ButtonStyle.primary,custom_id="status_process")
    async def process(self,interaction:discord.Interaction,button:discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
            if not is_admin_or_owner(interaction.user,interaction.guild): await interaction.followup.send("Hanya Admin & Owner!",ephemeral=True);return
            data=ticket_data.get(interaction.channel.id,{})
            if data: data["last_activity"]=time.time()
            await interaction.followup.send("Status diubah: Sedang Diproses");await send_status_update(interaction.guild,data.get("number","?"),data.get("username",interaction.user.name),data.get("user_id",interaction.user.id),data.get("paket","ORDER"),"Sedang Diproses",0x5865f2)
        except Exception as e: print(f"status process error: {e}")
    @discord.ui.button(label="✅ Selesai",style=discord.ButtonStyle.success,custom_id="status_done")
    async def done(self,interaction:discord.Interaction,button:discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
            if not is_admin_or_owner(interaction.user,interaction.guild): await interaction.followup.send("Hanya Admin & Owner!",ephemeral=True);return
            data=ticket_data.get(interaction.channel.id,{})
            if data: data["last_activity"]=time.time()
            await interaction.followup.send("Status diubah: Selesai!");await send_status_update(interaction.guild,data.get("number","?"),data.get("username",interaction.user.name),data.get("user_id",interaction.user.id),data.get("paket","ORDER"),"Selesai / Done",0x57f287)
        except Exception as e: print(f"status done error: {e}")
class CloseView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🔒 CLOSE TICKET",style=discord.ButtonStyle.danger,custom_id="close_ticket")
    async def close_btn(self,interaction:discord.Interaction,button:discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
            if not is_admin_or_owner(interaction.user,interaction.guild): await interaction.followup.send("Hanya Admin & Owner!",ephemeral=True);return
            channel=interaction.channel;data=ticket_data.get(channel.id)
            if not data: await interaction.followup.send("Ticket ditutup...");await channel.delete();return
            await interaction.followup.send("Ticket ditutup oleh "+interaction.user.mention+". Membuat transcript...");await do_auto_close(interaction.guild,channel,data,reason="closed by owner",admin_user=interaction.user)
        except Exception as e: print(f"close error: {e}")
class SaldoView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="💳 CEK SALDO SAYA",style=discord.ButtonStyle.primary,custom_id="cek_saldo_btn")
    async def cek_saldo(self,interaction:discord.Interaction,button:discord.ui.Button):
        try:
            tr,tro,tt=get_total_belanja(interaction.user.id);lvl=get_level(tr);nxt,sisa=get_next_level(tr);poin=get_poin(interaction.user.id);embed=discord.Embed(color=0xff1493);embed.description="INFORMASI SALDO / TOTAL TRANSAKSI\n\nHalo "+interaction.user.mention+",\n\n🏆 Level: "+lvl+"\n➡️ Next: "+nxt+f" (kurang {format_rp(sisa)})\n\nTotal Belanja: "+format_rp(tr)+"\nTotal Robux: "+str(tro)+" R$\nTotal Transaksi: "+str(tt)+"x\n🎁 Poin Daily: "+str(poin)+" poin\n\nMIPI STORE - CHECK SALDO";embed.set_footer(text="Mipi Store - Rafi Store");await interaction.response.send_message(embed=embed,ephemeral=True)
        except Exception as e:
            print(f"saldo view error: {e}")
            try: await interaction.response.send_message(f"❌ Error: {e}",ephemeral=True)
            except: pass
E_VIA="💎";E_VLOG="💎";E_BELI_LIMITED="💠";E_JUAL_LIMITED="💰";E_OFFSALE="🎁";E_PLUS="⭐";E_REKBER="🛡️";E_NANYA="🐱";E_KOMUNITAS="👥";E_AKUN="💃"
def build_ticket_panel_baru_embed():
    e=discord.Embed(title="🎫 Mipi Store - Ticket Order",description=f"{E_VIA} **Robux Via Username** - Beli Robux Via Username\n{E_VLOG} **Robux Vlog** - Beli Robux melalui via login\n{E_BELI_LIMITED} **Beli Limited Item** - Beli Item Via Trade\n{E_JUAL_LIMITED} **Jual Limited Item** - Dapatkan Uang (Cashout)\n{E_OFFSALE} **Beli Item Offsale** - Via Redeem Code\n{E_PLUS} **Beli Roblox Plus** - Roblox Plus Monthly\n{E_REKBER} **Rekber/MM** - Rekber, Akun, Jasa, dll\n{E_NANYA} **Other/Nanya** - Pertanyaan & bantuan lainnya\n{E_KOMUNITAS} **Via Komunitas** - Beli Robux Via Komunitas / Group\n{E_AKUN} **Beli Akun** - Beli Akun Roblox Sultan / Stok\n\n✨ **SISTEM BARU V4:** Referral 5% • Daily Reward • Level Sultan • Voucher • Game Tebak Harga!\nMipi Store Powered by MIPI 💗",color=0x2B2D31);e.set_image(url=WELCOME_URL);e.set_footer(text="Mipi Store - Pilih tombol di bawah sesuai kebutuhan kamu!");return e
class OrderModalBaru(discord.ui.Modal):
    def __init__(self,jenis:str):
        super().__init__(title=f"Order - {jenis}");self.jenis=jenis
        try:
            if jenis in ["BELI LIMITED","JUAL LIMITED","BELI ITEM OFFSALE"]: self.f1=discord.ui.TextInput(label="Username Roblox",placeholder="Username Roblox kamu",required=True);self.f2=discord.ui.TextInput(label="Nama Item",placeholder="Contoh: Domino Crown",required=True);self.f3=discord.ui.TextInput(label="Harga / Budget",placeholder="Contoh: 500k / QRIS",required=True)
            elif jenis=="BELI AKUN": self.f1=discord.ui.TextInput(label="Username Discord / Roblox",placeholder="Username kamu",required=True);self.f2=discord.ui.TextInput(label="Akun Yang Dicari",placeholder="Contoh: Akun Sultan, Korblox",required=True);self.f3=discord.ui.TextInput(label="Budget",placeholder="Contoh: 1jt / QRIS",required=True)
            elif jenis=="REKBER": self.f1=discord.ui.TextInput(label="Username Kamu",placeholder="Username kamu",required=True);self.f2=discord.ui.TextInput(label="Barang / Jasa Rekber",placeholder="Contoh: Rekber Akun 500k",required=True);self.f3=discord.ui.TextInput(label="Username Lawan Transaksi",placeholder="@ lawan transaksi kamu",required=True)
            elif jenis in ["OTHER","VIA KOMUNITAS","ROBLOX PLUSS"]: self.f1=discord.ui.TextInput(label="Username Roblox",placeholder="Username kamu",required=True);self.f2=discord.ui.TextInput(label="Keperluan",placeholder="Jelasin mau apa",style=discord.TextStyle.paragraph,required=True);self.f3=discord.ui.TextInput(label="Metode Pembayaran",placeholder="QRIS / DANA",required=True,default="QRIS")
            else: self.f1=discord.ui.TextInput(label="Nickname Roblox",placeholder="Nickname Roblox kamu",required=True);self.f2=discord.ui.TextInput(label="Username",placeholder="Username Roblox",required=True);self.f3=discord.ui.TextInput(label="Paket yang dipilih",placeholder="Contoh: 500 Robux",required=True)
            self.add_item(self.f1);self.add_item(self.f2);self.add_item(self.f3)
            if jenis in ["VIA SEND","VIA LOGIN","VIA KOMUNITAS"]: self.promo=discord.ui.TextInput(label="Kode Promo (Opsional)",placeholder="Kosongin aja kalau gak ada",required=False);self.add_item(self.promo);self.ref=discord.ui.TextInput(label="Kode Referral Temen (Opsional)",placeholder="Contoh: MIPI-12345 - Biar temen kamu dapet komisi!",required=False);self.add_item(self.ref)
            else: self.promo=None;self.ref=None
        except Exception as e: print(f"modal init error: {e}");self.promo=None;self.ref=None
    async def on_submit(self,interaction:discord.Interaction):
        try:
            global ticket_counter;ticket_counter+=1;guild=interaction.guild;overwrites={guild.default_role:discord.PermissionOverwrite(read_messages=False),interaction.user:discord.PermissionOverwrite(read_messages=True,send_messages=True),guild.me:discord.PermissionOverwrite(read_messages=True,send_messages=True)};category=get_ticket_category(guild);prefix=self.jenis.lower().replace(" ","-").replace("/","-");channel=await guild.create_text_channel(name=f"{prefix}-{ticket_counter}-{interaction.user.name}",overwrites=overwrites,category=category);paket_text=f"{self.jenis} - {self.f2.value}";harga_akhir=0;kategori=jenis_to_kategori(self.jenis);robux_jumlah_fix=0;ref_by=None
            if self.jenis in ["VIA SEND","VIA LOGIN","VIA KOMUNITAS"]:
                m_temp=re.search(r'(\d+)',str(self.f3.value).replace('.',''));jumlah_int=int(m_temp.group(1)) if m_temp else 500;robux_jumlah_fix=jumlah_int;harga_awal=get_harga(jumlah_int,kategori);kode_input=self.promo.value.strip() if self.promo and self.promo.value else "";harga_akhir,diskon,err_promo=cek_promo(kode_input,harga_awal,jumlah_int)
                if kode_input and not err_promo and diskon>0:
                    pdata=load_promo();k_up=kode_input.upper()
                    if k_up in pdata: pdata[k_up]["dipakai"]=pdata[k_up].get("dipakai",0)+1;save_promo(pdata)
                if self.ref and self.ref.value: ref_by=claim_referral(interaction.user.id,self.ref.value.strip())
            ticket_data[channel.id]={"user_id":interaction.user.id,"username":interaction.user.name,"nickname":self.f1.value,"roblox_username":self.f1.value,"pembayaran":"QRIS","created_at":time.time(),"last_activity":time.time(),"number":ticket_counter,"paket":paket_text,"promo":(self.promo.value if self.promo else ""),"harga_akhir":harga_akhir,"robux_jumlah":robux_jumlah_fix,"kategori":kategori,"referral_by":ref_by}
            embed=discord.Embed(title=f"Ticket Baru - {self.jenis} - {interaction.user.name}",description=f"**Jenis:** {self.jenis}\n**Data 1:** {self.f1.value}\n**Data 2:** {self.f2.value}\n**Data 3:** {self.f3.value}\n"+(f"**Promo:** {self.promo.value}\n" if self.promo and self.promo.value else "")+(f"**Referral:** {self.ref.value} (Temen kamu dapet 5%!)\n" if self.ref and self.ref.value else "")+f"\nTicket #{ticket_counter}\n\nSilahkan kirim bukti / detail disini ya 💗",color=0xff69b4);embed.set_image(url=WELCOME_URL);await channel.send(interaction.user.mention+" Halo! Selamat datang di MIPI STORE! 🌸",embed=embed,view=CloseView());embed_qris=discord.Embed(title="Scan QRIS Disini",description="Silahkan scan QRIS ini untuk pembayaran ya 💗",color=0xff69b4);embed_qris.set_image(url=QRIS_URL);await channel.send(embed=embed_qris);await channel.send("STATUS ORDER - Owner only:",view=StatusView());await send_status_update(guild,ticket_counter,interaction.user.name,interaction.user.id,paket_text,"Ticket Baru Dibuat",0xff69b4);go_view=discord.ui.View();go_view.add_item(discord.ui.Button(label="BUKA TICKET SAYA",style=discord.ButtonStyle.link,url=f"https://discord.com/channels/{guild.id}/{channel.id}",emoji="🚀"));await interaction.response.send_message(f"Ticket **{self.jenis}** kamu sudah dibuat!\nPencet tombol dibawah 👇\n{channel.mention}",view=go_view,ephemeral=True)
            try: await interaction.user.send(f"Ticket MIPI STORE kamu sudah dibuat!\nJenis: {self.jenis}\nData: {self.f1.value} | {self.f2.value}\nLink: https://discord.com/channels/{guild.id}/{channel.id}\n\nKirim bukti QRIS kamu disana ya 💗")
            except: pass
        except Exception as e:
            print(f"modal submit error: {e}");traceback.print_exc()
            try:
                if not interaction.response.is_done(): await interaction.response.send_message(f"❌ Gagal buat ticket: {e}",ephemeral=True)
                else: await interaction.followup.send(f"❌ Gagal buat ticket: {e}",ephemeral=True)
            except: pass
    async def on_error(self,interaction,error):
        print(f"modal on_error: {error}")
        try:
            if not interaction.response.is_done(): await interaction.response.send_message(f"❌ Error modal: {error}",ephemeral=True)
            else: await interaction.followup.send(f"❌ Error modal: {error}",ephemeral=True)
        except: pass
class ButtonTicket(discord.ui.Button):
    def __init__(self,label,custom_id,row,emoji):
        super().__init__(label=label,style=discord.ButtonStyle.primary,custom_id=custom_id,row=row,emoji=emoji);self.jenis_map={"t_via_send":"VIA SEND","t_via_login":"VIA LOGIN","t_beli_limited":"BELI LIMITED","t_jual_limited":"JUAL LIMITED","t_pluss":"ROBLOX PLUSS","t_offsale":"BELI ITEM OFFSALE","t_rekber":"REKBER","t_other":"OTHER","t_komunitas":"VIA KOMUNITAS","t_beli_akun":"BELI AKUN"}
    async def callback(self,interaction:discord.Interaction):
        try:
            view=TicketTypeView()
            if not await view.cek_store(interaction): return
            jenis=self.jenis_map.get(self.custom_id,"VIA SEND");kat=jenis_to_kategori(jenis);kat_stock=kat
            if jenis=="REKBER": kat_stock="rekber"
            elif jenis=="BELI AKUN": kat_stock="beli_akun"
            elif jenis=="OTHER": kat_stock="other"
            if not is_open(kat_stock):
                try: await interaction.response.send_message(f"❌ Maaf, **{jenis}** lagi **HABIS / TUTUP**! Coba kategori lain atau tunggu restock ya 💗\nMau di-notif kalo restock? Ketik `/notify {kat_stock}`!",ephemeral=True)
                except: pass
                return
            await interaction.response.send_modal(OrderModalBaru(jenis))
        except Exception as e:
            print(f"ButtonTicket callback error: {e}")
            try:
                if not interaction.response.is_done(): await interaction.response.send_message(f"❌ Error: {e}",ephemeral=True)
            except: pass
class TicketTypeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        def _label(base,kat_stock): return base if is_open(kat_stock) else base+" - HABIS"
        btns=[("Robux Via Username","t_via_send",0,"<a:robux:1563387482182254725>","via_username"),("Robux Vlog","t_via_login",0,"<:emoji_10:1431192496876027975>","via_login"),("Beli Limited Item","t_beli_limited",1,"<a:diamond:1516624681585869041>","limited"),("Jual Limited Item","t_jual_limited",1,"<a:moneybag:1512329138172596265>","limited"),("Beli Roblox Plus","t_pluss",2,"<:b_RobloxPlus:1499160341983006730>","plus"),("Beli Item Offsale","t_offsale",2,"<a:emoji_20:1550165111333986354>","limited"),("Rekber/MM","t_rekber",3,"<a:emoji_39:1555770513907916822>","rekber"),("Other/Nanya","t_other",3,"<a:b_bluequestion:1345684551502008340>","other"),("Via Komunitas","t_komunitas",4,"<a:rbx:1530537752729223308>","via_komunitas"),("Beli Akun","t_beli_akun",4,"<a:star_purple:1303353812374913035>","beli_akun")]
        for label,cid,row,emoji,kat_stock in btns:
            b=ButtonTicket(_label(label,kat_stock),cid,row=row,emoji=emoji)
            if not is_open(kat_stock): b.disabled=True;b.style=discord.ButtonStyle.secondary
            self.add_item(b)
    async def cek_store(self,interaction):
        try:
            if STORE_STATUS=="break":
                embed=discord.Embed(color=0xfee75c);embed.description="MIPI STORE LAGI BREAK! ☕\n\nMimin break sebentar yaa, 15-30 menit aja!";await interaction.response.send_message(embed=embed,ephemeral=True);return False
            if STORE_STATUS=="closed":
                embed=discord.Embed(color=0xff0000);embed.description="MIPI STORE UDAH TUTUP! 💤\n\nBalik besok yaa!";await interaction.response.send_message(embed=embed,ephemeral=True);return False
            return True
        except Exception as e: print(f"cek_store error: {e}");return False
OrderView=TicketTypeView
@bot.event
async def on_message(message):
    try:
        if message.author.bot: return
        if message.guild and "market" in message.channel.name.lower():
            if message.author.id!=message.guild.owner_id and not message.author.guild_permissions.administrator:
                if is_banned_selling(message.content) or is_scam_link(message.content):
                    try: await message.delete()
                    except: pass
                    embed=discord.Embed(title="Stickied Message:",description="DILARANG MENJUAL PRODUK YANG KAMI JUAL / LINK SCAM!",color=0xff0000);warn=await message.channel.send(message.author.mention,embed=embed);await asyncio.sleep(10)
                    try: await warn.delete()
                    except: pass
                    try: await message.author.send("Pesan kamu di #"+message.channel.name+" dihapus!\n\nAlasan: Dilarang menjual produk yang kami jual / link scam di MIPI STORE!")
                    except: pass
                    return
        if message.channel.id in ticket_data: ticket_data[message.channel.id]["last_activity"]=time.time()
        await bot.process_commands(message)
    except Exception as e: print(f"on_message error: {e}")
@bot.event
async def on_ready():
    try:
        print(f"Login {bot.user} - MIPI STORE V4 SUPER STORE!");bot.add_view(OrderView());bot.add_view(TicketTypeView());bot.add_view(CloseView());bot.add_view(StatusView());bot.add_view(RatingView(0));bot.add_view(SaldoView());bot.add_view(GiveawayView("dummy"))
        for oid in load_pending().keys():
            try: bot.add_view(KonfirmasiSaldoView(oid))
            except: pass
        if not check_inactive.is_running(): check_inactive.start()
        if not auto_update_top_sultan.is_running(): auto_update_top_sultan.start()
        if not auto_rekap_omset.is_running(): auto_rekap_omset.start()
        for g in bot.guilds:
            try: await update_top_sultan(g)
            except: pass
        try:
            synced=await bot.tree.sync();print(f"Synced {len(synced)} commands - V4!")
        except Exception as e: print(f"Sync error: {e}")
    except Exception as e: print(f"on_ready error: {e}");traceback.print_exc()
PANEL_FILE="panel.json"
def load_panel():
    try:
        with open(PANEL_FILE,"r") as f: return json.load(f)
    except: return {}
def save_panel(d):
    try:
        with open(PANEL_FILE,"w") as f: json.dump(d,f,indent=2)
    except Exception as e: print(f"save panel error: {e}")
async def update_all_panels(guild):
    try:
        panels=load_panel()
        for key,info in list(panels.items()):
            try:
                ch=guild.get_channel(int(info["channel_id"]))
                if not ch: continue
                msg=await ch.fetch_message(int(info["message_id"]))
                if key=="ticket": await msg.edit(embed=build_ticket_panel_baru_embed(),view=TicketTypeView())
                elif key=="pricelist": await msg.edit(embeds=build_all_pricelist_embeds())
            except Exception as e: print(f"update panel {key} error: {e}")
    except Exception as e: print(f"update_all_panels error: {e}")
async def refresh_ticket_panel(guild):
    try: await update_all_panels(guild)
    except Exception as e: print(f"refresh panel error: {e}")
# === SLASH COMMANDS V4 ===
@bot.tree.command(name="ticket",description="Tampilkan panel order MIPI STORE")
async def ticket(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=False)
    try:
        if STORE_STATUS!="open":
            st="BREAK - Mimin break 15-30 menit!" if STORE_STATUS=="break" else "CLOSED - Toko tutup, balik besok yaa!";await safe_followup(interaction,content=st+"\n\nTicket lagi dikunci sementara! Tunggu OPEN lagi yaa! 💗",ephemeral=True);return
        ch_target=interaction.guild.get_channel(OPEN_TICKET_CHANNEL_ID) or interaction.channel;panels=load_panel()
        if "ticket" in panels:
            try:
                ch=interaction.guild.get_channel(int(panels["ticket"]["channel_id"]));msg=await ch.fetch_message(int(panels["ticket"]["message_id"]));await msg.edit(embed=build_ticket_panel_baru_embed(),view=TicketTypeView());await safe_followup(interaction,content=f"✅ Panel udah di-update jadi 10 tombol baru! Cek {ch.mention}",ephemeral=True);return
            except Exception as e: print(f"edit old panel gagal, kirim baru: {e}")
        msg=await ch_target.send(embed=build_ticket_panel_baru_embed(),view=TicketTypeView());panels["ticket"]={"channel_id":str(msg.channel.id),"message_id":str(msg.id)};save_panel(panels);await safe_followup(interaction,content=f"✅ Panel ticket udah dikirim ke {ch_target.mention}!",ephemeral=True)
    except Exception as e: print(f"ERROR /ticket: {e}");traceback.print_exc();await safe_followup(interaction,content=f"❌ Error /ticket: {e}",ephemeral=True)
@bot.tree.command(name="setup-ticket",description="Kirim panel ticket order (Owner only)")
async def setup_ticket(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        if interaction.user.id!=interaction.guild.owner_id: await safe_followup(interaction,content="Hanya Owner!",ephemeral=True);return
        ch_target=interaction.guild.get_channel(OPEN_TICKET_CHANNEL_ID) or interaction.channel;msg=await ch_target.send(embed=build_ticket_panel_baru_embed(),view=TicketTypeView());panels=load_panel();panels["ticket"]={"channel_id":str(msg.channel.id),"message_id":str(msg.id)};save_panel(panels);await safe_followup(interaction,content=f"✅ Panel dikirim ke {ch_target.mention}!",ephemeral=True)
    except Exception as e: print(f"ERROR /setup-ticket: {e}");await safe_followup(interaction,content=f"❌ Error: {e}",ephemeral=True)
@bot.tree.command(name="open",description="Buka toko")
async def open_cmd(interaction:discord.Interaction):
    global STORE_STATUS;await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Cuma admin!",ephemeral=True);return
        STORE_STATUS="open";await safe_followup(interaction,content="✅ Mipi Store **DIBUKA**! Ticket bisa dipencet lagi!")
    except Exception as e: await safe_followup(interaction,content=f"❌ Error: {e}",ephemeral=True)
@bot.tree.command(name="break",description="Toko break sebentar")
async def break_cmd(interaction:discord.Interaction):
    global STORE_STATUS;await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Cuma admin!",ephemeral=True);return
        STORE_STATUS="break";await safe_followup(interaction,content="☕ Mipi Store **BREAK** 15-30 menit! Ticket dikunci sementara!")
    except Exception as e: await safe_followup(interaction,content=f"❌ Error: {e}",ephemeral=True)
@bot.tree.command(name="close",description="Tutup toko")
async def close_cmd(interaction:discord.Interaction):
    global STORE_STATUS;await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Cuma admin!",ephemeral=True);return
        STORE_STATUS="closed";await safe_followup(interaction,content="💤 Mipi Store **TUTUP**! Ticket dikunci, balik besok yaa!")
    except Exception as e: await safe_followup(interaction,content=f"❌ Error: {e}",ephemeral=True)
@bot.tree.command(name="pricelist-visend",description="Pricelist Via Username Modern Elegan")
async def pricelist_visend(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try: e=build_pricelist_embed("via_username");await interaction.channel.send(embed=e);await safe_followup(interaction,content="✅ Pricelist Visend Modern dikirim!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="pricelist-vilog",description="Pricelist Via Login")
async def pricelist_vilog(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try: e=build_pricelist_embed("via_login");await interaction.channel.send(embed=e);await safe_followup(interaction,content="✅ Pricelist Vilog dikirim!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="pricelist-plus",description="Pricelist Roblox Plus")
async def pricelist_plus(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try: e=build_pricelist_embed("plus");await interaction.channel.send(embed=e);await safe_followup(interaction,content="✅ Pricelist Plus dikirim!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="pricelist-komunitas",description="Pricelist Via Komunitas")
async def pricelist_komunitas(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try: e=build_pricelist_embed("via_komunitas");await interaction.channel.send(embed=e);await safe_followup(interaction,content="✅ Pricelist Komunitas dikirim!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="pricelist-rekber",description="Pricelist Rekber Elegan")
async def pricelist_rekber(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try: await interaction.channel.send(embed=build_rekber_embed(),view=RekberView(guild_id=interaction.guild.id));await safe_followup(interaction,content="✅ Pricelist Rekber Elegan dikirim & dialihin ke #open-ticket!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="setup-rekber",description="Kirim panel Rekber Elegan ke #open-ticket (Owner)")
async def setup_rekber(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        if interaction.user.id!=interaction.guild.owner_id: await safe_followup(interaction,content="Hanya Owner!",ephemeral=True);return
        ch=interaction.guild.get_channel(OPEN_TICKET_CHANNEL_ID)
        if not ch: await safe_followup(interaction,content="❌ Channel open-ticket gak ketemu!",ephemeral=True);return
        msg=await ch.send(embed=build_rekber_embed(),view=RekberView(guild_id=interaction.guild.id));panels=load_panel();panels["rekber"]={"channel_id":str(msg.channel.id),"message_id":str(msg.id)};save_panel(panels);await safe_followup(interaction,content=f"✅ Panel Rekber Elegan udah dialihin ke {ch.mention}!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ Error: {e}",ephemeral=True)
@bot.tree.command(name="tutup-kategori",description="Tutup 1 tombol biar gak bisa dipencet (Stok Habis) - Admin")
async def tutup_kategori(interaction:discord.Interaction,kategori:str):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin / Owner!",ephemeral=True);return
        kat=kategori_alias(kategori);set_stock(kat,False)
        try: await refresh_ticket_panel(interaction.guild)
        except: pass
        await safe_followup(interaction,content=f"🔴 **{kat.upper()} DITUTUP!**\nTombolnya sekarang abu-abu & gak bisa dipencet!\nBuka lagi: `/buka-kategori {kat}`",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="buka-kategori",description="Buka lagi 1 tombol yang tadi ditutup (Restock) - Admin")
async def buka_kategori(interaction:discord.Interaction,kategori:str):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin / Owner!",ephemeral=True);return
        kat=kategori_alias(kategori);set_stock(kat,True)
        try: await refresh_ticket_panel(interaction.guild)
        except: pass
        # V4: Kirim notif restock ke yang udah /notify
        try: await send_notify_restock(interaction.guild,kat)
        except: pass
        await safe_followup(interaction,content=f"🟢 **{kat.upper()} DIBUKA LAGI!**\nTombolnya udah bisa dipencet lagi! ✨\nYang udah /notify udah di-DM otomatis!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="cek-stock",description="Cek tombol mana aja yang BUKA / TUTUP")
async def cek_stock(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        s=load_stock();all_kat=["via_username","via_login","via_komunitas","plus","limited","rekber","beli_akun","other"];txt="📦 **STATUS STOCK MIPI STORE**\n\n"
        for k in all_kat:
            v=s.get(k,True);txt+=f"{'🟢 BUKA' if v else '🔴 HABIS / TUTUP'}  —  {k}\n"
        txt+="\nTutup: `/tutup-kategori plus`\nBuka: `/buka-kategori plus`";await safe_followup(interaction,content=txt,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="notify",description="Dapet DM otomatis kalo stok yang kamu mau restock!")
async def notify_cmd(interaction:discord.Interaction,kategori:str):
    await safe_defer(interaction,ephemeral=True)
    try:
        kat=kategori_alias(kategori);add_notify(interaction.user.id,kat);await safe_followup(interaction,content=f"🔔 Oke! Kalo **{kat}** restock / dibuka lagi, kamu langsung aku DM! 💗",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="add-saldo-bulanan",description="Tambah saldo ke Leaderboard BULANAN (Admin)")
async def add_saldo_bulanan(interaction:discord.Interaction,user:discord.User,robux:int,kategori:str="via_username"):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin / Owner!",ephemeral=True);return
        kat=kategori_alias(kategori);add_to_leaderboard(user.id,user.name,f"{robux} Robux",kategori=kat);await safe_followup(interaction,content=f"✅ **SALDO BULANAN DITAMBAH!**\nBuyer: {user.mention}\n+{robux} R$ ({format_rp(get_harga(robux,kat))})\n\n📅 Masuk **Top Sultan Bulanan** ({datetime.now().strftime('%B %Y')})\n👑 Otomatis kehitung juga di **Top Sultan All Time**!",ephemeral=True)
        try: await update_top_sultan(interaction.guild)
        except: pass
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="add-saldo-leaderboard",description="Tambah saldo ke Leaderboard SEMUA / ALL TIME (Admin)")
async def add_saldo_leaderboard(interaction:discord.Interaction,user:discord.User,robux:int,kategori:str="via_username"):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin / Owner!",ephemeral=True);return
        kat=kategori_alias(kategori);add_to_leaderboard(user.id,user.name,f"{robux} Robux",kategori=kat);add_saldo_alltime_only(user.id,user.name,robux,kategori=kat);await safe_followup(interaction,content=f"✅ **SALDO LEADERBOARD DITAMBAH!**\nBuyer: {user.mention}\n+{robux} R$ ({format_rp(get_harga(robux,kat))})\n\n👑 Masuk **Top Sultan SEMUA / ALL TIME**\n📅 Masuk juga ke **Top Sultan Bulanan**!",ephemeral=True)
        try: await update_top_sultan(interaction.guild)
        except: pass
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="add-saldo",description="Tambah saldo manual (masuk Bulanan + All Time)")
async def add_saldo(interaction:discord.Interaction,user:discord.User,robux:int,kategori:str="via_username"):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin / Owner!",ephemeral=True);return
        kat=kategori_alias(kategori);add_to_leaderboard(user.id,user.name,f"{robux} Robux",kategori=kat);await safe_followup(interaction,content=f"✅ Saldo ditambah! {user.mention} +{robux} R$ masuk **Bulanan + All Time**!",ephemeral=True)
        try: await update_top_sultan(interaction.guild)
        except: pass
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="leaderboard-bulanan",description="Lihat Top Sultan Bulanan")
async def lb_bulanan(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try: e=build_top_sultan_embed_bulanan();await safe_followup(interaction,embed=e,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="leaderboard-semua",description="Lihat Top Sultan Semua / All Time")
async def lb_semua(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try: e=build_top_sultan_embed_semua();await safe_followup(interaction,embed=e,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="lihat-harga",description="Lihat semua harga pricelist")
async def lihat_harga(interaction:discord.Interaction,kategori:str="via_username"):
    await safe_defer(interaction,ephemeral=True)
    try: kat=kategori_alias(kategori);e=build_pricelist_embed(kat);await safe_followup(interaction,embed=e,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="set-harga",description="Set harga pricelist per nominal (Admin)")
async def set_harga(interaction:discord.Interaction,kategori:str,robux:int,harga:int):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin / Owner!",ephemeral=True);return
        kat=kategori_alias(kategori);d=load_pricelist(kat);d[int(robux)]=int(harga);save_pricelist(d,kat);await safe_followup(interaction,content=f"✅ Harga {kat} {robux} R$ jadi {format_rp(harga)}!",ephemeral=True)
        try: await update_all_panels(interaction.guild)
        except: pass
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="saldo",description="Cek saldo / total belanja kamu + level + poin")
async def saldo_cmd(interaction:discord.Interaction,user:discord.User=None):
    await safe_defer(interaction,ephemeral=True)
    try:
        target=user or interaction.user;tr,tro,tt=get_total_belanja(target.id);lvl=get_level(tr);nxt,sisa=get_next_level(tr);poin=get_poin(target.id);embed=discord.Embed(color=0xff1493);embed.description=f"INFORMASI SALDO / TOTAL TRANSAKSI\n\nHalo {target.mention},\n\n🏆 Level: {lvl}\n➡️ Next: {nxt} (kurang {format_rp(sisa)})\n\nTotal Belanja: {format_rp(tr)}\nTotal Robux: {tro} R$\nTotal Transaksi: {tt}x\n🎁 Poin Daily: {poin} poin\n\nMIPI STORE - CHECK SALDO";embed.set_footer(text="Mipi Store - Rafi Store");await safe_followup(interaction,embed=embed,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="cek-saldo",description="Cek saldo kamu (tombol)")
async def cek_saldo_cmd(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try: await safe_followup(interaction,content="Pencet tombol di bawah buat cek saldo kamu!",view=SaldoView(),ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="top-sultan",description="Lihat Top Sultan")
async def top_sultan_cmd(interaction:discord.Interaction,jenis:str="semua"):
    await safe_defer(interaction,ephemeral=True)
    try:
        e=build_top_sultan_embed_bulanan() if "bulan" in jenis.lower() else build_top_sultan_embed_semua();await safe_followup(interaction,embed=e,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="statistik",description="Lihat statistik omset real-time MIPI STORE")
async def statistik_cmd(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        s=get_statistik();e=discord.Embed(title="📊 STATISTIK MIPI STORE - REAL TIME",description=f"📅 **Hari Ini:** {format_rp(s['hari_rp'])} ({s['hari_tr']} pending hari ini)\n📅 **Bulan Ini ({datetime.now().strftime('%B %Y')}):** {format_rp(s['bulan_rp'])} ({s['bulan_tr']} transaksi)\n👑 **All Time:** {format_rp(s['all_rp'])} ({s['all_tr']} transaksi)\n\n💗 Mipi Store — Rafi Store",color=0xff69b4);await safe_followup(interaction,embed=e,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
# === V4: REFERRAL COMMANDS ===
@bot.tree.command(name="referral",description="Lihat kode referral kamu + komisi kamu")
async def referral_cmd(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        data=load_referral();uid=str(interaction.user.id);code=get_referral_code(interaction.user.id)
        if uid not in data: data[uid]={"code":code,"total_komisi":0,"total_referral":0,"history":[]};save_referral(data)
        info=data[uid];txt=f"💸 **REFERRAL KAMU**\n\n🔑 Kode kamu: **{info['code']}**\nKasih kode ini ke temen kamu, suruh dia isi di modal order!\n\n💰 Total Komisi: {format_rp(info['total_komisi'])}\n👥 Total Temen yang Order: {info['total_referral']} orang\n\nCara: Temen order -> isi kode kamu -> kamu dapet 5% otomatis!\n💗 Mipi Store";await safe_followup(interaction,content=txt,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="daily",description="Claim daily reward dapet poin!")
async def daily_cmd(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        bonus,total,err=claim_daily(interaction.user.id)
        if err: await safe_followup(interaction,content=f"❌ {err}\nPoin kamu: {total} poin",ephemeral=True)
        else: await safe_followup(interaction,content=f"🎁 **DAILY CLAIM BERHASIL!**\nKamu dapet +{bonus} poin!\nTotal poin: {total} poin\n\nKumpulin 100 poin = bisa dituker 100 Robux! Ketik `/tuker-poin 100`!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="tuker-poin",description="Tuker poin daily jadi Robux!")
async def tuker_poin(interaction:discord.Interaction,jumlah:int):
    await safe_defer(interaction,ephemeral=True)
    try:
        poin=get_poin(interaction.user.id)
        if poin<jumlah: await safe_followup(interaction,content=f"❌ Poin kamu cuma {poin}, gak cukup buat tuker {jumlah}!",ephemeral=True);return
        if jumlah<100: await safe_followup(interaction,content="❌ Minimal tuker 100 poin = 100 Robux!",ephemeral=True);return
        if not use_poin(interaction.user.id,jumlah): await safe_followup(interaction,content="❌ Gagal tuker poin!",ephemeral=True);return
        # Masuk pending biar admin proses
        oid=add_to_pending(interaction.user.id,interaction.user.name,f"TUKER POIN - {jumlah} Robux",999999,f"tuker-poin-{interaction.user.name}",kategori="via_username",robux_jumlah=jumlah,harga_akhir=0)
        await safe_followup(interaction,content=f"✅ **TUKER POIN BERHASIL!**\n-{jumlah} poin\n+{jumlah} Robux masuk PENDING!\nAdmin bakal proses & kirim robux kamu! Order ID: {oid}",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
# === V4: VOUCHER ===
@bot.tree.command(name="buat-voucher",description="Bikin voucher diskon (Admin)")
async def buat_voucher(interaction:discord.Interaction,kode:str,diskon:int,tipe:str="persen",max_pakai:int=10):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin / Owner!",ephemeral=True);return
        data=load_voucher();data[kode.upper()]={"diskon":int(diskon),"tipe":tipe.lower(),"max":int(max_pakai),"dipakai":0,"used_by":[]};save_voucher(data);await safe_followup(interaction,content=f"✅ Voucher **{kode.upper()}** dibuat! Diskon {diskon} {tipe}, max {max_pakai}x!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="redeem-voucher",description="Redeem voucher dapet diskon!")
async def redeem_voucher_cmd(interaction:discord.Interaction,kode:str):
    await safe_defer(interaction,ephemeral=True)
    try:
        v,err=redeem_voucher(interaction.user.id,kode)
        if err: await safe_followup(interaction,content=f"❌ {err}",ephemeral=True)
        else: await safe_followup(interaction,content=f"✅ **VOUCHER DIREDEEM!**\nKode: {kode.upper()}\nDiskon: {v['diskon']} {v['tipe']}\n\nSS ini & kasih ke admin pas order, biar harganya dipotong! 💗",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="lihat-voucher",description="Lihat semua voucher yang ada")
async def lihat_voucher(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        data=load_voucher()
        if not data: await safe_followup(interaction,content="Belum ada voucher!",ephemeral=True);return
        txt="🎁 **DAFTAR VOUCHER MIPI STORE**\n\n"
        for k,v in data.items(): txt+=f"**{k}** — Diskon {v.get('diskon')} {v.get('tipe')} — Dipakai {v.get('dipakai',0)}/{v.get('max',1)}\n"
        await safe_followup(interaction,content=txt,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
# === V4: GAME TEBAK HARGA ===
@bot.tree.command(name="tebak-harga",description="Main tebak harga, menang dapet voucher!")
async def tebak_harga(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        nominal,harga,pilihan=start_tebak_harga();game_data[interaction.user.id]={"nominal":nominal,"harga":harga,"pilihan":pilihan};txt=f"🎮 **TEBAK HARGA - MIPI STORE**\n\nBerapa harga **{nominal} Robux Via Username**?\n\n"
        for i,p in enumerate(pilihan,1): txt+=f"{i}. {format_rp(p)}\n"
        txt+="\nJawab pake `/jawab-tebak <nomor>`! Benar = dapet voucher 5%!";await safe_followup(interaction,content=txt,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="jawab-tebak",description="Jawab game tebak harga!")
async def jawab_tebak(interaction:discord.Interaction,nomor:int):
    await safe_defer(interaction,ephemeral=True)
    try:
        if interaction.user.id not in game_data: await safe_followup(interaction,content="❌ Kamu belum mulai game! Ketik `/tebak-harga` dulu!",ephemeral=True);return
        g=game_data.pop(interaction.user.id);pilihan=g["pilihan"]
        if nomor<1 or nomor>len(pilihan): await safe_followup(interaction,content="❌ Nomor gak valid!",ephemeral=True);return
        if pilihan[nomor-1]==g["harga"]:
            kode=f"GAME-{interaction.user.id%10000:04d}";data=load_voucher();data[kode]={"diskon":5,"tipe":"persen","max":1,"dipakai":0,"used_by":[]};save_voucher(data);await safe_followup(interaction,content=f"🎉 **BENAR!** Harga {g['nominal']} Robux emang {format_rp(g['harga'])}!\nKamu dapet voucher **{kode}** (Diskon 5%)! Redeem pake `/redeem-voucher {kode}`!",ephemeral=True)
        else: await safe_followup(interaction,content=f"❌ Salah! Harga {g['nominal']} Robux itu {format_rp(g['harga'])}, bukan {format_rp(pilihan[nomor-1])}! Coba lagi pake `/tebak-harga`!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="tambah-promo",description="Tambah kode promo (Admin)")
async def tambah_promo(interaction:discord.Interaction,kode:str,diskon:int,tipe:str="persen",max_pakai:int=999):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin / Owner!",ephemeral=True);return
        data=load_promo();data[kode.upper()]={"diskon":int(diskon),"tipe":tipe.lower(),"max":int(max_pakai),"dipakai":0};save_promo(data);await safe_followup(interaction,content=f"✅ Promo **{kode.upper()}** ditambah! Diskon {diskon} {tipe}, max {max_pakai}x pakai!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="lihat-promo",description="Lihat semua kode promo")
async def lihat_promo(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        data=load_promo()
        if not data: await safe_followup(interaction,content="Belum ada promo!",ephemeral=True);return
        txt="🎁 **DAFTAR PROMO MIPI STORE**\n\n"
        for k,v in data.items(): txt+=f"**{k}** — Diskon {v.get('diskon')} {v.get('tipe')} — Dipakai {v.get('dipakai',0)}/{v.get('max',999)}\n"
        await safe_followup(interaction,content=txt,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="hapus-promo",description="Hapus kode promo (Admin)")
async def hapus_promo(interaction:discord.Interaction,kode:str):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin / Owner!",ephemeral=True);return
        data=load_promo();k=kode.upper()
        if k in data: del data[k];save_promo(data);await safe_followup(interaction,content=f"✅ Promo **{k}** dihapus!",ephemeral=True)
        else: await safe_followup(interaction,content="❌ Promo gak ketemu!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="giveaway",description="Bikin giveaway (Admin)")
async def giveaway_cmd(interaction:discord.Interaction,hadiah:str,pemenang:int=1,menit:int=60):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin / Owner!",ephemeral=True);return
        gid=f"GW-{int(time.time())}";giveaway_data[gid]={"hadiah":hadiah,"host_mention":interaction.user.mention,"peserta":[],"pemenang":int(pemenang),"ended":False};e=discord.Embed(title="🎉 GIVEAWAY MIPI STORE!",description=f"Hadiah: {hadiah}\nHost: {interaction.user.mention}\nPeserta: 0 orang",color=0xff69b4);msg=await interaction.channel.send(embed=e,view=GiveawayView(gid));await safe_followup(interaction,content=f"✅ Giveaway **{hadiah}** dibuat! Berakhir {menit} menit lagi!",ephemeral=True);await asyncio.sleep(int(menit)*60);await end_giveaway(interaction.guild,msg.channel.id,msg.id,gid)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="pending",description="Lihat semua pending saldo (Admin)")
async def pending_cmd(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin / Owner!",ephemeral=True);return
        data=load_pending()
        if not data: await safe_followup(interaction,content="✅ Gak ada pending! Semua udah dikonfirmasi!",ephemeral=True);return
        txt="⏳ **PENDING SALDO - BELUM DIKONFIRMASI**\n\n"
        for oid,d in data.items(): txt+=f"**{oid}** — <@{d['user_id']}> — {d['paket']} — {d['robux']} R$ — {format_rp(d['harga'])}\n"
        txt+="\nAdmin harus pencet ✅ di channel history / order-status buat masukin ke leaderboard!";await safe_followup(interaction,content=txt,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="tolak-pending",description="Tolak 1 pending saldo (Admin)")
async def tolak_pending(interaction:discord.Interaction,order_id:str):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin / Owner!",ephemeral=True);return
        data=load_pending();oid=order_id.upper()
        if oid in data: del data[oid];save_pending(data);await safe_followup(interaction,content=f"❌ {oid} ditolak, gak masuk saldo!",ephemeral=True)
        else: await safe_followup(interaction,content="❌ Order ID gak ketemu!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="konfirmasi-pending",description="Konfirmasi 1 pending saldo manual (Admin)")
async def konfirmasi_pending(interaction:discord.Interaction,order_id:str):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin / Owner!",ephemeral=True);return
        data=load_pending();oid=order_id.upper()
        if oid not in data: await safe_followup(interaction,content="❌ Order ID gak ketemu / udah diproses!",ephemeral=True);return
        d=data.pop(oid);save_pending(data);add_to_leaderboard(int(d["user_id"]),d["username"],d["paket"],kategori=d.get("kategori","via_username"));await safe_followup(interaction,content=f"✅ {oid} dikonfirmasi! <@{d['user_id']}> +{d['robux']} R$ masuk Bulanan + All Time!",ephemeral=True)
        try: await update_top_sultan(interaction.guild)
        except: pass
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="setup-top-sultan",description="Setup panel Top Sultan (Owner)")
async def setup_top_sultan(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        if interaction.user.id!=interaction.guild.owner_id: await safe_followup(interaction,content="Hanya Owner!",ephemeral=True);return
        e=build_top_sultan_embed_semua();msg=await interaction.channel.send(embed=e);await safe_followup(interaction,content="✅ Top Sultan di-setup di channel ini! Pindah / rename channel ini jadi #top-sultan biar auto-update!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="pricelist-all",description="Kirim semua pricelist sekaligus")
async def pricelist_all(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        for emb in build_all_pricelist_embeds(): await interaction.channel.send(embed=emb)
        await safe_followup(interaction,content="✅ Semua pricelist dikirim!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="help-mipi",description="Lihat semua command MIPI STORE V4")
async def help_mipi(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        txt=("💗 **HELP - MIPI STORE V4 SUPER STORE**\n\n**ORDER:**\n`/ticket` - Panel order\n`/pricelist-visend` `/pricelist-vilog` `/pricelist-plus` `/pricelist-komunitas` `/pricelist-rekber` `/pricelist-all`\n\n**SALDO / LEADERBOARD:**\n`/saldo` `/cek-saldo` `/top-sultan` `/leaderboard-bulanan` `/leaderboard-semua`\n`/add-saldo` `/add-saldo-bulanan` `/add-saldo-leaderboard`\n`/pending` `/konfirmasi-pending` `/tolak-pending`\n\n**STOCK / TOMBOL:**\n`/tutup-kategori` `/buka-kategori` `/cek-stock` `/notify`\n\n**V4 BARU - YANG BIKIN STORE BESAR KALAH:**\n`/referral` - Kode referral + komisi 5%\n`/daily` `/tuker-poin` - Daily reward\n`/buat-voucher` `/redeem-voucher` `/lihat-voucher` - Voucher\n`/tebak-harga` `/jawab-tebak` - Game\n`/statistik` - Omset real-time\n\n**TOKO:**\n`/open` `/break` `/close`\n\n**ADMIN:**\n`/set-harga` `/lihat-harga` `/tambah-promo` `/lihat-promo` `/hapus-promo` `/giveaway` `/setup-rekber` `/setup-top-sultan`\n");await safe_followup(interaction,content=txt,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
        # === SAMBUNGAN DARI YANG KEPOTONG TADI - LANJUTAN on_submit ===
            embed=discord.Embed(title=f"Ticket Baru - {self.jenis} - {interaction.user.name}",description=f"**Jenis:** {self.jenis}\n**Data 1:** {self.f1.value}\n**Data 2:** {self.f2.value}\n**Data 3:** {self.f3.value}\n"+(f"**Promo:** {self.promo.value}\n" if self.promo and self.promo.value else "")+(f"**Referral:** {self.ref.value} (Temen kamu dapet 5%!)\n" if self.ref and self.ref.value else "")+f"\nTicket #{ticket_counter}\n\nSilahkan kirim bukti / detail disini ya 💗",color=0xff69b4);embed.set_image(url=WELCOME_URL);await channel.send(interaction.user.mention+" Halo! Selamat datang di MIPI STORE! 🌸",embed=embed,view=CloseView());embed_qris=discord.Embed(title="Scan QRIS Disini",description="Silahkan scan QRIS ini untuk pembayaran ya 💗",color=0xff69b4);embed_qris.set_image(url=QRIS_URL);await channel.send(embed=embed_qris);await channel.send("STATUS ORDER - Owner only:",view=StatusView());await send_status_update(guild,ticket_counter,interaction.user.name,interaction.user.id,paket_text,"Ticket Baru Dibuat",0xff69b4);go_view=discord.ui.View();go_view.add_item(discord.ui.Button(label="BUKA TICKET SAYA",style=discord.ButtonStyle.link,url=f"https://discord.com/channels/{guild.id}/{channel.id}",emoji="🚀"));await interaction.response.send_message(f"Ticket **{self.jenis}** kamu sudah dibuat!\nPencet tombol dibawah 👇\n{channel.mention}",view=go_view,ephemeral=True)
            try: await interaction.user.send(f"Ticket MIPI STORE kamu sudah dibuat!\nJenis: {self.jenis}\nData: {self.f1.value} | {self.f2.value}\nLink: https://discord.com/channels/{guild.id}/{channel.id}\n\nKirim bukti QRIS kamu disana ya 💗")
            except: pass
        except Exception as e:
            print(f"modal submit error: {e}");traceback.print_exc()
            try:
                if not interaction.response.is_done(): await interaction.response.send_message(f"❌ Gagal buat ticket: {e}",ephemeral=True)
                else: await interaction.followup.send(f"❌ Gagal buat ticket: {e}",ephemeral=True)
            except: pass
    async def on_error(self,interaction,error):
        print(f"modal on_error: {error}")
        try:
            if not interaction.response.is_done(): await interaction.response.send_message(f"❌ Error modal: {error}",ephemeral=True)
            else: await interaction.followup.send(f"❌ Error modal: {error}",ephemeral=True)
        except: pass
class ButtonTicket(discord.ui.Button):
    def __init__(self,label,custom_id,row,emoji):
        super().__init__(label=label,style=discord.ButtonStyle.primary,custom_id=custom_id,row=row,emoji=emoji);self.jenis_map={"t_via_send":"VIA SEND","t_via_login":"VIA LOGIN","t_beli_limited":"BELI LIMITED","t_jual_limited":"JUAL LIMITED","t_pluss":"ROBLOX PLUSS","t_offsale":"BELI ITEM OFFSALE","t_rekber":"REKBER","t_other":"OTHER","t_komunitas":"VIA KOMUNITAS","t_beli_akun":"BELI AKUN"}
    async def callback(self,interaction:discord.Interaction):
        try:
            view=TicketTypeView()
            if not await view.cek_store(interaction): return
            jenis=self.jenis_map.get(self.custom_id,"VIA SEND");kat=jenis_to_kategori(jenis);kat_stock=kat
            if jenis=="REKBER": kat_stock="rekber"
            elif jenis=="BELI AKUN": kat_stock="beli_akun"
            elif jenis=="OTHER": kat_stock="other"
            if not is_open(kat_stock):
                try: await interaction.response.send_message(f"❌ Maaf, **{jenis}** lagi **HABIS / TUTUP**! Coba kategori lain atau tunggu restock ya 💗\nMau di-notif kalo restock? Ketik `/notify {kat_stock}`!",ephemeral=True)
                except: pass
                return
            await interaction.response.send_modal(OrderModalBaru(jenis))
        except Exception as e:
            print(f"ButtonTicket callback error: {e}")
            try:
                if not interaction.response.is_done(): await interaction.response.send_message(f"❌ Error: {e}",ephemeral=True)
            except: pass
class TicketTypeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        def _label(base,kat_stock): return base if is_open(kat_stock) else base+" - HABIS"
        btns=[("Robux Via Username","t_via_send",0,"<a:robux:1563387482182254725>","via_username"),("Robux Vlog","t_via_login",0,"<:emoji_10:1431192496876027975>","via_login"),("Beli Limited Item","t_beli_limited",1,"<a:diamond:1516624681585869041>","limited"),("Jual Limited Item","t_jual_limited",1,"<a:moneybag:1512329138172596265>","limited"),("Beli Roblox Plus","t_pluss",2,"<:b_RobloxPlus:1499160341983006730>","plus"),("Beli Item Offsale","t_offsale",2,"<a:emoji_20:1550165111333986354>","limited"),("Rekber/MM","t_rekber",3,"<a:emoji_39:1555770513907916822>","rekber"),("Other/Nanya","t_other",3,"<a:b_bluequestion:1345684551502008340>","other"),("Via Komunitas","t_komunitas",4,"<a:rbx:1530537752729223308>","via_komunitas"),("Beli Akun","t_beli_akun",4,"<a:star_purple:1303353812374913035>","beli_akun")]
        for label,cid,row,emoji,kat_stock in btns:
            b=ButtonTicket(_label(label,kat_stock),cid,row=row,emoji=emoji)
            if not is_open(kat_stock): b.disabled=True;b.style=discord.ButtonStyle.secondary
            self.add_item(b)
    async def cek_store(self,interaction):
        try:
            if STORE_STATUS=="break":
                embed=discord.Embed(color=0xfee75c);embed.description="MIPI STORE LAGI BREAK! ☕\n\nMimin break sebentar yaa, 15-30 menit aja!";await interaction.response.send_message(embed=embed,ephemeral=True);return False
            if STORE_STATUS=="closed":
                embed=discord.Embed(color=0xff0000);embed.description="MIPI STORE UDAH TUTUP! 💤\n\nBalik besok yaa!";await interaction.response.send_message(embed=embed,ephemeral=True);return False
            return True
        except Exception as e: print(f"cek_store error: {e}");return False
OrderView=TicketTypeView
@bot.event
async def on_message(message):
    try:
        if message.author.bot: return
        if message.guild and "market" in message.channel.name.lower():
            if message.author.id!=message.guild.owner_id and not message.author.guild_permissions.administrator:
                if is_banned_selling(message.content) or is_scam_link(message.content):
                    try: await message.delete()
                    except: pass
                    embed=discord.Embed(title="Stickied Message:",description="DILARANG MENJUAL PRODUK YANG KAMI JUAL / LINK SCAM!",color=0xff0000);warn=await message.channel.send(message.author.mention,embed=embed);await asyncio.sleep(10)
                    try: await warn.delete()
                    except: pass
                    try: await message.author.send("Pesan kamu di #"+message.channel.name+" dihapus!\n\nAlasan: Dilarang menjual produk yang kami jual / link scam di MIPI STORE!")
                    except: pass
                    return
        if message.channel.id in ticket_data: ticket_data[message.channel.id]["last_activity"]=time.time()
        await bot.process_commands(message)
    except Exception as e: print(f"on_message error: {e}")
@bot.event
async def on_ready():
    try:
        print(f"Login {bot.user} - MIPI STORE V4 FINAL!");bot.add_view(OrderView());bot.add_view(TicketTypeView());bot.add_view(CloseView());bot.add_view(StatusView());bot.add_view(RatingView(0));bot.add_view(SaldoView());bot.add_view(GiveawayView("dummy"));bot.add_view(EditPricelistView());bot.add_view(PanelProdukView())
        for oid in load_pending().keys():
            try: bot.add_view(KonfirmasiSaldoView(oid))
            except: pass
        if not check_inactive.is_running(): check_inactive.start()
        if not auto_update_top_sultan.is_running(): auto_update_top_sultan.start()
        if not auto_rekap_omset.is_running(): auto_rekap_omset.start()
        for g in bot.guilds:
            try: await update_top_sultan(g)
            except: pass
        try:
            synced=await bot.tree.sync();print(f"Synced {len(synced)} commands - V4 FINAL!")
        except Exception as e: print(f"Sync error: {e}")
    except Exception as e: print(f"on_ready error: {e}");traceback.print_exc()
PANEL_FILE="panel.json"
def load_panel():
    try:
        with open(PANEL_FILE,"r") as f: return json.load(f)
    except: return {}
def save_panel(d):
    try:
        with open(PANEL_FILE,"w") as f: json.dump(d,f,indent=2)
    except Exception as e: print(f"save panel error: {e}")
async def update_all_panels(guild):
    try:
        panels=load_panel()
        for key,info in list(panels.items()):
            try:
                ch=guild.get_channel(int(info["channel_id"]))
                if not ch: continue
                msg=await ch.fetch_message(int(info["message_id"]))
                if key=="ticket": await msg.edit(embed=build_ticket_panel_baru_embed(),view=TicketTypeView())
                elif key=="pricelist": await msg.edit(embeds=build_all_pricelist_embeds())
                elif key=="produk": await msg.edit(embed=build_produk_embed(),view=PanelProdukView())
            except Exception as e: print(f"update panel {key} error: {e}")
    except Exception as e: print(f"update_all_panels error: {e}")
async def refresh_ticket_panel(guild):
    try: await update_all_panels(guild)
    except Exception as e: print(f"refresh panel error: {e}")
# === PRODUK HELPER (biar gak error di V4 lama) ===
def load_produk():
    try:
        with open("produk.json","r") as f:
            d=json.load(f)
            if isinstance(d,dict): return d
    except: pass
    return {"robux_visend":{"nama":"💎 Robux Via Username","harga":80000,"stok":9999,"deskripsi":"Robux via username, 500 Robux","emoji":"💎","kategori":"via_username"},"akun_sultan":{"nama":"💃 Akun Sultan","harga":1000000,"stok":3,"deskripsi":"Akun Sultan stok","emoji":"💃","kategori":"beli_akun"}}
def save_produk(d): _save("produk.json",d)
def build_produk_embed():
    d=load_produk();desc="💗 **KATALOG PRODUK MIPI STORE**\nSemua produk yang lagi dijual sekarang!\n\n━━━━━━━━━━━━━━━━━━\n"
    if not d: desc+="> Belum ada produk! Pencet ➕ Tambah Produk dulu!\n"
    else:
        for kode,p in d.items():
            stok_txt="🟢 READY (Unlimited)" if p.get("stok",0)>1000 else f"{'🟢 READY' if p.get('stok',0)>0 else '🔴 HABIS'} ({p.get('stok',0)} stok)";desc+=f"{p.get('emoji','📦')} **{p.get('nama','Produk')}**\n└ Kode: `{kode}` | Harga: {format_rp(p.get('harga',0))} | {stok_txt}\n└ {p.get('deskripsi','')}\n\n"
    desc+="━━━━━━━━━━━━━━━━━━\n🛍️ Order: Pencet tombol di #open-ticket / ketik /panel-produk\n💗 Mipi Store - Rafi Store";e=discord.Embed(title="🛍️ KATALOG PRODUK - MIPI STORE",description=desc,color=0xff69b4);e.set_image(url=WELCOME_URL);e.set_footer(text="MIPI STORE • Katalog Produk • Auto Update");return e
# === EDIT PRICELIST - TINGGAL PENCET (BARU!) ===
class EditHargaModal(discord.ui.Modal, title="✏️ Edit Harga"):
    def __init__(self, kategori, nominal, harga_lama):
        super().__init__();self.kategori=kategori;self.nominal=nominal;self.harga_lama=harga_lama;self.harga_input=discord.ui.TextInput(label=f"Harga Baru {nominal} Robux ({kategori})",placeholder=f"Harga lama: {harga_lama} - Ketik angka aja, contoh: 75000",required=True,max_length=10);self.add_item(self.harga_input)
    async def on_submit(self, interaction: discord.Interaction):
        try:
            teks=self.harga_input.value.replace("Rp","").replace("rp","").replace(".","").replace(",","").replace(" ","").strip();harga_baru=int(teks);d=load_pricelist(self.kategori);d[int(self.nominal)]=harga_baru;save_pricelist(d,self.kategori)
            try: await update_all_panels(interaction.guild)
            except: pass
            e=discord.Embed(title="✅ HARGA BERHASIL DIEDIT!",description=f"**Kategori:** {self.kategori}\n**Paket:** {self.nominal} Robux\n**Harga Lama:** {format_rp(self.harga_lama)}\n**Harga Baru:** {format_rp(harga_baru)}\n\nPanel pricelist udah ke-update otomatis! 💗",color=0x57f287);await interaction.response.send_message(embed=e,ephemeral=True)
        except ValueError: await interaction.response.send_message("❌ Harga harus angka ya! Contoh: `75000`",ephemeral=True)
        except Exception as e: await interaction.response.send_message(f"❌ Error: {e}",ephemeral=True)
class EditPricelistView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None);self.kategori="via_username";self.nominal=500
    @discord.ui.select(placeholder="1️⃣ Pilih Kategori Dulu - Visend / Vilog / Plus / Komunitas",custom_id="edit_pilih_kategori",options=[discord.SelectOption(label="💎 Via Username (Visend)",value="via_username",emoji="💎",description="Paling laris!"),discord.SelectOption(label="🔑 Via Login (Vilog)",value="via_login",emoji="🔑"),discord.SelectOption(label="👥 Via Komunitas",value="via_komunitas",emoji="👥"),discord.SelectOption(label="⭐ Roblox Plus",value="plus",emoji="⭐"),discord.SelectOption(label="💠 Limited Item",value="limited",emoji="💠")],row=0)
    async def pilih_kategori(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.kategori=select.values[0];harga=get_harga(self.nominal,self.kategori);await interaction.response.send_message(f"✅ Kategori dipilih: **{self.kategori}**\nSekarang pilih nominal di bawah, terus pencet **✏️ Edit Harga Ini**!\nHarga {self.nominal} Robux sekarang: **{format_rp(harga)}**",ephemeral=True)
    @discord.ui.select(placeholder="2️⃣ Pilih Nominal - 100 / 500 / 1000 / 5000 / 10000",custom_id="edit_pilih_nominal",options=[discord.SelectOption(label="100 Robux",value="100",emoji="💠"),discord.SelectOption(label="200 Robux",value="200",emoji="💠"),discord.SelectOption(label="500 Robux - PALING LARIS",value="500",emoji="✨"),discord.SelectOption(label="1000 Robux",value="1000",emoji="✨"),discord.SelectOption(label="2000 Robux",value="2000",emoji="👑"),discord.SelectOption(label="5000 Robux",value="5000",emoji="👑"),discord.SelectOption(label="10000 Robux - SULTAN",value="10000",emoji="👑")],row=1)
    async def pilih_nominal(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.nominal=int(select.values[0]);harga=get_harga(self.nominal,self.kategori);await interaction.response.send_message(f"✅ Nominal dipilih: **{self.nominal} Robux** ({self.kategori})\nHarga sekarang: **{format_rp(harga)}**\nTinggal pencet **✏️ Edit Harga Ini** di bawah!",ephemeral=True)
    @discord.ui.button(label="✏️ Edit Harga Ini",style=discord.ButtonStyle.primary,custom_id="edit_harga_ini",emoji="✏️",row=2)
    async def edit_ini(self, interaction: discord.Interaction, button: discord.ui.Button):
        harga_lama=get_harga(self.nominal,self.kategori);await interaction.response.send_modal(EditHargaModal(self.kategori,self.nominal,harga_lama))
    @discord.ui.button(label="👀 Lihat Harga",style=discord.ButtonStyle.secondary,custom_id="edit_lihat_harga",emoji="👀",row=2)
    async def lihat(self, interaction: discord.Interaction, button: discord.ui.Button):
        e=build_pricelist_embed(self.kategori);await interaction.response.send_message(embed=e,ephemeral=True)
    @discord.ui.button(label="➕ Semua +5k",style=discord.ButtonStyle.success,custom_id="edit_plus_5k",emoji="➕",row=3)
    async def plus_5k(self, interaction: discord.Interaction, button: discord.ui.Button):
        d=load_pricelist(self.kategori)
        for k in list(d.keys()): d[k]=int(d[k])+5000
        save_pricelist(d,self.kategori)
        try: await update_all_panels(interaction.guild)
        except: pass
        await interaction.response.send_message(f"✅ Semua harga **{self.kategori}** naik +Rp 5.000!\nContoh: 500 Robux sekarang {format_rp(d.get(500,0))}",ephemeral=True)
    @discord.ui.button(label="➖ Semua -5k",style=discord.ButtonStyle.secondary,custom_id="edit_min_5k",emoji="➖",row=3)
    async def min_5k(self, interaction: discord.Interaction, button: discord.ui.Button):
        d=load_pricelist(self.kategori)
        for k in list(d.keys()): d[k]=max(1000,int(d[k])-5000)
        save_pricelist(d,self.kategori)
        try: await update_all_panels(interaction.guild)
        except: pass
        await interaction.response.send_message(f"✅ Semua harga **{self.kategori}** turun -Rp 5.000!\nContoh: 500 Robux sekarang {format_rp(d.get(500,0))}",ephemeral=True)
    @discord.ui.button(label="🎁 Diskon 10% Semua",style=discord.ButtonStyle.success,custom_id="edit_diskon_10",emoji="🎁",row=3)
    async def diskon_10(self, interaction: discord.Interaction, button: discord.ui.Button):
        d=load_pricelist(self.kategori)
        for k in list(d.keys()):
            baru=int(int(d[k])*0.90);d[k]=int(round(baru/500)*500)
        save_pricelist(d,self.kategori)
        try: await update_all_panels(interaction.guild)
        except: pass
        await interaction.response.send_message(f"✅ Semua harga **{self.kategori}** diskon 10%!\nContoh: 500 Robux sekarang {format_rp(d.get(500,0))} 💗",ephemeral=True)
    @discord.ui.button(label="🔄 Reset ke Default",style=discord.ButtonStyle.danger,custom_id="edit_reset",emoji="🔄",row=3)
    async def reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        rate=180 if self.kategori=="via_login" else 140 if self.kategori=="via_komunitas" else 160;d=_build_pricelist(rate);save_pricelist(d,self.kategori)
        try: await update_all_panels(interaction.guild)
        except: pass
        await interaction.response.send_message(f"✅ **{self.kategori}** udah di-reset ke harga default!\n500 Robux sekarang {format_rp(d.get(500,0))}",ephemeral=True)
# === PANEL PRODUK - TAMBAH / KURANGIN - TINGGAL PENCET (BARU!) ===
class TambahProdukModal(discord.ui.Modal, title="➕ Tambah Produk Baru"):
    def __init__(self): super().__init__()
    kode=discord.ui.TextInput(label="Kode Produk (tanpa spasi)",placeholder="Contoh: akun_korblox",required=True,max_length=30)
    nama=discord.ui.TextInput(label="Nama Produk",placeholder="Contoh: Akun Korblox Sultan",required=True,max_length=50)
    harga=discord.ui.TextInput(label="Harga (angka aja)",placeholder="Contoh: 500000",required=True,max_length=10)
    stok=discord.ui.TextInput(label="Stok (angka)",placeholder="Contoh: 5 / 9999 kalo unlimited",required=True,max_length=10)
    deskripsi=discord.ui.TextInput(label="Deskripsi Produk",placeholder="Contoh: Akun Korblox, full email",style=discord.TextStyle.paragraph,required=False,max_length=200)
    async def on_submit(self, interaction: discord.Interaction):
        try:
            kode_bersih=self.kode.value.lower().replace(" ","_").replace("-","_");harga_int=int(self.harga.value.replace(".","").replace(",","").replace("Rp","").replace(" ",""));stok_int=int(self.stok.value.replace(".","").replace(",","").replace(" ",""));d=load_produk();d[kode_bersih]={"nama":self.nama.value,"harga":harga_int,"stok":stok_int,"deskripsi":self.deskripsi.value if self.deskripsi.value else "-","emoji":"📦","kategori":"other"};save_produk(d);e=discord.Embed(title="✅ PRODUK DITAMBAH!",description=f"**Nama:** {self.nama.value}\n**Kode:** `{kode_bersih}`\n**Harga:** {format_rp(harga_int)}\n**Stok:** {stok_int}\n**Deskripsi:** {self.deskripsi.value}\n\nUdah masuk katalog! Cek pake /list-produk 💗",color=0x57f287);await interaction.response.send_message(embed=e,ephemeral=True)
        except ValueError: await interaction.response.send_message("❌ Harga & Stok harus angka ya! Contoh harga: `500000`, stok: `5`",ephemeral=True)
        except Exception as e: await interaction.response.send_message(f"❌ Error: {e}",ephemeral=True)
class KuranginProdukModal(discord.ui.Modal, title="➖ Kurangin / Hapus Produk"):
    def __init__(self): super().__init__()
    kode=discord.ui.TextInput(label="Kode Produk yang mau dihapus / dikurangin",placeholder="Contoh: akun_sultan - liat kode di /list-produk",required=True,max_length=30)
    jumlah=discord.ui.TextInput(label="Mau dikurangin berapa? / Ketik HAPUS kalo mau hapus total",placeholder="Contoh: 1 / HAPUS",required=True,max_length=10)
    async def on_submit(self, interaction: discord.Interaction):
        try:
            kode_bersih=self.kode.value.lower().strip();d=load_produk()
            if kode_bersih not in d:
                daftar=", ".join([f"`{k}`" for k in d.keys()]);await interaction.response.send_message(f"❌ Kode `{kode_bersih}` gak ketemu!\n\nKode yang ada: {daftar}\nCek lagi di /list-produk ya!",ephemeral=True);return
            nama=d[kode_bersih].get("nama",kode_bersih);stok_lama=d[kode_bersih].get("stok",0)
            if self.jumlah.value.strip().upper()=="HAPUS": del d[kode_bersih];save_produk(d);await interaction.response.send_message(f"✅ **PRODUK DIHAPUS!**\n**{nama}** (`{kode_bersih}`) udah dihapus dari katalog! 🗑️",ephemeral=True);return
            kurang=int(self.jumlah.value.replace(".","").replace(",","").replace(" ",""));stok_baru=max(0,stok_lama-kurang);d[kode_bersih]["stok"]=stok_baru;save_produk(d);status="🔴 HABIS!" if stok_baru==0 else f"🟢 Sisa {stok_baru}";await interaction.response.send_message(f"✅ **STOK DIKURANGIN!**\n**{nama}**\nStok lama: {stok_lama} -> Stok baru: {stok_baru} ({status})",ephemeral=True)
        except ValueError: await interaction.response.send_message("❌ Jumlah harus angka (contoh: `1`) atau ketik `HAPUS`!",ephemeral=True)
        except Exception as e: await interaction.response.send_message(f"❌ Error: {e}",ephemeral=True)
class TambahStokModal(discord.ui.Modal, title="📦 Tambah Stok Produk"):
    def __init__(self): super().__init__()
    kode=discord.ui.TextInput(label="Kode Produk",placeholder="Contoh: akun_sultan",required=True,max_length=30)
    jumlah=discord.ui.TextInput(label="Tambah berapa stok?",placeholder="Contoh: 5",required=True,max_length=10)
    async def on_submit(self, interaction: discord.Interaction):
        try:
            kode_bersih=self.kode.value.lower().strip();d=load_produk()
            if kode_bersih not in d: await interaction.response.send_message(f"❌ Kode `{kode_bersih}` gak ketemu! Cek /list-produk!",ephemeral=True);return
            tambah=int(self.jumlah.value.replace(".","").replace(",","").replace(" ",""));d[kode_bersih]["stok"]=d[kode_bersih].get("stok",0)+tambah;save_produk(d);await interaction.response.send_message(f"✅ **STOK DITAMBAH!**\n**{d[kode_bersih]['nama']}** sekarang stoknya {d[kode_bersih]['stok']}! 🟢 READY lagi!",ephemeral=True)
        except ValueError: await interaction.response.send_message("❌ Jumlah harus angka ya! Contoh: `5`",ephemeral=True)
        except Exception as e: await interaction.response.send_message(f"❌ Error: {e}",ephemeral=True)
class PanelProdukView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="➕ Tambah Produk",style=discord.ButtonStyle.success,custom_id="produk_tambah",emoji="➕",row=0)
    async def tambah(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_admin_or_owner(interaction.user,interaction.guild): await interaction.response.send_message("❌ Hanya Admin / Owner!",ephemeral=True);return
        await interaction.response.send_modal(TambahProdukModal())
    @discord.ui.button(label="➖ Kurangin / Hapus Produk",style=discord.ButtonStyle.danger,custom_id="produk_kurang",emoji="➖",row=0)
    async def kurang(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_admin_or_owner(interaction.user,interaction.guild): await interaction.response.send_message("❌ Hanya Admin / Owner!",ephemeral=True);return
        await interaction.response.send_modal(KuranginProdukModal())
    @discord.ui.button(label="📦 Tambah Stok",style=discord.ButtonStyle.primary,custom_id="produk_tambah_stok",emoji="📦",row=1)
    async def tambah_stok(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_admin_or_owner(interaction.user,interaction.guild): await interaction.response.send_message("❌ Hanya Admin / Owner!",ephemeral=True);return
        await interaction.response.send_modal(TambahStokModal())
    @discord.ui.button(label="🛍️ Lihat Katalog",style=discord.ButtonStyle.secondary,custom_id="produk_lihat",emoji="🛍️",row=1)
    async def lihat(self, interaction: discord.Interaction, button: discord.ui.Button):
        e=build_produk_embed();await interaction.response.send_message(embed=e,ephemeral=True)
# === SEMUA SLASH COMMAND V4 FINAL ===
@bot.tree.command(name="ticket",description="Tampilkan panel order MIPI STORE")
async def ticket(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=False)
    try:
        if STORE_STATUS!="open":
            st="BREAK - Mimin break 15-30 menit!" if STORE_STATUS=="break" else "CLOSED - Toko tutup, balik besok yaa!";await safe_followup(interaction,content=st+"\n\nTicket lagi dikunci sementara! Tunggu OPEN lagi yaa! 💗",ephemeral=True);return
        ch_target=interaction.guild.get_channel(OPEN_TICKET_CHANNEL_ID) or interaction.channel;panels=load_panel()
        if "ticket" in panels:
            try:
                ch=interaction.guild.get_channel(int(panels["ticket"]["channel_id"]));msg=await ch.fetch_message(int(panels["ticket"]["message_id"]));await msg.edit(embed=build_ticket_panel_baru_embed(),view=TicketTypeView());await safe_followup(interaction,content=f"✅ Panel udah di-update jadi 10 tombol baru! Cek {ch.mention}",ephemeral=True);return
            except Exception as e: print(f"edit old panel gagal, kirim baru: {e}")
        msg=await ch_target.send(embed=build_ticket_panel_baru_embed(),view=TicketTypeView());panels["ticket"]={"channel_id":str(msg.channel.id),"message_id":str(msg.id)};save_panel(panels);await safe_followup(interaction,content=f"✅ Panel ticket udah dikirim ke {ch_target.mention}!",ephemeral=True)
    except Exception as e: print(f"ERROR /ticket: {e}");traceback.print_exc();await safe_followup(interaction,content=f"❌ Error /ticket: {e}",ephemeral=True)
@bot.tree.command(name="setup-ticket",description="Kirim panel ticket order (Owner only)")
async def setup_ticket(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        if interaction.user.id!=interaction.guild.owner_id: await safe_followup(interaction,content="Hanya Owner!",ephemeral=True);return
        ch_target=interaction.guild.get_channel(OPEN_TICKET_CHANNEL_ID) or interaction.channel;msg=await ch_target.send(embed=build_ticket_panel_baru_embed(),view=TicketTypeView());panels=load_panel();panels["ticket"]={"channel_id":str(msg.channel.id),"message_id":str(msg.id)};save_panel(panels);await safe_followup(interaction,content=f"✅ Panel dikirim ke {ch_target.mention}!",ephemeral=True)
    except Exception as e: print(f"ERROR /setup-ticket: {e}");await safe_followup(interaction,content=f"❌ Error: {e}",ephemeral=True)
@bot.tree.command(name="open",description="Buka toko")
async def open_cmd(interaction:discord.Interaction):
    global STORE_STATUS;await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Cuma admin!",ephemeral=True);return
        STORE_STATUS="open";await safe_followup(interaction,content="✅ Mipi Store **DIBUKA**! Ticket bisa dipencet lagi!")
    except Exception as e: await safe_followup(interaction,content=f"❌ Error: {e}",ephemeral=True)
@bot.tree.command(name="break",description="Toko break sebentar")
async def break_cmd(interaction:discord.Interaction):
    global STORE_STATUS;await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Cuma admin!",ephemeral=True);return
        STORE_STATUS="break";await safe_followup(interaction,content="☕ Mipi Store **BREAK** 15-30 menit! Ticket dikunci sementara!")
    except Exception as e: await safe_followup(interaction,content=f"❌ Error: {e}",ephemeral=True)
@bot.tree.command(name="close",description="Tutup toko")
async def close_cmd(interaction:discord.Interaction):
    global STORE_STATUS;await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Cuma admin!",ephemeral=True);return
        STORE_STATUS="closed";await safe_followup(interaction,content="💤 Mipi Store **TUTUP**! Ticket dikunci, balik besok yaa!")
    except Exception as e: await safe_followup(interaction,content=f"❌ Error: {e}",ephemeral=True)
@bot.tree.command(name="panel-edit-pricelist",description="Buka panel edit pricelist - TINGGAL PENCET! (Admin)")
async def panel_edit_pricelist(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="❌ Hanya Admin / Owner!",ephemeral=True);return
        e=discord.Embed(title="💎 EDIT PRICELIST - TINGGAL PENCET AJA!",description="**Cara pake (3 detik doang!):**\n\n1️⃣ **Pilih Kategori** di dropdown atas (Visend / Vilog / Plus / dll)\n2️⃣ **Pilih Nominal** di dropdown bawah (100 / 500 / 1000 / dll)\n3️⃣ Pencet **✏️ Edit Harga Ini** -> ketik harga baru -> ENTER -> BERES!\n\n**Tombol Cepet:**\n➕ **Semua +5k** = Naikin semua harga kategori itu 5k sekaligus\n➖ **Semua -5k** = Turunin semua harga 5k sekaligus\n🎁 **Diskon 10%** = Diskon semua harga 10% buat promo\n🔄 **Reset** = Balikin ke harga awal kalo salah edit\n\n💗 Mipi Store - Gak usah ngetik command lagi!",color=0xff69b4);e.set_image(url=WELCOME_URL);await interaction.channel.send(embed=e,view=EditPricelistView());await safe_followup(interaction,content="✅ Panel Edit Pricelist udah dikirim di channel ini! Tinggal pencet-pencet aja! 💗",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ Error: {e}",ephemeral=True)
@bot.tree.command(name="edit-pricelist",description="Edit pricelist - TINGGAL PENCET! (Admin)")
async def edit_pricelist_pencet(interaction:discord.Interaction):
    await panel_edit_pricelist.callback(interaction)
@bot.tree.command(name="panel-produk",description="Buka panel Tambah & Kurangin Produk - TINGGAL PENCET! (Admin)")
async def panel_produk(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="❌ Hanya Admin / Owner!",ephemeral=True);return
        e=discord.Embed(title="🛍️ KELOLA PRODUK - TINGGAL PENCET AJA!",description="**Cara pake:**\n\n➕ **Tambah Produk** = Nambah produk baru (Akun, Gamepass, dll)\n➖ **Kurangin / Hapus Produk** = Kurangin stok / hapus produk yang udah gak dijual\n📦 **Tambah Stok** = Restock produk yang habis\n🛍️ **Lihat Katalog** = Lihat semua produk yang lagi dijual\n\n💗 Mipi Store - Gak usah ngetik command lagi!",color=0xff69b4);e.set_image(url=WELCOME_URL);await interaction.channel.send(embed=e,view=PanelProdukView());await safe_followup(interaction,content="✅ Panel Produk udah dikirim! Tinggal pencet-pencet aja! 💗",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ Error: {e}",ephemeral=True)
@bot.tree.command(name="tambah-produk",description="Tambah produk baru - TINGGAL PENCET! (Admin)")
async def tambah_produk(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="❌ Hanya Admin / Owner!",ephemeral=True);return
        await safe_followup(interaction,content="Pencet panel di bawah buat tambah produk! 💗",view=PanelProdukView(),ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="kurangin-produk",description="Kurangin stok / Hapus produk - TINGGAL PENCET! (Admin)")
async def kurangin_produk(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="❌ Hanya Admin / Owner!",ephemeral=True);return
        await safe_followup(interaction,content="Pencet panel di bawah buat kurangin / hapus produk! 💗\nKetik `HAPUS` kalo mau hapus total!",view=PanelProdukView(),ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="hapus-produk",description="Hapus produk total (Admin)")
async def hapus_produk(interaction:discord.Interaction,kode:str):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="❌ Hanya Admin / Owner!",ephemeral=True);return
        d=load_produk();k=kode.lower().strip()
        if k in d:
            nama=d[k].get("nama",k);del d[k];save_produk(d);await safe_followup(interaction,content=f"✅ **{nama}** (`{k}`) udah dihapus dari katalog! 🗑️",ephemeral=True)
        else: await safe_followup(interaction,content=f"❌ Kode `{k}` gak ketemu! Cek /list-produk!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="list-produk",description="Lihat semua produk + kode + stok")
async def list_produk(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try: e=build_produk_embed();await safe_followup(interaction,embed=e,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="pricelist-visend",description="Pricelist Via Username Modern Elegan")
async def pricelist_visend(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try: e=build_pricelist_embed("via_username");await interaction.channel.send(embed=e);await safe_followup(interaction,content="✅ Pricelist Visend Modern dikirim!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="pricelist-vilog",description="Pricelist Via Login")
async def pricelist_vilog(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try: e=build_pricelist_embed("via_login");await interaction.channel.send(embed=e);await safe_followup(interaction,content="✅ Pricelist Vilog dikirim!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="pricelist-plus",description="Pricelist Roblox Plus")
async def pricelist_plus(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try: e=build_pricelist_embed("plus");await interaction.channel.send(embed=e);await safe_followup(interaction,content="✅ Pricelist Plus dikirim!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="pricelist-komunitas",description="Pricelist Via Komunitas")
async def pricelist_komunitas(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try: e=build_pricelist_embed("via_komunitas");await interaction.channel.send(embed=e);await safe_followup(interaction,content="✅ Pricelist Komunitas dikirim!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="pricelist-rekber",description="Pricelist Rekber Elegan")
async def pricelist_rekber(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try: await interaction.channel.send(embed=build_rekber_embed(),view=RekberView(guild_id=interaction.guild.id));await safe_followup(interaction,content="✅ Pricelist Rekber Elegan dikirim!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="setup-rekber",description="Kirim panel Rekber Elegan ke #open-ticket (Owner)")
async def setup_rekber(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        if interaction.user.id!=interaction.guild.owner_id: await safe_followup(interaction,content="Hanya Owner!",ephemeral=True);return
        ch=interaction.guild.get_channel(OPEN_TICKET_CHANNEL_ID)
        if not ch: await safe_followup(interaction,content="❌ Channel open-ticket gak ketemu!",ephemeral=True);return
        msg=await ch.send(embed=build_rekber_embed(),view=RekberView(guild_id=interaction.guild.id));panels=load_panel();panels["rekber"]={"channel_id":str(msg.channel.id),"message_id":str(msg.id)};save_panel(panels);await safe_followup(interaction,content=f"✅ Panel Rekber Elegan udah dialihin ke {ch.mention}!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ Error: {e}",ephemeral=True)
@bot.tree.command(name="tutup-kategori",description="Tutup 1 tombol (Stok Habis) - Admin")
async def tutup_kategori(interaction:discord.Interaction,kategori:str):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin / Owner!",ephemeral=True);return
        kat=kategori_alias(kategori);set_stock(kat,False)
        try: await refresh_ticket_panel(interaction.guild)
        except: pass
        await safe_followup(interaction,content=f"🔴 **{kat.upper()} DITUTUP!**\nTombolnya sekarang abu-abu & gak bisa dipencet!\nBuka lagi: `/buka-kategori {kat}`",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="buka-kategori",description="Buka lagi 1 tombol (Restock) - Admin")
async def buka_kategori(interaction:discord.Interaction,kategori:str):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin / Owner!",ephemeral=True);return
        kat=kategori_alias(kategori);set_stock(kat,True)
        try: await refresh_ticket_panel(interaction.guild)
        except: pass
        try: await send_notify_restock(interaction.guild,kat)
        except: pass
        await safe_followup(interaction,content=f"🟢 **{kat.upper()} DIBUKA LAGI!**\nTombolnya udah bisa dipencet lagi! ✨\nYang udah /notify udah di-DM otomatis!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="cek-stock",description="Cek tombol mana aja yang BUKA / TUTUP")
async def cek_stock(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        s=load_stock();all_kat=["via_username","via_login","via_komunitas","plus","limited","rekber","beli_akun","other"];txt="📦 **STATUS STOCK MIPI STORE**\n\n"
        for k in all_kat:
            v=s.get(k,True);txt+=f"{'🟢 BUKA' if v else '🔴 HABIS / TUTUP'}  —  {k}\n"
        txt+="\nTutup: `/tutup-kategori plus`\nBuka: `/buka-kategori plus`";await safe_followup(interaction,content=txt,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="notify",description="Dapet DM otomatis kalo stok yang kamu mau restock!")
async def notify_cmd(interaction:discord.Interaction,kategori:str):
    await safe_defer(interaction,ephemeral=True)
    try: kat=kategori_alias(kategori);add_notify(interaction.user.id,kat);await safe_followup(interaction,content=f"🔔 Oke! Kalo **{kat}** restock / dibuka lagi, kamu langsung aku DM! 💗",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="saldo",description="Cek saldo / total belanja kamu + level + poin")
async def saldo_cmd(interaction:discord.Interaction,user:discord.User=None):
    await safe_defer(interaction,ephemeral=True)
    try:
        target=user or interaction.user;tr,tro,tt=get_total_belanja(target.id);lvl=get_level(tr);nxt,sisa=get_next_level(tr);poin=get_poin(target.id);embed=discord.Embed(color=0xff1493);embed.description=f"INFORMASI SALDO / TOTAL TRANSAKSI\n\nHalo {target.mention},\n\n🏆 Level: {lvl}\n➡️ Next: {nxt} (kurang {format_rp(sisa)})\n\nTotal Belanja: {format_rp(tr)}\nTotal Robux: {tro} R$\nTotal Transaksi: {tt}x\n🎁 Poin Daily: {poin} poin\n\nMIPI STORE - CHECK SALDO";embed.set_footer(text="Mipi Store - Rafi Store");await safe_followup(interaction,embed=embed,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="cek-saldo",description="Cek saldo kamu (tombol)")
async def cek_saldo_cmd(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try: await safe_followup(interaction,content="Pencet tombol di bawah buat cek saldo kamu!",view=SaldoView(),ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="top-sultan",description="Lihat Top Sultan")
async def top_sultan_cmd(interaction:discord.Interaction,jenis:str="semua"):
    await safe_defer(interaction,ephemeral=True)
    try: e=build_top_sultan_embed_bulanan() if "bulan" in jenis.lower() else build_top_sultan_embed_semua();await safe_followup(interaction,embed=e,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="statistik",description="Lihat statistik omset real-time MIPI STORE")
async def statistik_cmd(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try: s=get_statistik();e=discord.Embed(title="📊 STATISTIK MIPI STORE - REAL TIME",description=f"📅 **Hari Ini:** {format_rp(s['hari_rp'])} ({s['hari_tr']} pending hari ini)\n📅 **Bulan Ini ({datetime.now().strftime('%B %Y')}):** {format_rp(s['bulan_rp'])} ({s['bulan_tr']} transaksi)\n👑 **All Time:** {format_rp(s['all_rp'])} ({s['all_tr']} transaksi)\n\n💗 Mipi Store — Rafi Store",color=0xff69b4);await safe_followup(interaction,embed=e,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="referral",description="Lihat kode referral kamu + komisi kamu")
async def referral_cmd(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        data=load_referral();uid=str(interaction.user.id);code=get_referral_code(interaction.user.id)
        if uid not in data: data[uid]={"code":code,"total_komisi":0,"total_referral":0,"history":[]};save_referral(data)
        info=data[uid];txt=f"💸 **REFERRAL KAMU**\n\n🔑 Kode kamu: **{info['code']}**\nKasih kode ini ke temen kamu, suruh dia isi di modal order!\n\n💰 Total Komisi: {format_rp(info['total_komisi'])}\n👥 Total Temen yang Order: {info['total_referral']} orang\n\nCara: Temen order -> isi kode kamu -> kamu dapet 5% otomatis!\n💗 Mipi Store";await safe_followup(interaction,content=txt,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="daily",description="Claim daily reward dapet poin!")
async def daily_cmd(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        bonus,total,err=claim_daily(interaction.user.id)
        if err: await safe_followup(interaction,content=f"❌ {err}\nPoin kamu: {total} poin",ephemeral=True)
        else: await safe_followup(interaction,content=f"🎁 **DAILY CLAIM BERHASIL!**\nKamu dapet +{bonus} poin!\nTotal poin: {total} poin\n\nKumpulin 100 poin = bisa dituker 100 Robux! Ketik `/tuker-poin 100`!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="tuker-poin",description="Tuker poin daily jadi Robux!")
async def tuker_poin(interaction:discord.Interaction,jumlah:int):
    await safe_defer(interaction,ephemeral=True)
    try:
        poin=get_poin(interaction.user.id)
        if poin<jumlah: await safe_followup(interaction,content=f"❌ Poin kamu cuma {poin}, gak cukup buat tuker {jumlah}!",ephemeral=True);return
        if jumlah<100: await safe_followup(interaction,content="❌ Minimal tuker 100 poin = 100 Robux!",ephemeral=True);return
        if not use_poin(interaction.user.id,jumlah): await safe_followup(interaction,content="❌ Gagal tuker poin!",ephemeral=True);return
        oid=add_to_pending(interaction.user.id,interaction.user.name,f"TUKER POIN - {jumlah} Robux",999999,f"tuker-poin-{interaction.user.name}",kategori="via_username",robux_jumlah=jumlah,harga_akhir=0);await safe_followup(interaction,content=f"✅ **TUKER POIN BERHASIL!**\n-{jumlah} poin\n+{jumlah} Robux masuk PENDING!\nAdmin bakal proses & kirim robux kamu! Order ID: {oid}",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="buat-voucher",description="Bikin voucher diskon (Admin)")
async def buat_voucher(interaction:discord.Interaction,kode:str,diskon:int,tipe:str="persen",max_pakai:int=10):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin / Owner!",ephemeral=True);return
        data=load_voucher();data[kode.upper()]={"diskon":int(diskon),"tipe":tipe.lower(),"max":int(max_pakai),"dipakai":0,"used_by":[]};save_voucher(data);await safe_followup(interaction,content=f"✅ Voucher **{kode.upper()}** dibuat! Diskon {diskon} {tipe}, max {max_pakai}x!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="redeem-voucher",description="Redeem voucher dapet diskon!")
async def redeem_voucher_cmd(interaction:discord.Interaction,kode:str):
    await safe_defer(interaction,ephemeral=True)
    try:
        v,err=redeem_voucher(interaction.user.id,kode)
        if err: await safe_followup(interaction,content=f"❌ {err}",ephemeral=True)
        else: await safe_followup(interaction,content=f"✅ **VOUCHER DIREDEEM!**\nKode: {kode.upper()}\nDiskon: {v['diskon']} {v['tipe']}\n\nSS ini & kasih ke admin pas order, biar harganya dipotong! 💗",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="tebak-harga",description="Main tebak harga, menang dapet voucher!")
async def tebak_harga(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        nominal,harga,pilihan=start_tebak_harga();game_data[interaction.user.id]={"nominal":nominal,"harga":harga,"pilihan":pilihan};txt=f"🎮 **TEBAK HARGA - MIPI STORE**\n\nBerapa harga **{nominal} Robux Via Username**?\n\n"
        for i,p in enumerate(pilihan,1): txt+=f"{i}. {format_rp(p)}\n"
        txt+="\nJawab pake `/jawab-tebak <nomor>`! Benar = dapet voucher 5%!";await safe_followup(interaction,content=txt,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="jawab-tebak",description="Jawab game tebak harga!")
async def jawab_tebak(interaction:discord.Interaction,nomor:int):
    await safe_defer(interaction,ephemeral=True)
    try:
        if interaction.user.id not in game_data: await safe_followup(interaction,content="❌ Kamu belum mulai game! Ketik `/tebak-harga` dulu!",ephemeral=True);return
        g=game_data.pop(interaction.user.id);pilihan=g["pilihan"]
        if nomor<1 or nomor>len(pilihan): await safe_followup(interaction,content="❌ Nomor gak valid!",ephemeral=True);return
        if pilihan[nomor-1]==g["harga"]:
            kode=f"GAME-{interaction.user.id%10000:04d}";data=load_voucher();data[kode]={"diskon":5,"tipe":"persen","max":1,"dipakai":0,"used_by":[]};save_voucher(data);await safe_followup(interaction,content=f"🎉 **BENAR!** Harga {g['nominal']} Robux emang {format_rp(g['harga'])}!\nKamu dapet voucher **{kode}** (Diskon 5%)! Redeem pake `/redeem-voucher {kode}`!",ephemeral=True)
        else: await safe_followup(interaction,content=f"❌ Salah! Harga {g['nominal']} Robux itu {format_rp(g['harga'])}, bukan {format_rp(pilihan[nomor-1])}! Coba lagi pake `/tebak-harga`!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="tambah-promo",description="Tambah kode promo (Admin)")
async def tambah_promo(interaction:discord.Interaction,kode:str,diskon:int,tipe:str="persen",max_pakai:int=999):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin / Owner!",ephemeral=True);return
        data=load_promo();data[kode.upper()]={"diskon":int(diskon),"tipe":tipe.lower(),"max":int(max_pakai),"dipakai":0};save_promo(data);await safe_followup(interaction,content=f"✅ Promo **{kode.upper()}** ditambah! Diskon {diskon} {tipe}, max {max_pakai}x pakai!",ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="lihat-promo",description="Lihat semua kode promo")
async def lihat_promo(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        data=load_promo()
        if not data: await safe_followup(interaction,content="Belum ada promo!",ephemeral=True);return
        txt="🎁 **DAFTAR PROMO MIPI STORE**\n\n"
        for k,v in data.items(): txt+=f"**{k}** — Diskon {v.get('diskon')} {v.get('tipe')} — Dipakai {v.get('dipakai',0)}/{v.get('max',999)}\n"
        await safe_followup(interaction,content=txt,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="giveaway",description="Bikin giveaway (Admin)")
async def giveaway_cmd(interaction:discord.Interaction,hadiah:str,pemenang:int=1,menit:int=60):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin / Owner!",ephemeral=True);return
        gid=f"GW-{int(time.time())}";giveaway_data[gid]={"hadiah":hadiah,"host_mention":interaction.user.mention,"peserta":[],"pemenang":int(pemenang),"ended":False};e=discord.Embed(title="🎉 GIVEAWAY MIPI STORE!",description=f"Hadiah: {hadiah}\nHost: {interaction.user.mention}\nPeserta: 0 orang",color=0xff69b4);msg=await interaction.channel.send(embed=e,view=GiveawayView(gid));await safe_followup(interaction,content=f"✅ Giveaway **{hadiah}** dibuat! Berakhir {menit} menit lagi!",ephemeral=True);await asyncio.sleep(int(menit)*60);await end_giveaway(interaction.guild,msg.channel.id,msg.id,gid)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="pending",description="Lihat semua pending saldo (Admin)")
async def pending_cmd(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin / Owner!",ephemeral=True);return
        data=load_pending()
        if not data: await safe_followup(interaction,content="✅ Gak ada pending! Semua udah dikonfirmasi!",ephemeral=True);return
        txt="⏳ **PENDING SALDO - BELUM DIKONFIRMASI**\n\n"
        for oid,d in data.items(): txt+=f"**{oid}** — <@{d['user_id']}> — {d['paket']} — {d['robux']} R$ — {format_rp(d['harga'])}\n"
        txt+="\nAdmin harus pencet ✅ di channel history / order-status buat masukin ke leaderboard!";await safe_followup(interaction,content=txt,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="add-saldo",description="Tambah saldo manual (masuk Bulanan + All Time)")
async def add_saldo(interaction:discord.Interaction,user:discord.User,robux:int,kategori:str="via_username"):
    await safe_defer(interaction,ephemeral=True)
    try:
        if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin / Owner!",ephemeral=True);return
        kat=kategori_alias(kategori);add_to_leaderboard(user.id,user.name,f"{robux} Robux",kategori=kat);await safe_followup(interaction,content=f"✅ Saldo ditambah! {user.mention} +{robux} R$ masuk **Bulanan + All Time**!",ephemeral=True)
        try: await update_top_sultan(interaction.guild)
        except: pass
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="leaderboard-bulanan",description="Lihat Top Sultan Bulanan")
async def lb_bulanan(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try: e=build_top_sultan_embed_bulanan();await safe_followup(interaction,embed=e,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="leaderboard-semua",description="Lihat Top Sultan Semua / All Time")
async def lb_semua(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try: e=build_top_sultan_embed_semua();await safe_followup(interaction,embed=e,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="lihat-harga",description="Lihat semua harga pricelist")
async def lihat_harga(interaction:discord.Interaction,kategori:str="via_username"):
    await safe_defer(interaction,ephemeral=True)
    try: kat=kategori_alias(kategori);e=build_pricelist_embed(kat);await safe_followup(interaction,embed=e,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
@bot.tree.command(name="help-mipi",description="Lihat semua command MIPI STORE V4 FINAL")
async def help_mipi(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    try:
        txt=("💗 **HELP - MIPI STORE V4 FINAL**\n\n**ORDER:**\n`/ticket` - Panel order\n`/pricelist-visend` `/pricelist-vilog` `/pricelist-plus` `/pricelist-komunitas` `/pricelist-rekber`\n\n**EDIT PENCET (BARU!):**\n`/panel-edit-pricelist` - Edit harga tinggal pencet!\n`/panel-produk` - Tambah / Kurangin produk tinggal pencet!\n`/tambah-produk` `/kurangin-produk` `/list-produk` `/hapus-produk`\n\n**SALDO / LEADERBOARD:**\n`/saldo` `/cek-saldo` `/top-sultan` `/leaderboard-bulanan` `/leaderboard-semua` `/add-saldo` `/pending`\n\n**STOCK:**\n`/tutup-kategori` `/buka-kategori` `/cek-stock` `/notify`\n\n**V4:**\n`/referral` `/daily` `/tuker-poin` `/buat-voucher` `/redeem-voucher` `/tebak-harga` `/jawab-tebak` `/statistik`\n\n**TOKO:** `/open` `/break` `/close`\n\n**ADMIN:** `/tambah-promo` `/lihat-promo` `/giveaway` `/setup-rekber`\n");await safe_followup(interaction,content=txt,ephemeral=True)
    except Exception as e: await safe_followup(interaction,content=f"❌ {e}",ephemeral=True)
bot.run(os.getenv("DISCORD_TOKEN"))
bot.run(os.getenv("DISCORD_TOKEN"))
