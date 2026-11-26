import discord
from discord.ext import commands, tasks
import os, time, io, html, re, asyncio, json, random, traceback
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
REFERRAL_RATE=0.05;DAILY_POIN=10;LEVELS=[("🌱 Newbie",0),("💎 Regular",100000),("⭐ VIP",500000),("👑 Sultan",1000000),("🔥 LEGEND",5000000)]

async def safe_defer(interaction,ephemeral=False):
    try:
        if not interaction.response.is_done(): await interaction.response.defer(ephemeral=ephemeral);return True
    except: return False
async def safe_followup(interaction,content=None,embed=None,embeds=None,view=None,ephemeral=False):
    try:
        if interaction.response.is_done(): return await interaction.followup.send(content=content,embed=embed,embeds=embeds,view=view,ephemeral=ephemeral)
        else: return await interaction.response.send_message(content=content,embed=embed,embeds=embeds,view=view,ephemeral=ephemeral)
    except:
        try: return await interaction.channel.send(content=content,embed=embed,embeds=embeds,view=view)
        except: return None

@bot.tree.error
async def on_app_command_error(interaction,error):
    print(f"SLASH ERROR {interaction.command.name if interaction.command else '?'}: {error}")
    try:
        msg=f"❌ Error: {str(error)[:400]}"
        if interaction.response.is_done(): await interaction.followup.send(msg,ephemeral=True)
        else: await interaction.response.send_message(msg,ephemeral=True)
    except: pass

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
    m={"visend":"via_username","via_send":"via_username","via_username":"via_username","vilog":"via_login","via_login":"via_login","vlog":"via_login","komunitas":"via_komunitas","via_komunitas":"via_komunitas","plus":"plus","roblox_plus":"plus","roblox_pluss":"plus","pluss":"plus","limited":"limited","rekber":"rekber","mm":"rekber","middleman":"rekber","beli_akun":"beli_akun","other":"other","nanya":"other"}
    return m.get(k,k)

# ===== HARGA ASLI - UDAH DIPISAH, GAK PAKE RUMUS! =====
LIMITED_ITEMS={
  "8bit_royal_crown":{"nama":"8-BIT ROYAL CROWN","harga":2300000,"emoji":"<:BRC:1510531815427805194>"},
  "8bit_hp_bar":{"nama":"8-BIT HP BAR","harga":850000,"emoji":"<:HPBAR:1510531549274312824>"},
  "8bit_tabby_cat":{"nama":"8-BIT TABBY CAT","harga":750000,"emoji":"<:TABBY:1510531527006748762>"},
  "8bit_extra":{"nama":"8-BIT EXTRA","harga":700000,"emoji":"<:EXTRA:1510531838848925867>"},
  "8bit_coin":{"nama":"8-BIT COIN","harga":700000,"emoji":"<:COIN:1510531570425925734>"},
}
DEFAULT_PRICELIST_PER_KATEGORI={
  "via_username":{100:15500,200:31000,300:46500,400:62000,500:73000,600:88000,700:108000,800:118000,900:133000,1000:145000,1200:176000,1500:218000,2000:290000,2500:363000,3000:435000,4000:580000,5000:725000,6000:870000,7000:1015000,8000:1160000,9000:1305000,10000:1450000},
  "via_login":{500:80000,600:96000,700:112000,800:128000,900:144000,1000:155000,1200:186000,1500:232500,2000:310000,2500:387500,3000:465000,4000:620000,5000:775000,6000:930000,7000:1085000,8000:1240000,9000:1395000,10000:1550000},
  "via_komunitas":{500:70000,600:81000,700:94500,800:108000,900:121500,1000:135000,1200:162000,1500:202500,2000:270000,2500:337500,3000:405000,3500:472500,4000:540000,4500:607500,5000:675000,5500:742500,6000:810000,6500:877500,7000:945000,7500:1012500,8000:1080000,8500:1147500,9000:1215000,9500:1282500,10000:1350000},
  "plus":{450:110000,500:225000,1000:300000,2000:455000,2200:455000},
  "limited":{k:v["harga"] for k,v in LIMITED_ITEMS.items()}
}
DEFAULT_PRICELIST=DEFAULT_PRICELIST_PER_KATEGORI["via_username"].copy()
PRICELIST_FILE="pricelist.json"
def _load_all_pricelist_raw():
    try:
        with open(PRICELIST_FILE,"r") as f:
            d=json.load(f)
            if isinstance(d,dict): return d
    except: return {}
    return {}
def load_pricelist(kategori="via_username"):
    kategori=kategori_alias(kategori);raw=_load_all_pricelist_raw()
    if kategori in raw and isinstance(raw[kategori],dict):
        try:
            if kategori=="limited": return {str(k):int(v) for k,v in raw[kategori].items()}
            return {int(k):int(v) for k,v in raw[kategori].items()}
        except: pass
    return DEFAULT_PRICELIST_PER_KATEGORI.get(kategori,DEFAULT_PRICELIST).copy()
def save_pricelist(data,kategori="via_username"):
    kategori=kategori_alias(kategori);raw=_load_all_pricelist_raw()
    if not raw or list(raw.keys())[0].isdigit(): raw={}
    for kat in ["via_username","via_login","via_komunitas","plus","limited"]:
        if kat not in raw:
            if kat=="limited": raw[kat]={str(k):v for k,v in DEFAULT_PRICELIST_PER_KATEGORI[kat].items()}
            else: raw[kat]={str(k):v for k,v in DEFAULT_PRICELIST_PER_KATEGORI[kat].items()}
    if kategori=="limited": raw[kategori]={str(k):int(v) for k,v in data.items()}
    else: raw[kategori]={str(k):int(v) for k,v in data.items()}
    with open(PRICELIST_FILE,"w") as f: json.dump(raw,f,indent=2)
    return True
def get_harga(robux,kategori="via_username"):
    kategori=kategori_alias(kategori)
    if kategori=="limited":
        d=load_pricelist("limited"); return int(d.get(str(robux), LIMITED_ITEMS.get(str(robux),{}).get("harga",0)))
    data=load_pricelist(kategori)
    try: robux=int(robux)
    except: return 0
    return int(data.get(robux,0))
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
def get_nominal_list(kategori):
    if kategori=="via_username": return [100,200,300,400,500,600,700,800,900,1000,1200,1500,2000,2500,3000,4000,5000,6000,7000,8000,9000,10000]
    if kategori=="via_login": return [500,600,700,800,900,1000,1200,1500,2000,2500,3000,4000,5000,6000,7000,8000,9000,10000]
    if kategori=="via_komunitas": return [500,600,700,800,900,1000,1200,1500,2000,2500,3000,3500,4000,4500,5000,5500,6000,6500,7000,7500,8000,8500,9000,9500,10000]
    if kategori=="plus": return [450,500,1000,2000,2200]
    if kategori=="limited": return list(LIMITED_ITEMS.keys())
    return [100,500,1000]

def build_pricelist_text(kategori="via_username"):
    kategori=kategori_alias(kategori)
    if not is_open(kategori): return f"🔴 **{kategori.upper()} LAGI HABIS!**\n\nMaaf ya, stok {kategori} lagi habis / tutup sementara!\nCoba kategori lain dulu ya 💗"
    data=load_pricelist(kategori)
    def h(n): return format_rp(data.get(int(n),get_harga(n,kategori)))
    if kategori=="via_username":
        txt="✨ Robux dikirim langsung ke akun kamu, tanpa login, tanpa ribet!\n💎 Aman • Cepat • Terpercaya • Garansi 100%\n\n━━━━━━━━━━━━━━━━━━\n🌸 ECERAN\n━━━━━━━━━━━━━━━━━━\n"
        for n in [100,200,300,400]: txt+=f"💠 {n} Robux — {h(n)}\n"
        txt+="\n━━━━━━━━━━━━━━━━━━\n💎 HEMAT — Paling Laris!\n━━━━━━━━━━━━━━━━━━\n"
        for n in [500,600,700,800,900,1000]: txt+=f"✨ {n} Robux — {h(n)}\n"
        txt+="\n━━━━━━━━━━━━━━━━━━\n👑 SULTAN\n━━━━━━━━━━━━━━━━━━\n"
        for n in [1200,1500,2000,2500,3000,4000,5000,6000,7000,8000,9000,10000]: txt+=f"👑 {n} Robux — {h(n)}\n"
        txt+=f"\n━━━━━━━━━━━━━━━━━━\n🛍️ CARA ORDER\n━━━━━━━━━━━━━━━━━━\n1️⃣ Klik tombol ORDER di <#{OPEN_TICKET_CHANNEL_ID}>\n2️⃣ Isi Nickname + Username + Paket\n3️⃣ Scan QRIS & kirim bukti\n4️⃣ Robux langsung masuk!\n\n💳 Pembayaran: QRIS ONLY!\n⚡ Proses: 1-15 Menit (Jam Kerja)\n💗 Mipi Store — Rafi Store"
        return txt
    if kategori=="via_login":
        txt="🔑 **ROBUX VIA LOGIN — MIPI STORE**\n✨ Akun diproses langsung, aman & cepat!\n\n━━━━━━━━━━━━━━━━━━\n💎 PAKET VIA LOGIN (500 - 10.000)\n━━━━━━━━━━━━━━━━━━\n"
        for n in get_nominal_list("via_login"): txt+=f"✨ {n} Robux — {h(n)}\n"
        txt+=f"\n⚠️ Wajib ganti password sementara / kasih kode verif ke admin!\n🛍️ Order di <#{OPEN_TICKET_CHANNEL_ID}>\n💗 Mipi Store"
        return txt
    if kategori=="via_komunitas":
        txt="👥 **ROBUX VIA KOMUNITAS — MIPI STORE**\n✨ Via Group / Community, payout aman!\n\n━━━━━━━━━━━━━━━━━━\n💎 PAKET KOMUNITAS (500 - 10.000)\n━━━━━━━━━━━━━━━━━━\n"
        for n in get_nominal_list("via_komunitas"): txt+=f"✨ {n} Robux — {h(n)}\n"
        txt+=f"\n📋 Syarat: Join grup dulu, tunggu 14 hari (aturan Roblox)!\n🛍️ Order di <#{OPEN_TICKET_CHANNEL_ID}>\n💗 Mipi Store"
        return txt
    if kategori=="plus":
        return f"⭐ **ROBLOX PLUS — PENGGANTI PREMIUM**\n✨ Robux masuk otomatis tiap bulan!\n\n━━━━━━━━━━━━━━━━━━\n💎 PAKET PLUS\n━━━━━━━━━━━━━━━━━━\n🌸 Plus 450 (Subscribe Indo 1 Bulan) — {format_rp(data.get(450,110000))}\n✨ Plus 500 — {format_rp(data.get(500,225000))}\n✨ Plus 1000 — {format_rp(data.get(1000,300000))}\n👑 Plus 2000 / 2200 — {format_rp(data.get(2200,455000))}\n\n💡 Plus = Premium versi Mipi, Robux cair tiap bulan!\n🛍️ Order di <#{OPEN_TICKET_CHANNEL_ID}>\n💗 Mipi Store"
    if kategori=="limited":
        txt="<a:announce:1506170564677472306> UPDATE HARGA ITEM LIMITED\n\n"
        for kode,item in LIMITED_ITEMS.items():
            harga=data.get(kode,item["harga"])
            txt+=f"{item['emoji']}  {item['nama']} : RP. {int(harga):,}\n".replace(",",".")
        txt+=f"\n# ALL ITEM CLEAN BERGARANSI <a:tandaseru:1523583702137962526>  **READY**\n\n🛍️ Order di <#{OPEN_TICKET_CHANNEL_ID}>\n💗 Mipi Store"
        return txt
    return "Pricelist lagi error, coba /lihat-harga lagi ya!"

CATEGORY_PRICELIST={"via_username":{"title":"💎 PRICELIST ROBUX VIA USERNAME — MIPI STORE","image":VIA_USERNAME_URL,"desc":"✨ Fast Process • Aman • Instan"},"via_login":{"title":"🔑 PRICELIST ROBUX VLOG / VIA LOGIN","image":VIA_LOGIN_URL,"desc":"Via Login / Vlog - Proses Cepat"},"via_komunitas":{"title":"👥 PRICELIST ROBUX VIA KOMUNITAS","image":VIA_KOMUNITAS_URL,"desc":"Via Komunitas / Group"},"plus":{"title":"⭐ PRICELIST ROBLOX PLUS","image":PLUS_URL,"desc":"Roblox Plus Monthly"},"limited":{"title":"💠 PRICELIST LIMITED ITEM","image":LIMITED_URL,"desc":"Beli / Jual Limited Via Trade"}}
def build_pricelist_embed(kategori="via_username"):
    info=CATEGORY_PRICELIST.get(kategori,CATEGORY_PRICELIST["via_username"])
    e=discord.Embed(title=info["title"],description=info["desc"]+"\n\n"+build_pricelist_text(kategori),color=0xff69b4)
    e.set_image(url=info["image"]);e.set_footer(text="Mipi Store - Rafi Store | Harga bisa berubah sewaktu-waktu");return e
def build_all_pricelist_embeds(): return [build_pricelist_embed(k) for k in ["via_username","via_login","via_komunitas","plus","limited"]]
def build_rekber_embed():
    e=discord.Embed(title="🛡️ Middleman / Rekber Service by MIPI STORE",description=("✨ Transaksi aman, tanpa takut ketipu!\n\n━━━━━━━━━━━━━━━━━━\n💰 Daftar Fee Middleman\n━━━━━━━━━━━━━━━━━━\n🌸 Rp 1.000 — Rp 9.000 → Fee **Rp 1.500**\n💠 Rp 10.000 — Rp 49.000 → Fee **Rp 1.500**\n💠 Rp 50.000 — Rp 99.000 → Fee **Rp 1.500**\n✨ Rp 100.000 — Rp 199.000 → Fee **Rp 2.500**\n✨ Rp 200.000 — Rp 499.000 → Fee **Rp 4.000**\n👑 Rp 500.000 — Rp 1.000.000 → Fee **Rp 7.000**\n👑 Di atas Rp 1.000.000 → Fee **Rp 10.000**\n\n━━━━━━━━━━━━━━━━━━\n🛍️ Cara Order\n━━━━━━━━━━━━━━━━━━\n"+f"1️⃣ Klik tombol 🎫 Buat Ticket Middleman di bawah / Open Ticket di <#{OPEN_TICKET_CHANNEL_ID}>\n2️⃣ Isi Buyer, Seller, Jenis Barang, Harga, dan Fee Ditanggung\n3️⃣ Tunggu admin verifikasi & proses\n4️⃣ Deal! 💗\n\n💗 Mipi Store — Rafi Store"),color=0xff69b4);e.set_image(url=WELCOME_URL);e.set_footer(text="MIPI STORE • Rekber / Middleman • 100% Aman");return e
class RekberView(discord.ui.View):
    def __init__(self,guild_id=None):
        super().__init__(timeout=None);url=f"https://discord.com/channels/{guild_id}/{OPEN_TICKET_CHANNEL_ID}" if guild_id else f"https://discord.com/channels/@me/{OPEN_TICKET_CHANNEL_ID}";self.add_item(discord.ui.Button(label="🎫 Buat Ticket Middleman",style=discord.ButtonStyle.link,url=url,emoji="🎫"));self.add_item(discord.ui.Button(label="💬 Open Ticket",style=discord.ButtonStyle.link,url=url,emoji="💬"))
def jenis_to_kategori(jenis):
    j=str(jenis).upper()
    if "VIA LOGIN" in j: return "via_login"
    if "VIA KOMUNITAS" in j: return "via_komunitas"
    if "PLUSS" in j or "PLUS" in j: return "plus"
    if "LIMITED" in j or "OFFSALE" in j: return "limited"
    return "via_username"
def load_produk():
    try:
        with open("produk.json","r") as f:
            d=json.load(f)
            if isinstance(d,dict): return d
    except: pass
    return {"robux_visend":{"nama":"💎 Robux Via Username","harga":80000,"stok":9999,"deskripsi":"Robux via username, 500 Robux","emoji":"💎","kategori":"via_username"}}
def save_produk(d): _save("produk.json",d)
def build_produk_embed():
    d=load_produk();desc="💗 **KATALOG PRODUK MIPI STORE**\n\n━━━━━━━━━━━━━━━━━━\n"
    if not d: desc+="> Belum ada produk!\n"
    else:
        for kode,p in d.items():
            stok_txt="🟢 READY (Unlimited)" if p.get("stok",0)>1000 else f"{'🟢 READY' if p.get('stok',0)>0 else '🔴 HABIS'} ({p.get('stok',0)} stok)"
            desc+=f"{p.get('emoji','📦')} **{p.get('nama','Produk')}**\n└ Kode: `{kode}` | Harga: {format_rp(p.get('harga',0))} | {stok_txt}\n└ {p.get('deskripsi','')}\n\n"
    desc+="━━━━━━━━━━━━━━━━━━\n🛍️ Order: Pencet tombol di #open-ticket\n💗 Mipi Store - Rafi Store";e=discord.Embed(title="🛍️ KATALOG PRODUK - MIPI STORE",description=desc,color=0xff69b4);e.set_image(url=WELCOME_URL);e.set_footer(text="MIPI STORE • Katalog Produk");return e
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
        data[bulan][uid]["username"]=username;data[bulan][uid]["total"]+=jumlah;data[bulan][uid]["transaksi"]+=1;data[bulan][uid]["total_rp"]+=harga;save_leaderboard(data)
    except Exception as e: print(f"add leaderboard error: {e}")
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
        if robux_jumlah is not None: jumlah=int(robux_jumlah);harga=int(harga_akhir) if harga_akhir else get_harga(jumlah,kategori)
        else:
            m=re.search(r'(\d+)',str(paket_text).replace('.','').replace(',',''))
            if not m: return None
            jumlah=int(m.group(1));harga=get_harga(jumlah,kategori)
        if jumlah<=0: return None
        data=load_pending();oid=f"ORDER-{ticket_number:06d}";data[oid]={"user_id":str(user_id),"username":username,"paket":paket_text,"robux":jumlah,"harga":harga,"ticket_number":ticket_number,"channel":channel_name,"kategori":kategori,"waktu":datetime.now().strftime("%d %b %Y %H:%M"),"referral_by":referral_by};save_pending(data);return oid
    except Exception as e: print(f"add pending error: {e}");return None
def load_referral(): return _load("referral.json",{})
def save_referral(d): _save("referral.json",d)
def get_referral_code(user_id): return f"MIPI-{int(user_id)%100000:05d}"
def claim_referral(new_user_id,code):
    try:
        if not code: return None
        data=load_referral()
        for uid,info in data.items():
            if info.get("code")==code.upper() and str(uid)!=str(new_user_id): return uid
        return None
    except: return None
def add_referral_komisi(referrer_id,buyer_harga,buyer_name):
    try:
        komisi=int(buyer_harga*REFERRAL_RATE);data=load_referral();uid=str(referrer_id)
        if uid not in data: data[uid]={"code":get_referral_code(referrer_id),"total_komisi":0,"total_referral":0,"history":[]}
        data[uid]["total_komisi"]+=komisi;data[uid]["total_referral"]+=1;data[uid]["history"].append({"buyer":buyer_name,"harga":buyer_harga,"komisi":komisi,"waktu":datetime.now().strftime("%d %b %Y %H:%M")});save_referral(data);return komisi
    except: return 0
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
def load_daily(): return _load("daily.json",{})
def save_daily(d): _save("daily.json",d)
def claim_daily(user_id):
    try:
        data=load_daily();uid=str(user_id);today=datetime.now().strftime("%Y-%m-%d")
        if uid in data and data[uid].get("last_claim")==today: return None,data[uid].get("poin",0),"Kamu udah claim hari ini!"
        if uid not in data: data[uid]={"poin":0,"streak":0,"last_claim":""}
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
                u=await bot.fetch_user(int(uid));await u.send(f"🔔 **RESTOCK!** {kategori.upper()} udah DIBUKA lagi di MIPI STORE! 💗\nOrder di <#{OPEN_TICKET_CHANNEL_ID}>")
            except: pass
        d[kategori]=[];save_notify(d)
    except: pass
game_data={}
def start_tebak_harga():
    nominal=random.choice([100,200,300,400,500,1000,2000]);harga=get_harga(nominal,"via_username");pilihan=[harga]
    while len(pilihan)<4:
        fake=int(harga*random.uniform(0.7,1.4)/500)*500
        if fake not in pilihan and fake>0: pilihan.append(fake)
    random.shuffle(pilihan);return nominal,harga,pilihan
def get_top_sultan_channel(guild):
    try:
        for ch in guild.text_channels:
            if "top-sultan" in ch.name.lower() or "top-leaderboard" in ch.name.lower(): return ch
    except: pass
    return None
def build_top_sultan_embed_bulanan():
    try:
        data=load_leaderboard();bulan_ini=datetime.now().strftime("%Y-%m");users=data.get(bulan_ini,{});s=sorted(users.items(),key=lambda x: x[1].get("total_rp",0),reverse=True)[:10];nama_bulan=datetime.now().strftime("%B %Y");desc=f"MIPI STORE • LEADERBOARD BULANAN - {nama_bulan}\n\n"
        if not s: desc+="> Belum ada Sultan bulan ini!\n\n"
        else:
            medals=["🥇","🥈","🥉"]
            for i,(uid,info) in enumerate(s):
                medal=medals[i] if i<3 else "🏅";desc+=f"{medal} **#{i+1} - <@{uid}>** ({info.get('username','User')})\n└ Rp {info.get('total_rp',0):,} • {info.get('transaksi',0)}x\n".replace(",",".")
        desc+=f"\n🕒 Update: {datetime.now().strftime('%Y-%m-%d %H:%M')} WIB";e=discord.Embed(title=f"🏆 TOP 10 SULTAN BULANAN - {nama_bulan}",description=desc,color=0xff69b4);e.set_image(url=TOP_SULTAN_IMAGE);return e
    except: return discord.Embed(title="Top Sultan",description="Error",color=0xff0000)
def build_top_sultan_embed_semua():
    try:
        data=load_leaderboard();gabung={}
        for bulan,users in data.items():
            for uid,info in users.items():
                if uid not in gabung: gabung[uid]={"username":info.get("username","User"),"total_rp":0,"total":0,"transaksi":0}
                gabung[uid]["total_rp"]+=info.get("total_rp",0);gabung[uid]["total"]+=info.get("total",0);gabung[uid]["transaksi"]+=info.get("transaksi",0)
        s=sorted(gabung.items(),key=lambda x: x[1]["total_rp"],reverse=True)[:10];desc="MIPI STORE • LEADERBOARD SEMUA / ALL TIME\n\n"
        if not s: desc+="> Belum ada Sultan!\n\n"
        else:
            medals=["🥇","🥈","🥉"]
            for i,(uid,info) in enumerate(s):
                medal=medals[i] if i<3 else "🏅";desc+=f"{medal} **#{i+1} - <@{uid}>** ({info['username']})\n└ Rp {info['total_rp']:,} • {info['transaksi']}x\n".replace(",",".")
        e=discord.Embed(title="👑 TOP 10 SULTAN SEMUA / ALL TIME",description=desc,color=0x2B2D31);e.set_image(url=TOP_SULTAN_IMAGE);return e
    except: return discord.Embed(title="Top Sultan",description="Error",color=0xff0000)
def build_top_sultan_embed(): return build_top_sultan_embed_semua()
async def update_top_sultan(guild):
    try:
        ch=get_top_sultan_channel(guild)
        if not ch: return
        embed=build_top_sultan_embed_semua()
        async for msg in ch.history(limit=20):
            if msg.author==guild.me and msg.embeds and "TOP 10 SULTAN" in str(msg.embeds[0].title): await msg.edit(embed=embed);return
        await ch.send(embed=embed)
    except Exception as e: print(f"update top error: {e}")
@tasks.loop(minutes=1)
async def auto_update_top_sultan():
    for guild in bot.guilds:
        try: await update_top_sultan(guild)
        except: pass
async def check_auto_role(guild,user_id,total_rp):
    try:
        member=guild.get_member(int(user_id))
        if not member: return None
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
            await member.add_roles(role);return target
        return None
    except: return None
def is_admin_or_owner(user,guild):
    try:
        if user.id==guild.owner_id: return True
        if user.guild_permissions.administrator: return True
        rn=[r.name.lower() for r in user.roles]
        return any(x in rn for x in ["admin","owner","staff","moderator","adm"])
    except: return False
        # ===== PART 2 - VIEWS, MODAL, TICKET, PRICELIST DROPDOWN =====
class KonfirmasiSaldoView(discord.ui.View):
    def __init__(self,order_id):
        super().__init__(timeout=None);self.order_id=order_id
    @discord.ui.button(label="✅ Konfirmasi Masuk Saldo",style=discord.ButtonStyle.success,custom_id="saldo_confirm_btn")
    async def confirm_btn(self,interaction:discord.Interaction,button:discord.ui.Button):
        if not is_admin_or_owner(interaction.user,interaction.guild): await interaction.response.send_message("❌ Hanya Admin / Owner!",ephemeral=True);return
        pend=load_pending()
        if self.order_id not in pend: await interaction.response.send_message("❌ Udah dikonfirmasi / ditolak!",ephemeral=True);return
        d=pend[self.order_id];add_to_leaderboard(int(d["user_id"]),d["username"],d["paket"],kategori=d.get("kategori","via_username"));del pend[self.order_id];save_pending(pend)
        komisi_txt=""
        if d.get("referral_by"):
            komisi=add_referral_komisi(d["referral_by"],d["harga"],d["username"]);komisi_txt=f"\n💸 Referral: <@{d['referral_by']}> dapet {format_rp(komisi)} (5%)!"
        await interaction.response.send_message(f"✅ **SALDO DIKONFIRMASI!**\nBuyer: <@{d['user_id']}>\nPaket: {d['paket']}\n+{d['robux']} R$ udah masuk saldo!{komisi_txt}",ephemeral=False)
        for item in self.children: item.disabled=True
        try: await interaction.message.edit(view=self)
        except: pass
        try: await update_top_sultan(interaction.guild)
        except: pass
    @discord.ui.button(label="❌ Tolak / Order Palsu",style=discord.ButtonStyle.danger,custom_id="saldo_reject_btn")
    async def reject_btn(self,interaction:discord.Interaction,button:discord.ui.Button):
        if not is_admin_or_owner(interaction.user,interaction.guild): await interaction.response.send_message("❌ Hanya Admin / Owner!",ephemeral=True);return
        pend=load_pending()
        if self.order_id not in pend: await interaction.response.send_message("❌ Udah diproses!",ephemeral=True);return
        d=pend[self.order_id];del pend[self.order_id];save_pending(pend);await interaction.response.send_message(f"❌ Order {self.order_id} DITOLAK!",ephemeral=False)
        for item in self.children: item.disabled=True
        try: await interaction.message.edit(view=self)
        except: pass
PROMO_FILE="promo.json"
def load_promo(): return _load(PROMO_FILE,{})
def save_promo(d): _save(PROMO_FILE,d)
def cek_promo(kode,harga_awal,jumlah_robux=0):
    try:
        if not kode or not str(kode).strip(): return harga_awal,0,None
        kode=str(kode).upper().strip();data=load_promo()
        if kode not in data: return harga_awal,0,"Kode promo tidak ditemukan!"
        p=data[kode]
        if jumlah_robux<500: return harga_awal,0,"Minimal 500 Robux!"
        if p.get("dipakai",0)>=p.get("max",999): return harga_awal,0,"Promo habis!"
        diskon=int(harga_awal*p["diskon"]/100) if p["tipe"]=="persen" else int(p["diskon"]);return max(0,harga_awal-diskon),diskon,None
    except: return harga_awal,0,None
giveaway_data={}
class GiveawayView(discord.ui.View):
    def __init__(self,giveaway_id):
        super().__init__(timeout=None);self.giveaway_id=giveaway_id
    @discord.ui.button(label="JOIN GIVEAWAY",style=discord.ButtonStyle.success,custom_id="join_giveaway",emoji="🎉")
    async def join_btn(self,interaction:discord.Interaction,button:discord.ui.Button):
        data=giveaway_data.get(self.giveaway_id)
        if not data or data["ended"]: await interaction.response.send_message("Giveaway berakhir!",ephemeral=True);return
        if interaction.user.id in data["peserta"]: await interaction.response.send_message("Udah join!",ephemeral=True);return
        data["peserta"].append(interaction.user.id);await interaction.response.send_message("Berhasil join!",ephemeral=True)
async def end_giveaway(guild,channel_id,message_id,giveaway_id):
    try:
        data=giveaway_data.get(giveaway_id)
        if not data or data["ended"]: return
        data["ended"]=True;channel=guild.get_channel(channel_id)
        if not channel: return
        try: msg=await channel.fetch_message(message_id)
        except: msg=None
        if len(data["peserta"])==0:
            await channel.send("Giveaway berakhir, gak ada yang join!");return
        winners=random.sample(data["peserta"],min(data["pemenang"],len(data["peserta"])));wm=", ".join([f"<@{w}>" for w in winners]);await channel.send(f"GIVEAWAY BERAKHIR!\nHadiah: {data['hadiah']}\nPemenang: {wm}")
    except: pass
BANNED_WORDS=["wts robux","jual robux","sell robux","jual rb","wts rb","jual limited","wts limited","sell limited","jual robux murah","robux murah","top up robux"]
SCAM_LINKS=["discord.gg/","bit.ly/","tinyurl.com/","free-robux","robux-free"]
def is_banned_selling(text):
    try: return any(w in str(text).lower() for w in BANNED_WORDS)
    except: return False
def is_scam_link(text):
    try: return any(s in str(text).lower() for s in SCAM_LINKS)
    except: return False
def hitung_harga(paket_text,kategori="via_username",robux_jumlah=None,harga_akhir=None):
    try:
        if robux_jumlah is not None:
            j=int(robux_jumlah);h=int(harga_akhir) if harga_akhir else get_harga(j,kategori);return str(j),format_rp(h)
        m=re.search(r'(\d+)',str(paket_text).replace('.','').replace(',',''))
        if not m: return "500",format_rp(get_harga(500,kategori))
        jumlah=int(m.group(1));return str(jumlah),format_rp(get_harga(jumlah,kategori))
    except: return "500",format_rp(get_harga(500,kategori))
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
def get_omset_channel(guild):
    for ch in guild.text_channels:
        if "omset" in ch.name.lower() or "rekap" in ch.name.lower() or "history" in ch.name.lower(): return ch
    return get_history_channel(guild)
def make_html_transcript(number,messages,username,paket,duration):
    rows=""
    for m in messages: rows+="<div>"+html.escape(str(m["author"]))+" | "+m["time"]+"<br>"+html.escape(m["content"] or "(gambar)")+"</div>"
    return f"<html><body><h2>Ticket #{number} - {html.escape(username)} - {html.escape(paket)}</h2>{rows}</body></html>"
async def send_status_update(guild,number,username,user_id,paket,status_text,color):
    try:
        ch=get_status_channel(guild)
        if not ch: return
        embed=discord.Embed(title=f"Order Status - Ticket #{number}",description=f"Customer: <@{user_id}> ({username})\nPaket: {paket}\nStatus: {status_text}",color=color);await ch.send(embed=embed)
    except: pass
async def send_history_log(guild,channel,data,admin_user):
    try:
        ch=get_history_channel(guild)
        if not ch: return
        jumlah,harga=hitung_harga(data.get("paket","500 Robux"),data.get("kategori","via_username"),robux_jumlah=data.get("robux_jumlah"),harga_akhir=data.get("harga_akhir"))
        embed=discord.Embed(color=0x2b2d31);embed.description=f"Ticket Log\n\nTicket\n{channel.name if channel else 'ticket'}\nMember\n<@{data['user_id']}>\nNickname\n{data.get('nickname','-')}\nUsername\n{data.get('roblox_username','-')}\nJumlah\n{jumlah}\nTotal\n{harga}\nAdmin\n{admin_user.mention if admin_user else 'Auto-Close'}";embed.set_image(url=THANKYOU_URL);await ch.send(embed=embed)
    except: pass
async def send_vouch(guild,user,paket,stars,komentar,ticket_number=0,ticket_name=""):
    try:
        ch=get_vouch_channel(guild)
        if not ch: return
        jumlah,harga=hitung_harga(paket);embed=discord.Embed(color=0x2b2d31);embed.description=f"VOUCH RECEIVED\n\nTicket ID\n{ticket_number}\nNominal\n{harga}\nBuyer\n<@{user.id}>\nRating\n{'⭐'*stars}\nKomentar\n{komentar} 💗";embed.set_thumbnail(url=user.display_avatar.url);await ch.send(embed=embed)
    except: pass
def get_statistik():
    try:
        data=load_leaderboard();bulan=datetime.now().strftime("%Y-%m");bulan_rp=bulan_tr=all_rp=all_tr=0;pend=load_pending();hari_rp=sum(d.get("harga",0) for d in pend.values());hari_tr=len(pend)
        for b,users in data.items():
            for uid,info in users.items():
                if b=="ALLTIME": continue
                all_rp+=info.get("total_rp",0);all_tr+=info.get("transaksi",0)
                if b==bulan: bulan_rp+=info.get("total_rp",0);bulan_tr+=info.get("transaksi",0)
        return {"hari_rp":hari_rp,"hari_tr":hari_tr,"bulan_rp":bulan_rp,"bulan_tr":bulan_tr,"all_rp":all_rp,"all_tr":all_tr}
    except: return {"hari_rp":0,"hari_tr":0,"bulan_rp":0,"bulan_tr":0,"all_rp":0,"all_tr":0}
async def do_auto_close(guild,channel,data,reason="auto-closed",admin_user=None):
    try:
        number=data["number"];user_id=data["user_id"];paket=data.get("paket","ORDER ROBUX");duration=int((time.time()-data["created_at"])//60) or 1
        user_last_ticket[user_id]={"number":number,"paket":paket,"ticket_name":channel.name if channel else "","seller_id":guild.owner_id}
        try: await send_history_log(guild,channel,data,admin_user)
        except: pass
        try:
            user=await bot.fetch_user(user_id);embed=discord.Embed(title="Rate Your Experience",description=f"Hi {user.name}! Ticket #{number} sudah selesai.\nRate ya!",color=0x2b2d31);await user.send(embed=embed,view=RatingView(number))
        except: pass
        try:
            order_id=add_to_pending(user_id,data.get("username","User"),paket,number,channel.name if channel else "",kategori=data.get("kategori","via_username"),robux_jumlah=data.get("robux_jumlah"),harga_akhir=data.get("harga_akhir"),referral_by=data.get("referral_by"))
            if order_id:
                ch_pending=get_history_channel(guild) or get_status_channel(guild)
                if ch_pending:
                    jumlah_tmp,harga_tmp=hitung_harga(paket,data.get("kategori","via_username"),robux_jumlah=data.get("robux_jumlah"),harga_akhir=data.get("harga_akhir"));embed_p=discord.Embed(title=f"⏳ PENDING SALDO - {order_id}",description=f"Buyer: <@{user_id}>\nPaket: {paket}\nRobux: {jumlah_tmp} R$\nHarga: {harga_tmp}\nTicket: #{number}\n\nAdmin pencet ✅ dulu baru masuk saldo!",color=0xfee75c);await ch_pending.send(embed=embed_p,view=KonfirmasiSaldoView(order_id))
        except: pass
        if channel.id in ticket_data: del ticket_data[channel.id]
        try: await channel.delete()
        except: pass
    except Exception as e: print(f"do_auto_close error: {e}")
@tasks.loop(minutes=1)
async def check_inactive():
    try:
        now=time.time()
        for channel_id,data in list(ticket_data.items()):
            last=data.get("last_activity",data["created_at"])
            if now-last>15*60:
                ch=bot.get_channel(channel_id)
                if not ch: del ticket_data[channel_id];continue
                await do_auto_close(ch.guild,ch,data)
    except: pass
@tasks.loop(minutes=60)
async def auto_rekap_omset():
    try:
        now=datetime.now()
        if now.hour!=0: return
        for guild in bot.guilds:
            s=get_statistik();ch=get_omset_channel(guild)
            if not ch: continue
            e=discord.Embed(title="📊 REKAP OMSET HARIAN",description=f"📅 {now.strftime('%d %B %Y')}\n\n💰 Bulan Ini: {format_rp(s['bulan_rp'])} ({s['bulan_tr']} transaksi)\n👑 All Time: {format_rp(s['all_rp'])} ({s['all_tr']} transaksi)",color=0xff69b4);await ch.send(embed=e)
    except: pass
class RatingView(discord.ui.View):
    def __init__(self,ticket_number):
        super().__init__(timeout=None);self.ticket_number=ticket_number
    async def send_thanks(self,interaction,stars):
        user_ratings[interaction.user.id]=stars;embed=discord.Embed(title="Terima Kasih! 💗",description=f"Kamu memberi rating {'⭐'*stars} ({stars}/5)!",color=0xff69b4);embed.set_image(url=THANKYOU_URL);await interaction.response.edit_message(embed=embed,view=self)
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
        await interaction.response.send_modal(CommentModal(ticket_number=self.ticket_number))
    @discord.ui.button(label="❌ No Thanks",style=discord.ButtonStyle.secondary,custom_id="no_thanks",row=1)
    async def no_thanks(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.edit_message(content="Oke! Terima kasih sudah order di MIPI STORE 💗",embed=None,view=None)
class CommentModal(discord.ui.Modal,title="Komentar / Testimoni"):
    def __init__(self,ticket_number):
        super().__init__();self.ticket_number=ticket_number
    komentar=discord.ui.TextInput(label="Komentar kamu",placeholder="satset poll",style=discord.TextStyle.paragraph,required=True)
    async def on_submit(self,interaction:discord.Interaction):
        stars=user_ratings.get(interaction.user.id,5);last=user_last_ticket.get(interaction.user.id,{});paket=last.get("paket","500 Robux")
        for g in bot.guilds:
            if get_vouch_channel(g): await send_vouch(g,interaction.user,paket,stars,self.komentar.value,ticket_number=self.ticket_number);break
        await interaction.response.send_message("Terima kasih komentarnya! 💗 Vouch kamu sudah muncul!",ephemeral=True)
class StatusView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="⏳ Menunggu Pembayaran",style=discord.ButtonStyle.secondary,custom_id="status_waiting")
    async def waiting(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not is_admin_or_owner(interaction.user,interaction.guild): await interaction.followup.send("Hanya Admin!",ephemeral=True);return
        data=ticket_data.get(interaction.channel.id,{})
        await interaction.followup.send("Status: Menunggu Pembayaran");await send_status_update(interaction.guild,data.get("number","?"),data.get("username",""),data.get("user_id",interaction.user.id),data.get("paket","ORDER"),"Menunggu Pembayaran",0xfee75c)
    @discord.ui.button(label="🔄 Diproses",style=discord.ButtonStyle.primary,custom_id="status_process")
    async def process(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not is_admin_or_owner(interaction.user,interaction.guild): await interaction.followup.send("Hanya Admin!",ephemeral=True);return
        data=ticket_data.get(interaction.channel.id,{})
        await interaction.followup.send("Status: Diproses");await send_status_update(interaction.guild,data.get("number","?"),data.get("username",""),data.get("user_id",interaction.user.id),data.get("paket","ORDER"),"Diproses",0x5865f2)
    @discord.ui.button(label="✅ Selesai",style=discord.ButtonStyle.success,custom_id="status_done")
    async def done(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not is_admin_or_owner(interaction.user,interaction.guild): await interaction.followup.send("Hanya Admin!",ephemeral=True);return
        data=ticket_data.get(interaction.channel.id,{})
        await interaction.followup.send("Status: Selesai!");await send_status_update(interaction.guild,data.get("number","?"),data.get("username",""),data.get("user_id",interaction.user.id),data.get("paket","ORDER"),"Selesai",0x57f287)
class CloseView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🔒 CLOSE TICKET",style=discord.ButtonStyle.danger,custom_id="close_ticket")
    async def close_btn(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not is_admin_or_owner(interaction.user,interaction.guild): await interaction.followup.send("Hanya Admin!",ephemeral=True);return
        channel=interaction.channel;data=ticket_data.get(channel.id)
        if not data: await channel.delete();return
        await interaction.followup.send("Ticket ditutup...");await do_auto_close(interaction.guild,channel,data,reason="closed by owner",admin_user=interaction.user)
class SaldoView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="💳 CEK SALDO SAYA",style=discord.ButtonStyle.primary,custom_id="cek_saldo_btn")
    async def cek_saldo(self,interaction:discord.Interaction,button:discord.ui.Button):
        tr,tro,tt=get_total_belanja(interaction.user.id);lvl=get_level(tr);nxt,sisa=get_next_level(tr);poin=get_poin(interaction.user.id);embed=discord.Embed(color=0xff1493);embed.description=f"INFORMASI SALDO\n\nHalo {interaction.user.mention}\n\n🏆 Level: {lvl}\n➡️ Next: {nxt} (kurang {format_rp(sisa)})\n\nTotal Belanja: {format_rp(tr)}\nTotal Robux: {tro} R$\nTotal Transaksi: {tt}x\n🎁 Poin: {poin} poin";await interaction.response.send_message(embed=embed,ephemeral=True)
def build_ticket_panel_baru_embed():
    e=discord.Embed(title="🎫 Mipi Store - Ticket Order",description="💎 **Robux Via Username** - Beli Robux Via Username\n🔑 **Robux Vlog** - Beli Robux Via Login\n💠 **Beli Limited Item** - Beli Item Via Trade\n💰 **Jual Limited Item** - Cashout\n🎁 **Beli Item Offsale** - Via Redeem Code\n⭐ **Beli Roblox Plus** - Plus Monthly\n🛡️ **Rekber/MM** - Rekber, Akun, Jasa\n🐱 **Other/Nanya** - Pertanyaan\n👥 **Via Komunitas** - Via Group\n💃 **Beli Akun** - Beli Akun Sultan\n\n✨ **V5:** Referral 5% • Daily • Level • Voucher • Game!\nMipi Store 💗",color=0x2B2D31);e.set_image(url=WELCOME_URL);e.set_footer(text="Mipi Store - Pilih tombol di bawah!");return e
class OrderModalBaru(discord.ui.Modal):
       def __init__(self,jenis:str):
        self.jenis=jenis
        super().__init__(title=f"Order - {jenis} | MIPI STORE")
        if jenis in ["VIA SEND","VIA LOGIN","VIA KOMUNITAS"]:
            l1,l2,l3="Username Roblox","Nominal Robux","Metode Pembayaran"
            p1,p2,p3="Contoh: RafixMP","Contoh: 200","Contoh: QRIS / Dana / Gopay"
        elif jenis in ["BELI LIMITED","JUAL LIMITED","OFFSALE"]:
            l1,l2,l3="Nama Item","Harga / Budget","Username Roblox"
            p1,p2,p3="Contoh: Classic Fedora","Contoh: 50000","Contoh: RafixMP"
        elif jenis=="BELI AKUN":
            l1,l2,l3="Akun Yang Dicari","Budget","Username Discord"
            p1,p2,p3="Contoh: Akun 2018+","Contoh: 100000","Contoh: m.rafii"
        elif jenis=="REKBER":
            l1,l2,l3="Barang Yang Direkber","Nominal","Username Penjual/Pembeli"
            p1,p2,p3="Contoh: Limited Fedora","Contoh: 200000","Contoh: @pembeli"
        else:
            l1,l2,l3="Keperluan","Detail","Username Roblox"
            p1,p2,p3="Contoh: Mau nanya stok","Tulis detailnya","Contoh: RafixMP"
        self.f1=discord.ui.TextInput(label=l1,placeholder=p1,required=True,max_length=100)
        self.f2=discord.ui.TextInput(label=l2,placeholder=p2,required=True,max_length=100)
        self.f3=discord.ui.TextInput(label=l3,placeholder=p3,required=False,max_length=100,style=discord.TextStyle.paragraph)
        self.add_item(self.f1);self.add_item(self.f2);self.add_item(self.f3)
        if jenis in ["VIA SEND","VIA LOGIN"]:
            self.promo=discord.ui.TextInput(label="Kode Promo (Opsional)",placeholder="Kosongkan jika tidak ada",required=False,max_length=20)
            self.ref=discord.ui.TextInput(label="Kode Referral (Opsional)",placeholder="Kosongkan jika tidak ada",required=False,max_length=20)
            self.add_item(self.promo);self.add_item(self.ref)
        else: self.promo=None;self.ref=None
    async def on_submit(self,interaction:discord.Interaction):
        global ticket_counter;ticket_counter+=1;guild=interaction.guild;overwrites={guild.default_role:discord.PermissionOverwrite(read_messages=False),interaction.user:discord.PermissionOverwrite(read_messages=True,send_messages=True),guild.me:discord.PermissionOverwrite(read_messages=True,send_messages=True)};category=get_ticket_category(guild);prefix=self.jenis.lower().replace(" ","-").replace("/","-");channel=await guild.create_text_channel(name=f"{prefix}-{ticket_counter}-{interaction.user.name}",overwrites=overwrites,category=category);paket_text=f"{self.jenis} - {self.f2.value}";harga_akhir=0;kategori=jenis_to_kategori(self.jenis);robux_jumlah_fix=0;ref_by=None
        if self.jenis in ["VIA SEND","VIA LOGIN","VIA KOMUNITAS"]:
            m_temp=re.search(r'(\d+)',str(self.f3.value).replace('.',''));jumlah_int=int(m_temp.group(1)) if m_temp else 500;robux_jumlah_fix=jumlah_int;harga_awal=get_harga(jumlah_int,kategori);kode_input=self.promo.value.strip() if self.promo and self.promo.value else "";harga_akhir,diskon,err_promo=cek_promo(kode_input,harga_awal,jumlah_int)
            if kode_input and not err_promo and diskon>0:
                pdata=load_promo();k_up=kode_input.upper()
                if k_up in pdata: pdata[k_up]["dipakai"]=pdata[k_up].get("dipakai",0)+1;save_promo(pdata)
            if self.ref and self.ref.value: ref_by=claim_referral(interaction.user.id,self.ref.value.strip())
        ticket_data[channel.id]={"user_id":interaction.user.id,"username":interaction.user.name,"nickname":self.f1.value,"roblox_username":self.f1.value,"pembayaran":"QRIS","created_at":time.time(),"last_activity":time.time(),"number":ticket_counter,"paket":paket_text,"promo":(self.promo.value if self.promo else ""),"harga_akhir":harga_akhir,"robux_jumlah":robux_jumlah_fix,"kategori":kategori,"referral_by":ref_by}
        embed=discord.Embed(title=f"Ticket Baru - {self.jenis} - {interaction.user.name}",description=f"**Jenis:** {self.jenis}\n**Data 1:** {self.f1.value}\n**Data 2:** {self.f2.value}\n**Data 3:** {self.f3.value}\n\nTicket #{ticket_counter}\nKirim bukti di sini ya 💗",color=0xff69b4);embed.set_image(url=WELCOME_URL);await channel.send(interaction.user.mention+" Halo! Selamat datang di MIPI STORE! 🌸",embed=embed,view=CloseView());embed_qris=discord.Embed(title="Scan QRIS Disini",description="Silahkan scan QRIS ini ya 💗",color=0xff69b4);embed_qris.set_image(url=QRIS_URL);await channel.send(embed=embed_qris);await channel.send("STATUS ORDER - Owner only:",view=StatusView());await send_status_update(guild,ticket_counter,interaction.user.name,interaction.user.id,paket_text,"Ticket Baru Dibuat",0xff69b4);go_view=discord.ui.View();go_view.add_item(discord.ui.Button(label="BUKA TICKET SAYA",style=discord.ButtonStyle.link,url=f"https://discord.com/channels/{guild.id}/{channel.id}",emoji="🚀"));await interaction.response.send_message(f"Ticket **{self.jenis}** kamu sudah dibuat!\n{channel.mention}",view=go_view,ephemeral=True)
class ButtonTicket(discord.ui.Button):
    def __init__(self,label,custom_id,row,emoji):
        super().__init__(label=label,style=discord.ButtonStyle.primary,custom_id=custom_id,row=row,emoji=emoji);self.jenis_map={"t_via_send":"VIA SEND","t_via_login":"VIA LOGIN","t_beli_limited":"BELI LIMITED","t_jual_limited":"JUAL LIMITED","t_pluss":"ROBLOX PLUSS","t_offsale":"BELI ITEM OFFSALE","t_rekber":"REKBER","t_other":"OTHER","t_komunitas":"VIA KOMUNITAS","t_beli_akun":"BELI AKUN"}
    async def callback(self,interaction:discord.Interaction):
        view=TicketTypeView()
        if not await view.cek_store(interaction): return
        jenis=self.jenis_map.get(self.custom_id,"VIA SEND");kat=jenis_to_kategori(jenis);kat_stock=kat
        if jenis=="REKBER": kat_stock="rekber"
        elif jenis=="BELI AKUN": kat_stock="beli_akun"
        elif jenis=="OTHER": kat_stock="other"
        if not is_open(kat_stock):
            await interaction.response.send_message(f"❌ Maaf, **{jenis}** lagi **HABIS / TUTUP**! Coba kategori lain ya 💗",ephemeral=True);return
        await interaction.response.send_modal(OrderModalBaru(jenis))
class TicketTypeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        def _label(base,kat_stock): return base if is_open(kat_stock) else base+" - HABIS"
        btns=[
          ("Robux Via Username","t_via_send",0,"<a:robux:1563387482182254725>","via_username"),
          ("Robux Vlog","t_via_login",0,"<:emoji_10:1431192496876027975>","via_login"),
          ("Beli Limited Item","t_beli_limited",1,"<a:diamond:1516624681585869041>","limited"),
          ("Jual Limited Item","t_jual_limited",1,"<a:moneybag:1512329138172596265>","limited"),
          ("Beli Roblox Plus","t_pluss",2,"<:b_RobloxPlus:1499160341983006730>","plus"),
          ("Beli Item Offsale","t_offsale",2,"<a:emoji_20:1550165111333986354>","limited"),
          ("Rekber/MM","t_rekber",3,"<a:emoji_39:1555770513907916822>","rekber"),
          ("Other/Nanya","t_other",3,"<a:b_bluequestion:1345684551502008340>","other"),
          ("Via Komunitas","t_komunitas",4,"<a:rbx:1530537752729223308>","via_komunitas"),
          ("Beli Akun","t_beli_akun",4,"<a:star_purple:1303353812374913035>","beli_akun"),
        ]
        for label,cid,row,emoji,kat_stock in btns:
            b=ButtonTicket(_label(label,kat_stock),cid,row=row,emoji=emoji)
            if not is_open(kat_stock): b.disabled=True;b.style=discord.ButtonStyle.secondary
            self.add_item(b)
    async def cek_store(self,interaction):
        if STORE_STATUS=="break":
            await interaction.response.send_message("MIPI STORE LAGI BREAK! ☕ 15-30 menit!",ephemeral=True);return False
        if STORE_STATUS=="closed":
            await interaction.response.send_message("MIPI STORE UDAH TUTUP! 💤 Balik besok!",ephemeral=True);return False
        return True
OrderView=TicketTypeView
# ===== PART 3 - EDIT PRICELIST, PRODUK, PRICELIST DROPDOWN, COMMANDS =====
class EditHargaModal(discord.ui.Modal, title="✏️ Edit Harga"):
    def __init__(self, kategori, nominal, harga_lama):
        super().__init__();self.kategori=kategori;self.nominal=nominal;self.harga_lama=harga_lama;self.harga_input=discord.ui.TextInput(label=f"Harga Baru {nominal} ({kategori})",placeholder=f"Lama: {harga_lama} - Contoh: 75000",required=True,max_length=10);self.add_item(self.harga_input)
    async def on_submit(self, interaction: discord.Interaction):
        try:
            teks=self.harga_input.value.replace("Rp","").replace(".","").replace(",","").replace(" ","").strip();harga_baru=int(teks)
            if self.kategori=="limited":
                d=load_pricelist("limited");d[str(self.nominal)]=harga_baru;save_pricelist(d,"limited")
            else:
                d=load_pricelist(self.kategori);d[int(self.nominal)]=harga_baru;save_pricelist(d,self.kategori)
            try: await update_all_panels(interaction.guild)
            except: pass
            await interaction.response.send_message(f"✅ Harga {self.kategori} {self.nominal} jadi {format_rp(harga_baru)}! Panel udah ke-update! 💗",ephemeral=True)
        except ValueError: await interaction.response.send_message("❌ Harga harus angka! Contoh: 75000",ephemeral=True)
class EditPricelistView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None);self.kategori="via_username";self.nominal=500;self._build_nominal_select()
    def _build_nominal_select(self):
        for child in list(self.children):
            if getattr(child,'custom_id','')=="edit_pilih_nominal": self.remove_item(child)
        opts=[]
        for n in get_nominal_list(self.kategori):
            if self.kategori=="limited":
                item=LIMITED_ITEMS.get(n,{});label=item.get("nama",str(n))
            else: label=f"{n} Robux" + (" - PALING LARIS" if n==500 else "") + (" - SULTAN" if n==10000 else "")
            opts.append(discord.SelectOption(label=label,value=str(n)))
        select=discord.ui.Select(placeholder=f"2️⃣ Pilih Nominal / Item {self.kategori} - {len(opts)} pilihan!",custom_id="edit_pilih_nominal",options=opts,row=1);select.callback=self.pilih_nominal;self.add_item(select)
    @discord.ui.select(placeholder="1️⃣ Pilih Kategori Dulu",custom_id="edit_pilih_kategori",options=[discord.SelectOption(label="💎 Via Username (Visend)",value="via_username",emoji="💎"),discord.SelectOption(label="🔑 Via Login (Vilog)",value="via_login",emoji="🔑"),discord.SelectOption(label="👥 Via Komunitas",value="via_komunitas",emoji="👥"),discord.SelectOption(label="⭐ Roblox Plus",value="plus",emoji="⭐"),discord.SelectOption(label="💠 Limited Item",value="limited",emoji="💠")],row=0)
    async def pilih_kategori(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.kategori=select.values[0]
        # Reset nominal default per kategori
        if self.kategori=="limited": self.nominal="8bit_royal_crown"
        elif self.kategori=="plus": self.nominal=1000
        else: self.nominal=500
        self._build_nominal_select();await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"✅ Kategori: **{self.kategori}**\nDropdown bawah udah berubah jadi **{len(get_nominal_list(self.kategori))} pilihan**! Pilih, terus pencet ✏️ Edit!",ephemeral=True)
    async def pilih_nominal(self, interaction: discord.Interaction):
        val=interaction.data['values'][0]
        if self.kategori=="limited": self.nominal=val;harga=get_harga(val,"limited")
        else: self.nominal=int(val);harga=get_harga(self.nominal,self.kategori)
        await interaction.response.send_message(f"✅ Dipilih: **{self.nominal}** ({self.kategori})\nHarga sekarang: **{format_rp(harga)}**\nPencet ✏️ Edit Harga Ini!",ephemeral=True)
    @discord.ui.button(label="✏️ Edit Harga Ini",style=discord.ButtonStyle.primary,custom_id="edit_harga_ini",emoji="✏️",row=2)
    async def edit_ini(self, interaction: discord.Interaction, button: discord.ui.Button):
        harga_lama=get_harga(self.nominal,self.kategori);await interaction.response.send_modal(EditHargaModal(self.kategori,self.nominal,harga_lama))
    @discord.ui.button(label="👀 Lihat Harga",style=discord.ButtonStyle.secondary,custom_id="edit_lihat_harga",emoji="👀",row=2)
    async def lihat(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=build_pricelist_embed(self.kategori),ephemeral=True)
    @discord.ui.button(label="➕ Semua +5k",style=discord.ButtonStyle.success,custom_id="edit_plus_5k",emoji="➕",row=3)
    async def plus_5k(self, interaction: discord.Interaction, button: discord.ui.Button):
        d=load_pricelist(self.kategori)
        for k in list(d.keys()): d[k]=int(d[k])+5000
        save_pricelist(d,self.kategori);await interaction.response.send_message(f"✅ Semua harga {self.kategori} naik +5k!",ephemeral=True)
    @discord.ui.button(label="➖ Semua -5k",style=discord.ButtonStyle.secondary,custom_id="edit_min_5k",emoji="➖",row=3)
    async def min_5k(self, interaction: discord.Interaction, button: discord.ui.Button):
        d=load_pricelist(self.kategori)
        for k in list(d.keys()): d[k]=max(1000,int(d[k])-5000)
        save_pricelist(d,self.kategori);await interaction.response.send_message(f"✅ Semua harga {self.kategori} turun -5k!",ephemeral=True)
    @discord.ui.button(label="🎁 Diskon 10% Semua",style=discord.ButtonStyle.success,custom_id="edit_diskon_10",emoji="🎁",row=3)
    async def diskon_10(self, interaction: discord.Interaction, button: discord.ui.Button):
        d=load_pricelist(self.kategori)
        for k in list(d.keys()): d[k]=int(round(int(d[k])*0.90/500)*500)
        save_pricelist(d,self.kategori);await interaction.response.send_message(f"✅ Semua harga {self.kategori} diskon 10%!",ephemeral=True)
    @discord.ui.button(label="🔄 Reset ke Default",style=discord.ButtonStyle.danger,custom_id="edit_reset",emoji="🔄",row=3)
    async def reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        d=DEFAULT_PRICELIST_PER_KATEGORI.get(self.kategori,{}).copy();save_pricelist(d,self.kategori);await interaction.response.send_message(f"✅ {self.kategori} di-reset ke harga asli!",ephemeral=True)
class TambahProdukModal(discord.ui.Modal, title="➕ Tambah Produk Baru"):
    def __init__(self): super().__init__()
    kode=discord.ui.TextInput(label="Kode Produk (tanpa spasi)",placeholder="Contoh: akun_korblox",required=True,max_length=30)
    nama=discord.ui.TextInput(label="Nama Produk",placeholder="Contoh: Akun Korblox",required=True,max_length=50)
    harga=discord.ui.TextInput(label="Harga (angka aja)",placeholder="Contoh: 500000",required=True,max_length=10)
    stok=discord.ui.TextInput(label="Stok (angka)",placeholder="Contoh: 5 / 9999 unlimited",required=True,max_length=10)
    deskripsi=discord.ui.TextInput(label="Deskripsi Produk",placeholder="Contoh: Akun Korblox full email",style=discord.TextStyle.paragraph,required=False,max_length=200)
    async def on_submit(self, interaction: discord.Interaction):
        try:
            kode_bersih=self.kode.value.lower().replace(" ","_");harga_int=int(self.harga.value.replace(".","").replace(",",""));stok_int=int(self.stok.value.replace(".",""));d=load_produk();d[kode_bersih]={"nama":self.nama.value,"harga":harga_int,"stok":stok_int,"deskripsi":self.deskripsi.value or "-","emoji":"📦","kategori":"other"};save_produk(d);await interaction.response.send_message(f"✅ Produk **{self.nama.value}** ditambah! Harga {format_rp(harga_int)} Stok {stok_int}",ephemeral=True)
        except: await interaction.response.send_message("❌ Harga & Stok harus angka!",ephemeral=True)
class KuranginProdukModal(discord.ui.Modal, title="➖ Kurangin / Hapus Produk"):
    def __init__(self): super().__init__()
    kode=discord.ui.TextInput(label="Kode Produk",placeholder="Contoh: akun_sultan",required=True,max_length=30)
    jumlah=discord.ui.TextInput(label="Kurangin berapa? / HAPUS",placeholder="Contoh: 1 / HAPUS",required=True,max_length=10)
    async def on_submit(self, interaction: discord.Interaction):
        kode_bersih=self.kode.value.lower().strip();d=load_produk()
        if kode_bersih not in d: await interaction.response.send_message(f"❌ Kode `{kode_bersih}` gak ketemu! Cek /list-produk!",ephemeral=True);return
        if self.jumlah.value.strip().upper()=="HAPUS": del d[kode_bersih];save_produk(d);await interaction.response.send_message(f"✅ Produk dihapus!",ephemeral=True);return
        try: kurang=int(self.jumlah.value);d[kode_bersih]["stok"]=max(0,d[kode_bersih].get("stok",0)-kurang);save_produk(d);await interaction.response.send_message(f"✅ Stok dikurangin! Sisa {d[kode_bersih]['stok']}",ephemeral=True)
        except: await interaction.response.send_message("❌ Jumlah harus angka / HAPUS!",ephemeral=True)
class TambahStokModal(discord.ui.Modal, title="📦 Tambah Stok Produk"):
    def __init__(self): super().__init__()
    kode=discord.ui.TextInput(label="Kode Produk",placeholder="Contoh: akun_sultan",required=True,max_length=30)
    jumlah=discord.ui.TextInput(label="Tambah berapa?",placeholder="Contoh: 5",required=True,max_length=10)
    async def on_submit(self, interaction: discord.Interaction):
        kode_bersih=self.kode.value.lower().strip();d=load_produk()
        if kode_bersih not in d: await interaction.response.send_message("❌ Kode gak ketemu!",ephemeral=True);return
        try: d[kode_bersih]["stok"]=d[kode_bersih].get("stok",0)+int(self.jumlah.value);save_produk(d);await interaction.response.send_message(f"✅ Stok ditambah! Sekarang {d[kode_bersih]['stok']}",ephemeral=True)
        except: await interaction.response.send_message("❌ Jumlah harus angka!",ephemeral=True)
class PanelProdukView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="➕ Tambah Produk",style=discord.ButtonStyle.success,custom_id="produk_tambah",emoji="➕",row=0)
    async def tambah(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_admin_or_owner(interaction.user,interaction.guild): await interaction.response.send_message("❌ Hanya Admin!",ephemeral=True);return
        await interaction.response.send_modal(TambahProdukModal())
    @discord.ui.button(label="➖ Kurangin / Hapus Produk",style=discord.ButtonStyle.danger,custom_id="produk_kurang",emoji="➖",row=0)
    async def kurang(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_admin_or_owner(interaction.user,interaction.guild): await interaction.response.send_message("❌ Hanya Admin!",ephemeral=True);return
        await interaction.response.send_modal(KuranginProdukModal())
    @discord.ui.button(label="📦 Tambah Stok",style=discord.ButtonStyle.primary,custom_id="produk_tambah_stok",emoji="📦",row=1)
    async def tambah_stok(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_admin_or_owner(interaction.user,interaction.guild): await interaction.response.send_message("❌ Hanya Admin!",ephemeral=True);return
        await interaction.response.send_modal(TambahStokModal())
    @discord.ui.button(label="🛍️ Lihat Katalog",style=discord.ButtonStyle.secondary,custom_id="produk_lihat",emoji="🛍️",row=1)
    async def lihat(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=build_produk_embed(),ephemeral=True)
# ===== PRICELIST ALA 1ST MARKET - DROPDOWN PRIVAT! =====
class PricelistPublicView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.select(placeholder="Pilih Kategori Produk (Robux / Akun)  >",custom_id="mipi_pricelist_public",options=[discord.SelectOption(label="Robux Via Username (Visend)",value="via_username",emoji="💎",description="Lihat rincian harga Visend"),discord.SelectOption(label="Robux Via Login (Vilog)",value="via_login",emoji="🔑",description="Lihat rincian harga Vilog"),discord.SelectOption(label="Robux Via Komunitas",value="via_komunitas",emoji="👥",description="Lihat rincian harga Komunitas"),discord.SelectOption(label="Roblox Plus",value="plus",emoji="⭐",description="Lihat rincian harga Plus"),discord.SelectOption(label="Limited Item",value="limited",emoji="💠",description="Lihat rincian harga Limited"),discord.SelectOption(label="Rekber / Middleman",value="rekber",emoji="🛡️",description="Lihat fee Rekber")])
    async def pilih_kategori_public(self, interaction: discord.Interaction, select: discord.ui.Select):
        kat=select.values[0]
        if kat=="rekber": e=build_rekber_embed()
        else: e=build_pricelist_embed(kat)
        await interaction.response.send_message(embed=e,ephemeral=True)
def build_pricelist_public_embed():
    e=discord.Embed(title="💎 DAFTAR HARGA ROBUX • MIPI STORE",description="💗 **Silakan pilih kategori produk pada menu dropdown di bawah:**\n\n💎 **Robux Via Username (Visend)**\n🔑 **Robux Via Login (Vilog)**\n👥 **Robux Via Komunitas**\n⭐ **Roblox Plus**\n💠 **Limited Item**\n🛡️ **Rekber / Middleman**\n\n• Harga sewaktu-waktu dapat berubah mengikuti rate pasar.\n• Rincian harga akan muncul secara privat (mode dismiss message).\n\n💗 **Mipi Store — Rafi Store**",color=0xff69b4);e.set_image(url=WELCOME_URL);e.set_footer(text="MIPI STORE • Pilih kategori di bawah ya!");return e
PANEL_FILE="panel.json"
def load_panel():
    try:
        with open(PANEL_FILE,"r") as f: return json.load(f)
    except: return {}
def save_panel(d):
    try:
        with open(PANEL_FILE,"w") as f: json.dump(d,f,indent=2)
    except: pass
async def update_all_panels(guild):
    try:
        panels=load_panel()
        for key,info in list(panels.items()):
            try:
                ch=guild.get_channel(int(info["channel_id"]))
                if not ch: continue
                msg=await ch.fetch_message(int(info["message_id"]))
                if key=="ticket": await msg.edit(embed=build_ticket_panel_baru_embed(),view=TicketTypeView())
                elif key=="pricelist": await msg.edit(embed=build_pricelist_public_embed(),view=PricelistPublicView())
                elif key=="produk": await msg.edit(embed=build_produk_embed(),view=PanelProdukView())
            except: pass
    except: pass
async def refresh_ticket_panel(guild):
    try: await update_all_panels(guild)
    except: pass
@bot.event
async def on_message(message):
    try:
        if message.author.bot: return
        if message.guild and "market" in message.channel.name.lower():
            if message.author.id!=message.guild.owner_id and not message.author.guild_permissions.administrator:
                if is_banned_selling(message.content) or is_scam_link(message.content):
                    try: await message.delete()
                    except: pass
                    await message.channel.send(f"{message.author.mention} DILARANG JUALAN / LINK SCAM DI SINI!",delete_after=10);return
        if message.channel.id in ticket_data: ticket_data[message.channel.id]["last_activity"]=time.time()
        await bot.process_commands(message)
    except: pass
@bot.event
async def on_ready():
    print(f"Login {bot.user} - MIPI STORE V5 FINAL!")
    bot.add_view(OrderView());bot.add_view(TicketTypeView());bot.add_view(CloseView());bot.add_view(StatusView());bot.add_view(RatingView(0));bot.add_view(SaldoView());bot.add_view(GiveawayView("dummy"));bot.add_view(EditPricelistView());bot.add_view(PanelProdukView());bot.add_view(PricelistPublicView())
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
        synced=await bot.tree.sync();print(f"Synced {len(synced)} commands!")
    except Exception as e: print(f"Sync error: {e}")
@bot.tree.command(name="ticket",description="Tampilkan panel order MIPI STORE")
async def ticket(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=False)
    ch_target=interaction.guild.get_channel(OPEN_TICKET_CHANNEL_ID) or interaction.channel;panels=load_panel()
    if "ticket" in panels:
        try:
            ch=interaction.guild.get_channel(int(panels["ticket"]["channel_id"]));msg=await ch.fetch_message(int(panels["ticket"]["message_id"]));await msg.edit(embed=build_ticket_panel_baru_embed(),view=TicketTypeView());await safe_followup(interaction,content=f"✅ Panel di-update! Cek {ch.mention}",ephemeral=True);return
        except: pass
    msg=await ch_target.send(embed=build_ticket_panel_baru_embed(),view=TicketTypeView());panels["ticket"]={"channel_id":str(msg.channel.id),"message_id":str(msg.id)};save_panel(panels);await safe_followup(interaction,content=f"✅ Panel dikirim ke {ch_target.mention}!",ephemeral=True)
@bot.tree.command(name="pricelist",description="Lihat pricelist ala 1ST MARKET - dropdown!")
async def pricelist_baru(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    e=build_pricelist_public_embed();msg=await interaction.channel.send(embed=e,view=PricelistPublicView());panels=load_panel();panels["pricelist"]={"channel_id":str(msg.channel.id),"message_id":str(msg.id)};save_panel(panels);await safe_followup(interaction,content="✅ Pricelist dropdown udah dikirim! Kayak 1ST MARKET!",ephemeral=True)
@bot.tree.command(name="open",description="Buka toko")
async def open_cmd(interaction:discord.Interaction):
    global STORE_STATUS;await safe_defer(interaction,ephemeral=True)
    if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Cuma admin!",ephemeral=True);return
    STORE_STATUS="open";await safe_followup(interaction,content="✅ Mipi Store **DIBUKA**!")
@bot.tree.command(name="break",description="Toko break sebentar")
async def break_cmd(interaction:discord.Interaction):
    global STORE_STATUS;await safe_defer(interaction,ephemeral=True)
    if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Cuma admin!",ephemeral=True);return
    STORE_STATUS="break";await safe_followup(interaction,content="☕ Mipi Store **BREAK** 15-30 menit!")
@bot.tree.command(name="close",description="Tutup toko")
async def close_cmd(interaction:discord.Interaction):
    global STORE_STATUS;await safe_defer(interaction,ephemeral=True)
    if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Cuma admin!",ephemeral=True);return
    STORE_STATUS="closed";await safe_followup(interaction,content="💤 Mipi Store **TUTUP**!")
@bot.tree.command(name="panel-edit-pricelist",description="Buka panel edit pricelist - TINGGAL PENCET! (Admin)")
async def panel_edit_pricelist(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="❌ Hanya Admin!",ephemeral=True);return
    e=discord.Embed(title="💎 EDIT PRICELIST - TINGGAL PENCET!",description="1️⃣ Pilih Kategori\n2️⃣ Pilih Nominal / Item\n3️⃣ Pencet ✏️ Edit Harga Ini -> ketik harga baru -> BERES!\n\n➕ +5k / ➖ -5k / 🎁 Diskon 10% / 🔄 Reset",color=0xff69b4);await interaction.channel.send(embed=e,view=EditPricelistView());await safe_followup(interaction,content="✅ Panel Edit udah dikirim!",ephemeral=True)
@bot.tree.command(name="panel-produk",description="Buka panel produk (Admin)")
async def panel_produk(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="❌ Hanya Admin!",ephemeral=True);return
    e=discord.Embed(title="🛍️ KELOLA PRODUK",description="➕ Tambah / ➖ Kurangin / 📦 Tambah Stok / 🛍️ Lihat Katalog",color=0xff69b4);await interaction.channel.send(embed=e,view=PanelProdukView());await safe_followup(interaction,content="✅ Panel Produk dikirim!",ephemeral=True)
@bot.tree.command(name="list-produk",description="Lihat semua produk")
async def list_produk(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True);await safe_followup(interaction,embed=build_produk_embed(),ephemeral=True)
@bot.tree.command(name="tutup-kategori",description="Tutup 1 tombol (Admin)")
async def tutup_kategori(interaction:discord.Interaction,kategori:str):
    await safe_defer(interaction,ephemeral=True)
    if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin!",ephemeral=True);return
    kat=kategori_alias(kategori);set_stock(kat,False);await refresh_ticket_panel(interaction.guild);await safe_followup(interaction,content=f"🔴 **{kat.upper()} DITUTUP!**",ephemeral=True)
@bot.tree.command(name="buka-kategori",description="Buka lagi 1 tombol (Admin)")
async def buka_kategori(interaction:discord.Interaction,kategori:str):
    await safe_defer(interaction,ephemeral=True)
    if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin!",ephemeral=True);return
    kat=kategori_alias(kategori);set_stock(kat,True);await refresh_ticket_panel(interaction.guild);await send_notify_restock(interaction.guild,kat);await safe_followup(interaction,content=f"🟢 **{kat.upper()} DIBUKA LAGI!**",ephemeral=True)
@bot.tree.command(name="cek-stock",description="Cek stock")
async def cek_stock(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True);s=load_stock();txt="📦 **STATUS STOCK**\n\n"
    for k in ["via_username","via_login","via_komunitas","plus","limited","rekber","beli_akun","other"]: txt+=f"{'🟢 BUKA' if s.get(k,True) else '🔴 TUTUP'} — {k}\n"
    await safe_followup(interaction,content=txt,ephemeral=True)
@bot.tree.command(name="notify",description="DM otomatis kalo restock!")
async def notify_cmd(interaction:discord.Interaction,kategori:str):
    await safe_defer(interaction,ephemeral=True);kat=kategori_alias(kategori);add_notify(interaction.user.id,kat);await safe_followup(interaction,content=f"🔔 Oke! Kalo **{kat}** restock, kamu aku DM! 💗",ephemeral=True)
@bot.tree.command(name="saldo",description="Cek saldo kamu")
async def saldo_cmd(interaction:discord.Interaction,user:discord.User=None):
    await safe_defer(interaction,ephemeral=True);target=user or interaction.user;tr,tro,tt=get_total_belanja(target.id);lvl=get_level(tr);nxt,sisa=get_next_level(tr);poin=get_poin(target.id);embed=discord.Embed(color=0xff1493);embed.description=f"Saldo {target.mention}\n\n🏆 Level: {lvl}\n➡️ Next: {nxt} (kurang {format_rp(sisa)})\n\nTotal Belanja: {format_rp(tr)}\nTotal Robux: {tro} R$\nTransaksi: {tt}x\n🎁 Poin: {poin}";await safe_followup(interaction,embed=embed,ephemeral=True)
@bot.tree.command(name="top-sultan",description="Lihat Top Sultan")
async def top_sultan_cmd(interaction:discord.Interaction,jenis:str="semua"):
    await safe_defer(interaction,ephemeral=True);e=build_top_sultan_embed_bulanan() if "bulan" in jenis.lower() else build_top_sultan_embed_semua();await safe_followup(interaction,embed=e,ephemeral=True)
@bot.tree.command(name="statistik",description="Lihat statistik omset")
async def statistik_cmd(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True);s=get_statistik();e=discord.Embed(title="📊 STATISTIK MIPI STORE",description=f"📅 Hari Ini: {format_rp(s['hari_rp'])}\n📅 Bulan Ini: {format_rp(s['bulan_rp'])} ({s['bulan_tr']} transaksi)\n👑 All Time: {format_rp(s['all_rp'])} ({s['all_tr']} transaksi)",color=0xff69b4);await safe_followup(interaction,embed=e,ephemeral=True)
@bot.tree.command(name="referral",description="Lihat kode referral kamu")
async def referral_cmd(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True);data=load_referral();uid=str(interaction.user.id);code=get_referral_code(interaction.user.id)
    if uid not in data: data[uid]={"code":code,"total_komisi":0,"total_referral":0,"history":[]};save_referral(data)
    info=data[uid];await safe_followup(interaction,content=f"💸 **REFERRAL KAMU**\n\n🔑 Kode: **{info['code']}**\n💰 Komisi: {format_rp(info['total_komisi'])}\n👥 Temen: {info['total_referral']} orang",ephemeral=True)
@bot.tree.command(name="daily",description="Claim daily reward!")
async def daily_cmd(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True);bonus,total,err=claim_daily(interaction.user.id)
    if err: await safe_followup(interaction,content=f"❌ {err}\nPoin: {total}",ephemeral=True)
    else: await safe_followup(interaction,content=f"🎁 **DAILY BERHASIL!** +{bonus} poin! Total: {total} poin",ephemeral=True)
@bot.tree.command(name="tuker-poin",description="Tuker poin jadi Robux!")
async def tuker_poin(interaction:discord.Interaction,jumlah:int):
    await safe_defer(interaction,ephemeral=True);poin=get_poin(interaction.user.id)
    if poin<jumlah: await safe_followup(interaction,content=f"❌ Poin cuma {poin}!",ephemeral=True);return
    if jumlah<100: await safe_followup(interaction,content="❌ Minimal 100 poin!",ephemeral=True);return
    if not use_poin(interaction.user.id,jumlah): await safe_followup(interaction,content="❌ Gagal!",ephemeral=True);return
    oid=add_to_pending(interaction.user.id,interaction.user.name,f"TUKER POIN - {jumlah} Robux",999999,f"tuker-poin-{interaction.user.name}",kategori="via_username",robux_jumlah=jumlah,harga_akhir=0);await safe_followup(interaction,content=f"✅ Tuker berhasil! +{jumlah} Robux PENDING! ID: {oid}",ephemeral=True)
@bot.tree.command(name="buat-voucher",description="Bikin voucher (Admin)")
async def buat_voucher(interaction:discord.Interaction,kode:str,diskon:int,tipe:str="persen",max_pakai:int=10):
    await safe_defer(interaction,ephemeral=True)
    if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin!",ephemeral=True);return
    data=load_voucher();data[kode.upper()]={"diskon":int(diskon),"tipe":tipe.lower(),"max":int(max_pakai),"dipakai":0,"used_by":[]};save_voucher(data);await safe_followup(interaction,content=f"✅ Voucher **{kode.upper()}** dibuat!",ephemeral=True)
@bot.tree.command(name="redeem-voucher",description="Redeem voucher!")
async def redeem_voucher_cmd(interaction:discord.Interaction,kode:str):
    await safe_defer(interaction,ephemeral=True);v,err=redeem_voucher(interaction.user.id,kode)
    if err: await safe_followup(interaction,content=f"❌ {err}",ephemeral=True)
    else: await safe_followup(interaction,content=f"✅ Voucher {kode.upper()} diredeem! Diskon {v['diskon']} {v['tipe']}! SS & kasih ke admin!",ephemeral=True)
@bot.tree.command(name="tebak-harga",description="Main tebak harga!")
async def tebak_harga(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True);nominal,harga,pilihan=start_tebak_harga();game_data[interaction.user.id]={"nominal":nominal,"harga":harga,"pilihan":pilihan};txt=f"🎮 **TEBAK HARGA**\n\nBerapa harga **{nominal} Robux Via Username**?\n\n"
    for i,p in enumerate(pilihan,1): txt+=f"{i}. {format_rp(p)}\n"
    txt+="\nJawab pake `/jawab-tebak <nomor>`!";await safe_followup(interaction,content=txt,ephemeral=True)
@bot.tree.command(name="jawab-tebak",description="Jawab tebak harga!")
async def jawab_tebak(interaction:discord.Interaction,nomor:int):
    await safe_defer(interaction,ephemeral=True)
    if interaction.user.id not in game_data: await safe_followup(interaction,content="Ketik /tebak-harga dulu!",ephemeral=True);return
    g=game_data.pop(interaction.user.id)
    if g["pilihan"][nomor-1]==g["harga"]:
        kode=f"GAME-{interaction.user.id%10000:04d}";data=load_voucher();data[kode]={"diskon":5,"tipe":"persen","max":1,"dipakai":0,"used_by":[]};save_voucher(data);await safe_followup(interaction,content=f"🎉 BENAR! Kamu dapet voucher **{kode}** (5%)!",ephemeral=True)
    else: await safe_followup(interaction,content=f"❌ Salah! Harganya {format_rp(g['harga'])}!",ephemeral=True)
@bot.tree.command(name="tambah-promo",description="Tambah promo (Admin)")
async def tambah_promo(interaction:discord.Interaction,kode:str,diskon:int,tipe:str="persen",max_pakai:int=999):
    await safe_defer(interaction,ephemeral=True)
    if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin!",ephemeral=True);return
    data=load_promo();data[kode.upper()]={"diskon":int(diskon),"tipe":tipe.lower(),"max":int(max_pakai),"dipakai":0};save_promo(data);await safe_followup(interaction,content=f"✅ Promo **{kode.upper()}** ditambah!",ephemeral=True)
@bot.tree.command(name="lihat-promo",description="Lihat semua promo")
async def lihat_promo(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True);data=load_promo()
    if not data: await safe_followup(interaction,content="Belum ada promo!",ephemeral=True);return
    txt="🎁 **DAFTAR PROMO**\n\n"
    for k,v in data.items(): txt+=f"**{k}** — {v.get('diskon')} {v.get('tipe')} — {v.get('dipakai',0)}/{v.get('max',999)}\n"
    await safe_followup(interaction,content=txt,ephemeral=True)
@bot.tree.command(name="giveaway",description="Bikin giveaway (Admin)")
async def giveaway_cmd(interaction:discord.Interaction,hadiah:str,pemenang:int=1,menit:int=60):
    await safe_defer(interaction,ephemeral=True)
    if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin!",ephemeral=True);return
    gid=f"GW-{int(time.time())}";giveaway_data[gid]={"hadiah":hadiah,"host_mention":interaction.user.mention,"peserta":[],"pemenang":int(pemenang),"ended":False};e=discord.Embed(title="🎉 GIVEAWAY MIPI STORE!",description=f"Hadiah: {hadiah}\nHost: {interaction.user.mention}\nPeserta: 0 orang",color=0xff69b4);msg=await interaction.channel.send(embed=e,view=GiveawayView(gid));await safe_followup(interaction,content=f"✅ Giveaway dibuat! Berakhir {menit} menit lagi!",ephemeral=True);await asyncio.sleep(int(menit)*60);await end_giveaway(interaction.guild,msg.channel.id,msg.id,gid)
@bot.tree.command(name="pending",description="Lihat pending (Admin)")
async def pending_cmd(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True)
    if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin!",ephemeral=True);return
    data=load_pending()
    if not data: await safe_followup(interaction,content="✅ Gak ada pending!",ephemeral=True);return
    txt="⏳ **PENDING SALDO**\n\n"
    for oid,d in data.items(): txt+=f"**{oid}** — <@{d['user_id']}> — {d['paket']} — {d['robux']} R$ — {format_rp(d['harga'])}\n"
    await safe_followup(interaction,content=txt,ephemeral=True)
@bot.tree.command(name="add-saldo",description="Tambah saldo manual (Admin)")
async def add_saldo(interaction:discord.Interaction,user:discord.User,robux:int,kategori:str="via_username"):
    await safe_defer(interaction,ephemeral=True)
    if not is_admin_or_owner(interaction.user,interaction.guild): await safe_followup(interaction,content="Hanya Admin!",ephemeral=True);return
    kat=kategori_alias(kategori);add_to_leaderboard(user.id,user.name,f"{robux} Robux",kategori=kat);await safe_followup(interaction,content=f"✅ {user.mention} +{robux} R$!",ephemeral=True)
@bot.tree.command(name="lihat-harga",description="Lihat harga pricelist")
async def lihat_harga(interaction:discord.Interaction,kategori:str="via_username"):
    await safe_defer(interaction,ephemeral=True);kat=kategori_alias(kategori);await safe_followup(interaction,embed=build_pricelist_embed(kat),ephemeral=True)
@bot.tree.command(name="pricelist-rekber",description="Pricelist Rekber")
async def pricelist_rekber(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True);await interaction.channel.send(embed=build_rekber_embed(),view=RekberView(guild_id=interaction.guild.id));await safe_followup(interaction,content="✅ Pricelist Rekber dikirim!",ephemeral=True)
@bot.tree.command(name="help-mipi",description="Lihat semua command")
async def help_mipi(interaction:discord.Interaction):
    await safe_defer(interaction,ephemeral=True);txt="💗 **HELP - MIPI STORE V5 FINAL**\n\n**ORDER:** `/ticket` `/pricelist`\n**EDIT:** `/panel-edit-pricelist` `/panel-produk` `/list-produk`\n**SALDO:** `/saldo` `/top-sultan` `/pending`\n**STOCK:** `/tutup-kategori` `/buka-kategori` `/cek-stock` `/notify`\n**V5:** `/referral` `/daily` `/tuker-poin` `/buat-voucher` `/redeem-voucher` `/tebak-harga`\n**TOKO:** `/open` `/break` `/close`\n**ADMIN:** `/tambah-promo` `/lihat-promo` `/giveaway`";await safe_followup(interaction,content=txt,ephemeral=True)
bot.run(os.getenv("DISCORD_TOKEN"))
