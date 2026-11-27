import discord
from discord.ext import commands, tasks
from discord import app_commands
import os,time,html,re,asyncio,json,random,traceback
from datetime import datetime,timedelta
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
TOP_BULANAN_IMAGE="https://raw.githubusercontent.com/mipistore/mipi-store/main/97b3c2a7-b1e8-66b1-50e5-563dc75098ea.jpeg"
ticket_data={};ticket_counter=0;user_ratings={};user_last_ticket={};STORE_STATUS="open";OPEN_CLOSE_CHANNEL_ID=1569135504262299689;OPEN_TICKET_CHANNEL_ID=1569711323653083279
REFERRAL_RATE=0.05;DAILY_POIN=10;LEVELS=[("🌱 Newbie",0),("💎 Regular",100000),("⭐ VIP",500000),("👑 Sultan",1000000),("🔥 LEGEND",5000000)]
async def safe_defer(i,ephemeral=False):
    try:
        if not i.response.is_done(): await i.response.defer(ephemeral=ephemeral)
        return True
    except: return False
async def safe_followup(i,content=None,embed=None,embeds=None,view=None,ephemeral=False):
    try:
        if i.response.is_done(): return await i.followup.send(content=content,embed=embed,embeds=embeds,view=view,ephemeral=ephemeral)
        else: return await i.response.send_message(content=content,embed=embed,embeds=embeds,view=view,ephemeral=ephemeral)
    except:
        try: return await i.channel.send(content=content,embed=embed,embeds=embeds,view=view)
        except: return None
@bot.tree.error
async def on_app_command_error(i,error):
    print(f"ERR {i.command.name if i.command else '?'}: {error}");traceback.print_exc()
    try:
        m=f"❌ Error: {str(error)[:400]}"
        if i.response.is_done(): await i.followup.send(m,ephemeral=True)
        else: await i.response.send_message(m,ephemeral=True)
    except: pass
def _load(fn,default):
    try:
        with open(fn,"r") as f: return json.load(f)
    except: return default
def _save(fn,d):
    try:
        with open(fn,"w") as f: json.dump(d,f,indent=2)
    except: pass
def load_stock(): return _load("stock.json",{})
def save_stock(d): _save("stock.json",d)
def is_open(k): return load_stock().get(str(k),True)
def set_stock(k,b):
    d=load_stock();d[str(k)]=bool(b);save_stock(d);return d
def kategori_alias(k):
    k=str(k).lower().replace(" ","_").replace("-","_")
    m={"visend":"via_username","via_send":"via_username","via_username":"via_username","vilog":"via_login","via_login":"via_login","vlog":"via_login","komunitas":"via_komunitas","via_komunitas":"via_komunitas","plus":"plus","roblox_plus":"plus","roblox_pluss":"plus","pluss":"plus","limited":"limited","rekber":"rekber","mm":"rekber","middleman":"rekber","beli_akun":"beli_akun","other":"other","nanya":"other"}
    return m.get(k,k)
LIMITED_ITEMS={"8bit_royal_crown":{"nama":"8-BIT ROYAL CROWN","harga":2300000,"emoji":"<:BRC:1510531815427805194>"},"8bit_hp_bar":{"nama":"8-BIT HP BAR","harga":850000,"emoji":"<:HPBAR:1510531549274312824>"},"8bit_tabby_cat":{"nama":"8-BIT TABBY CAT","harga":750000,"emoji":"<:TABBY:1510531527006748762>"},"8bit_extra":{"nama":"8-BIT EXTRA","harga":700000,"emoji":"<:EXTRA:1510531838848925867>"},"8bit_coin":{"nama":"8-BIT COIN","harga":700000,"emoji":"<:COIN:1510531570425925734>"}}
DEFAULT_PRICELIST_PER_KATEGORI={"via_username":{50:9500,100:15500,200:31000,300:46500,350:51000,400:62000,500:73000,600:88000,700:108000,800:118000,900:133000,1000:145000,1200:176000,1500:218000,2000:290000,2500:363000,3000:435000,4000:580000,5000:725000,6000:870000,7000:1015000,8000:1160000,9000:1305000,10000:1450000},"via_login":{500:80000,600:96000,700:112000,800:128000,900:144000,1000:155000,1200:186000,1500:232500,2000:310000,2500:387500,3000:465000,4000:620000,5000:775000,6000:930000,7000:1085000,8000:1240000,9000:1395000,10000:1550000},"via_komunitas":{500:70000,600:81000,700:94500,800:108000,900:121500,1000:135000,1200:162000,1500:202500,2000:270000,2500:337500,3000:405000,3500:472500,4000:540000,4500:607500,5000:675000,5500:742500,6000:810000,6500:877500,7000:945000,7500:1012500,8000:1080000,8500:1147500,9000:1215000,9500:1282500,10000:1350000},"plus":{450:110000,500:225000,1000:300000,2000:455000,2200:455000},"limited":{k:v["harga"] for k,v in LIMITED_ITEMS.items()}}
DEFAULT_PRICELIST=DEFAULT_PRICELIST_PER_KATEGORI["via_username"].copy()
PRICELIST_FILE="pricelist.json"
def _load_all_pricelist_raw():
    try:
        with open(PRICELIST_FILE,"r") as f:
            d=json.load(f)
            return d if isinstance(d,dict) else {}
    except: return {}
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
        if kat not in raw: raw[kat]={str(k):v for k,v in DEFAULT_PRICELIST_PER_KATEGORI[kat].items()}
    raw[kategori]={str(k):int(v) for k,v in data.items()}
    with open(PRICELIST_FILE,"w") as f: json.dump(raw,f,indent=2)
    return True
def get_harga(robux,kategori="via_username"):
    kategori=kategori_alias(kategori)
    if kategori=="limited":
        d=load_pricelist("limited");return int(d.get(str(robux),LIMITED_ITEMS.get(str(robux),{}).get("harga",0)))
    data=load_pricelist(kategori)
    try: robux=int(robux)
    except: return 0
    return int(data.get(robux,0))
def format_rp(n):
    try: return f"Rp {int(n):,}".replace(",",".")
    except: return f"Rp {n}"
def get_level(t):
    lvl="🌱 Newbie"
    for n,m in LEVELS:
        if t>=m: lvl=n
    return lvl
def get_next_level(t):
    for n,m in LEVELS:
        if t<m: return n,m-t
    return "🔥 MAX LEVEL",0
def get_nominal_list(k):
    if k=="via_username": return [50,100,200,300,350,400,500,600,700,800,900,1000,1200,1500,2000,2500,3000,4000,5000,6000,7000,8000,9000,10000]
    if k=="via_login": return [500,600,700,800,900,1000,1200,1500,2000,2500,3000,4000,5000,6000,7000,8000,9000,10000]
    if k=="via_komunitas": return [500,600,700,800,900,1000,1200,1500,2000,2500,3000,3500,4000,4500,5000,5500,6000,6500,7000,7500,8000,8500,9000,9500,10000]
    if k=="plus": return [450,500,1000,2000,2200]
    if k=="limited": return list(LIMITED_ITEMS.keys())
    return [100,500,1000]
def build_pricelist_text(kategori="via_username"):
    kategori=kategori_alias(kategori)
    if not is_open(kategori): return f"🔴 **{kategori.upper()} LAGI HABIS!**\nCoba kategori lain ya 💗"
    data=load_pricelist(kategori)
    def h(n): return format_rp(data.get(int(n),get_harga(n,kategori)))
    if kategori=="via_username":
        txt="✨ Robux langsung ke akun kamu, tanpa login!\n💎 Aman • Cepat • Garansi 100%\n\n━━ 🌸 ECERAN ━━\n"
        for n in [50,100,200,300,350,400]: txt+=f"💠 {n} Robux — {h(n)}\n"
        txt+="\n━━ 💎 HEMAT ━━\n"
        for n in [500,600,700,800,900,1000]: txt+=f"✨ {n} Robux — {h(n)}\n"
        txt+="\n━━ 👑 SULTAN ━━\n"
        for n in [1200,1500,2000,2500,3000,4000,5000,6000,7000,8000,9000,10000]: txt+=f"👑 {n} Robux — {h(n)}\n"
        txt+=f"\n🛍️ Order di <#{OPEN_TICKET_CHANNEL_ID}>\n💳 QRIS ONLY • ⚡ 1-15 Menit\n💗 Mipi Store"
        return txt
    if kategori=="via_login":
        txt="🔑 **VIA LOGIN**\n\n"
        for n in get_nominal_list("via_login"): txt+=f"✨ {n} Robux — {h(n)}\n"
        txt+=f"\n🛍️ Order di <#{OPEN_TICKET_CHANNEL_ID}>\n💗 Mipi Store";return txt
    if kategori=="via_komunitas":
        txt="👥 **VIA KOMUNITAS**\n\n"
        for n in get_nominal_list("via_komunitas"): txt+=f"✨ {n} Robux — {h(n)}\n"
        txt+=f"\n🛍️ Order di <#{OPEN_TICKET_CHANNEL_ID}>\n💗 Mipi Store";return txt
    if kategori=="plus":
        return f"⭐ **ROBLOX PLUS**\n🌸 Plus 450 — {format_rp(data.get(450,110000))}\n✨ Plus 500 — {format_rp(data.get(500,225000))}\n✨ Plus 1000 — {format_rp(data.get(1000,300000))}\n👑 Plus 2000/2200 — {format_rp(data.get(2200,455000))}\n\n🛍️ Order di <#{OPEN_TICKET_CHANNEL_ID}>\n💗 Mipi Store"
    if kategori=="limited":
        txt="<a:announce:1506170564677472306> UPDATE HARGA LIMITED\n\n"
        for kode,item in LIMITED_ITEMS.items():
            harga=data.get(kode,item["harga"]);txt+=f"{item['emoji']} {item['nama']} : RP. {int(harga):,}\n".replace(",",".")
        txt+=f"\n# ALL ITEM CLEAN BERGARANSI **READY**\n🛍️ Order di <#{OPEN_TICKET_CHANNEL_ID}>\n💗 Mipi Store";return txt
    return "Error, coba /lihat-harga lagi!"
CATEGORY_PRICELIST={"via_username":{"title":"💎 PRICELIST VIA USERNAME — MIPI STORE","image":VIA_USERNAME_URL,"desc":"✨ Fast • Aman • Instan"},"via_login":{"title":"🔑 PRICELIST VLOG / VIA LOGIN","image":VIA_LOGIN_URL,"desc":"Via Login"},"via_komunitas":{"title":"👥 PRICELIST VIA KOMUNITAS","image":VIA_KOMUNITAS_URL,"desc":"Via Komunitas"},"plus":{"title":"⭐ PRICELIST ROBLOX PLUS","image":PLUS_URL,"desc":"Plus Monthly"},"limited":{"title":"💠 PRICELIST LIMITED ITEM","image":LIMITED_URL,"desc":"Beli / Jual Limited"}}
def build_pricelist_embed(kategori="via_username"):
    info=CATEGORY_PRICELIST.get(kategori,CATEGORY_PRICELIST["via_username"]);e=discord.Embed(title=info["title"],description=info["desc"]+"\n\n"+build_pricelist_text(kategori),color=0xff69b4);e.set_image(url=info["image"]);e.set_footer(text="Mipi Store | Harga bisa berubah");return e
def build_rekber_embed():
    e=discord.Embed(title="🛡️ Middleman / Rekber - MIPI STORE",description=f"✨ Transaksi aman!\n\n💰 Fee Middleman\n🌸 Rp 1.000 — Rp 99.000 → Fee **Rp 1.500**\n✨ Rp 100.000 — Rp 199.000 → Fee **Rp 2.500**\n✨ Rp 200.000 — Rp 499.000 → Fee **Rp 4.000**\n👑 Rp 500.000 — Rp 1.000.000 → Fee **Rp 7.000**\n👑 Di atas Rp 1.000.000 → Fee **Rp 10.000**\n\n🛍️ Order di <#{OPEN_TICKET_CHANNEL_ID}>\n💗 Mipi Store",color=0xff69b4);e.set_image(url=WELCOME_URL);return e
class RekberView(discord.ui.View):
    def __init__(self,guild_id=None):
        super().__init__(timeout=None);url=f"https://discord.com/channels/{guild_id}/{OPEN_TICKET_CHANNEL_ID}" if guild_id else f"https://discord.com/channels/@me/{OPEN_TICKET_CHANNEL_ID}";self.add_item(discord.ui.Button(label="🎫 Buat Ticket Middleman",style=discord.ButtonStyle.link,url=url,emoji="🎫"));self.add_item(discord.ui.Button(label="💬 Open Ticket",style=discord.ButtonStyle.link,url=url,emoji="💬"))
def jenis_to_kategori(jenis):
    j=str(jenis).upper()
    if "VIA LOGIN" in j: return "via_login"
    if "VIA KOMUNITAS" in j: return "via_komunitas"
    if "PLUS" in j: return "plus"
    if "LIMITED" in j or "OFFSALE" in j: return "limited"
    return "via_username"
def load_produk():
    try:
        with open("produk.json","r") as f:
            d=json.load(f)
            return d if isinstance(d,dict) else {}
    except: return {"robux_visend":{"nama":"💎 Robux Via Username","harga":80000,"stok":9999,"deskripsi":"500 Robux","emoji":"💎","kategori":"via_username"}}
def save_produk(d): _save("produk.json",d)
def build_produk_embed():
    d=load_produk();desc="💗 **KATALOG MIPI STORE**\n\n━━━\n"
    for kode,p in d.items():
        stok_txt="🟢 READY (Unlimited)" if p.get("stok",0)>1000 else f"{'🟢 READY' if p.get('stok',0)>0 else '🔴 HABIS'} ({p.get('stok',0)})"
        desc+=f"{p.get('emoji','📦')} **{p.get('nama','Produk')}**\n└ `{kode}` | {format_rp(p.get('harga',0))} | {stok_txt}\n└ {p.get('deskripsi','')}\n\n"
    desc+="━━━\n🛍️ Order di #open-ticket\n💗 Mipi Store";e=discord.Embed(title="🛍️ KATALOG - MIPI STORE",description=desc,color=0xff69b4);e.set_image(url=WELCOME_URL);return e
LEADERBOARD_SULTAN_FILE="leaderboard_sultan.json";LEADERBOARD_BULANAN_FILE="leaderboard_bulanan.json"
def load_leaderboard_sultan(): return _load(LEADERBOARD_SULTAN_FILE,{})
def save_leaderboard_sultan(d): _save(LEADERBOARD_SULTAN_FILE,d)
def load_leaderboard_bulanan(): return _load(LEADERBOARD_BULANAN_FILE,{})
def save_leaderboard_bulanan(d): _save(LEADERBOARD_BULANAN_FILE,d)
def load_leaderboard(): return load_leaderboard_sultan()
def save_leaderboard(d): save_leaderboard_sultan(d)
def _hitung_saldo(paket_text,kategori,robux_jumlah,harga_akhir):
    if robux_jumlah is not None: return int(robux_jumlah),int(harga_akhir) if harga_akhir else get_harga(int(robux_jumlah),kategori)
    m=re.search(r'(\d+)',str(paket_text).replace('.','').replace(',',''))
    if not m: return 0,0
    j=int(m.group(1));return j,get_harga(j,kategori)
def add_to_sultan_only(user_id,username,paket_text,kategori="via_username",robux_jumlah=None,harga_akhir=None):
    try:
        jumlah,harga=_hitung_saldo(paket_text,kategori,robux_jumlah,harga_akhir)
        if jumlah<=0 and harga<=0: return
        uid=str(user_id);d=load_leaderboard_sultan()
        if uid not in d: d[uid]={"username":username,"total":0,"transaksi":0,"total_rp":0}
        d[uid]["username"]=username;d[uid]["total"]+=jumlah;d[uid]["transaksi"]+=1;d[uid]["total_rp"]+=harga;save_leaderboard_sultan(d)
    except Exception as e: print(f"sultan err {e}")
def add_to_bulanan_only(user_id,username,paket_text,kategori="via_username",robux_jumlah=None,harga_akhir=None):
    try:
        jumlah,harga=_hitung_saldo(paket_text,kategori,robux_jumlah,harga_akhir)
        if jumlah<=0 and harga<=0: return
        uid=str(user_id);bulan=datetime.now().strftime("%Y-%m");d=load_leaderboard_bulanan()
        if bulan not in d: d[bulan]={}
        if uid not in d[bulan]: d[bulan][uid]={"username":username,"total":0,"transaksi":0,"total_rp":0}
        d[bulan][uid]["username"]=username;d[bulan][uid]["total"]+=jumlah;d[bulan][uid]["transaksi"]+=1;d[bulan][uid]["total_rp"]+=harga;save_leaderboard_bulanan(d)
        ds=load_leaderboard_sultan()
        if uid not in ds: ds[uid]={"username":username,"total":0,"transaksi":0,"total_rp":0}
        ds[uid]["username"]=username;ds[uid]["total"]+=jumlah;ds[uid]["transaksi"]+=1;ds[uid]["total_rp"]+=harga;save_leaderboard_sultan(ds)
    except Exception as e: print(f"bulanan err {e}")
def add_to_leaderboard(user_id,username,paket_text,kategori="via_username",robux_jumlah=None,harga_akhir=None):
    add_to_bulanan_only(user_id,username,paket_text,kategori,robux_jumlah,harga_akhir)
def get_total_belanja(user_id):
    d=load_leaderboard_sultan();u=str(user_id)
    if u not in d: return 0,0,0
    return d[u].get("total_rp",0),d[u].get("total",0),d[u].get("transaksi",0)
def get_total_bulanan(user_id):
    d=load_leaderboard_bulanan();b=datetime.now().strftime("%Y-%m");u=str(user_id);users=d.get(b,{})
    if u not in users: return 0,0,0
    return users[u].get("total_rp",0),users[u].get("total",0),users[u].get("transaksi",0)
def get_robux_dari_rp(rp, kategori="via_username"):
    data=load_pricelist(kategori)
    for robux, harga in data.items():
        if int(harga)==int(rp): return int(robux)
    if data:
        items=sorted(data.items(), key=lambda x: x[1])
        for (r1,h1),(r2,h2) in zip(items, items[1:]):
            if h1 <= rp <= h2 and h2 != h1:
                return int(r1 + (rp - h1) * (r2 - r1) / (h2 - h1))
        r_last, h_last = items[-1]
        if h_last>0: return int(rp * r_last / h_last)
    return int(rp // 155) if rp < 77500 else int(rp // 150)
def konversi_input(jumlah_input, mode, kategori="via_username"):
    if mode=="rupiah":
        robux=get_robux_dari_rp(jumlah_input, kategori); return robux, int(jumlah_input)
    else:
        robux=int(jumlah_input); return robux, get_harga(robux, kategori)
def kurang_sultan_only(user_id, robux_jumlah, harga_akhir):
    try:
        uid=str(user_id); d=load_leaderboard_sultan()
        if uid not in d: return None
        d[uid]["total"]=max(0, d[uid].get("total",0)-int(robux_jumlah))
        d[uid]["total_rp"]=max(0, d[uid].get("total_rp",0)-int(harga_akhir))
        save_leaderboard_sultan(d); return d.get(uid, {"total":0,"total_rp":0,"transaksi":0})
    except Exception as e: print(f"kurang sultan err {e}"); return None
def kurang_bulanan_only(user_id, robux_jumlah, harga_akhir):
    try:
        uid=str(user_id); bulan=datetime.now().strftime("%Y-%m"); d=load_leaderboard_bulanan()
        hasil=None
        if bulan in d and uid in d[bulan]:
            d[bulan][uid]["total"]=max(0, d[bulan][uid].get("total",0)-int(robux_jumlah))
            d[bulan][uid]["total_rp"]=max(0, d[bulan][uid].get("total_rp",0)-int(harga_akhir))
            save_leaderboard_bulanan(d); hasil=d[bulan][uid]
        kurang_sultan_only(user_id, robux_jumlah, harga_akhir)
        return hasil
    except Exception as e: print(f"kurang bulanan err {e}"); return None
def kurang_dua_duanya(user_id, robux_jumlah, harga_akhir):
    s=kurang_sultan_only(user_id, robux_jumlah, harga_akhir); b=kurang_bulanan_only(user_id, robux_jumlah, harga_akhir); return s,b
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
        if jumlah<=0 and harga<=0: return None
        d=load_pending();oid=f"ORDER-{ticket_number:06d}";d[oid]={"user_id":str(user_id),"username":username,"paket":paket_text,"robux":jumlah,"harga":harga,"ticket_number":ticket_number,"channel":channel_name,"kategori":kategori,"waktu":datetime.now().strftime("%d %b %Y %H:%M"),"referral_by":referral_by};save_pending(d);return oid
    except: return None
def load_referral(): return _load("referral.json",{})
def save_referral(d): _save("referral.json",d)
def get_referral_code(uid): return f"MIPI-{int(uid)%100000:05d}"
def claim_referral(new_id,code):
    if not code: return None
    d=load_referral()
    for uid,info in d.items():
        if info.get("code")==code.upper() and str(uid)!=str(new_id): return uid
    return None
def add_referral_komisi(ref_id,harga,buyer):
    try:
        komisi=int(harga*REFERRAL_RATE);d=load_referral();uid=str(ref_id)
        if uid not in d: d[uid]={"code":get_referral_code(ref_id),"total_komisi":0,"total_referral":0,"history":[]}
        d[uid]["total_komisi"]+=komisi;d[uid]["total_referral"]+=1;d[uid]["history"].append({"buyer":buyer,"harga":harga,"komisi":komisi,"waktu":datetime.now().strftime("%d %b %Y %H:%M")});save_referral(d);return komisi
    except: return 0
def load_voucher(): return _load("voucher.json",{})
def save_voucher(d): _save("voucher.json",d)
def redeem_voucher(uid,code):
    try:
        d=load_voucher();k=code.upper()
        if k not in d: return None,"Kode gak ketemu!"
        v=d[k]
        if v.get("dipakai",0)>=v.get("max",1): return None,"Voucher habis!"
        if str(uid) in v.get("used_by",[]): return None,"Udah dipake!"
        v["dipakai"]=v.get("dipakai",0)+1;v.setdefault("used_by",[]).append(str(uid));save_voucher(d);return v,None
    except Exception as e: return None,str(e)
def load_daily(): return _load("daily.json",{})
def save_daily(d): _save("daily.json",d)
def claim_daily(uid):
    try:
        d=load_daily();u=str(uid);today=datetime.now().strftime("%Y-%m-%d")
        if u in d and d[u].get("last_claim")==today: return None,d[u].get("poin",0),"Udah claim hari ini!"
        if u not in d: d[u]={"poin":0,"streak":0,"last_claim":""}
        kemarin=(datetime.now()-timedelta(days=1)).strftime("%Y-%m-%d")
        d[u]["streak"]=d[u]["streak"]+1 if d[u].get("last_claim")==kemarin else 1
        bonus=DAILY_POIN+min(d[u]["streak"]*2,20);d[u]["poin"]+=bonus;d[u]["last_claim"]=today;save_daily(d);return bonus,d[u]["poin"],None
    except Exception as e: return None,0,str(e)
def get_poin(uid): return load_daily().get(str(uid),{}).get("poin",0)
def use_poin(uid,j):
    try:
        d=load_daily();u=str(uid)
        if d.get(u,{}).get("poin",0)<j: return False
        d[u]["poin"]-=j;save_daily(d);return True
    except: return False
def load_notify(): return _load("notify.json",{})
def save_notify(d): _save("notify.json",d)
def add_notify(uid,kat):
    d=load_notify();d.setdefault(kat,[])
    if str(uid) not in d[kat]: d[kat].append(str(uid))
    save_notify(d)
async def send_notify_restock(guild,kat):
    try:
        d=load_notify();users=d.get(kat,[])
        for uid in users:
            try:
                u=await bot.fetch_user(int(uid));await u.send(f"🔔 **RESTOCK!** {kat.upper()} udah DIBUKA lagi! Order di <#{OPEN_TICKET_CHANNEL_ID}>")
            except: pass
        d[kat]=[];save_notify(d)
    except: pass
game_data={}
def start_tebak_harga():
    nominal=random.choice([100,200,300,400,500,1000,2000]);harga=get_harga(nominal,"via_username");pilihan=[harga]
    while len(pilihan)<4:
        fake=int(harga*random.uniform(0.7,1.4)/500)*500
        if fake not in pilihan and fake>0: pilihan.append(fake)
    random.shuffle(pilihan);return nominal,harga,pilihan
def get_top_sultan_channel(g):
    for ch in g.text_channels:
        if "top-sultan" in ch.name.lower(): return ch
    return None
def get_top_bulanan_channel(g):
    for ch in g.text_channels:
        if "top-bulanan" in ch.name.lower() or "top-monthly" in ch.name.lower(): return ch
    return None
def build_top_sultan_embed_semua():
    try:
        data=load_leaderboard_sultan();s=sorted(data.items(),key=lambda x: x[1].get("total_rp",0),reverse=True)[:10];total_all=sum(v.get("total_rp",0) for v in data.values());total_tr=sum(v.get("transaksi",0) for v in data.values())
        e=discord.Embed(title="👑  TOP SULTAN  •  HALL OF FAME",description="✦ **MIPI STORE — LEGENDARY BUYERS** ✦\n*Tidak pernah reset.*\n\n━━━━━━━━━━━━━━",color=0xFFD700)
        if not s: e.add_field(name="Belum Ada Sultan",value="> Jadilah Sultan pertama!",inline=False)
        else:
            t=s[0][1];e.add_field(name="👑 KING OF MIPI STORE",value=f"<@{s[0][0]}> • **{t.get('username','User')}**\n💰 {format_rp(t.get('total_rp',0))} • {t.get('total',0):,} R$ • {t.get('transaksi',0)}x".replace(",","."),inline=False)
            lines="";medals=["🥇","🥈","🥉"]
            for i,(uid,info) in enumerate(s):
                medal=medals[i] if i<3 else f"`{i+1}.`";mx=max(1,s[0][1].get('total_rp',1));bar="█"*max(1,int(info.get('total_rp',0)/mx*10));lines+=f"{medal} <@{uid}>\n╰ {format_rp(info.get('total_rp',0))} • {info.get('total',0):,} R$ • {info.get('transaksi',0)}x • {bar}\n".replace(",",".")
            e.add_field(name="🏆 TOP 10 — ALL TIME",value=lines,inline=False)
        e.add_field(name="📊 TOTAL ALL TIME",value=f"💰 **{format_rp(total_all)}**\n🧾 **{total_tr}** Transaksi • 👥 **{len(data)}** Sultan",inline=True);e.add_field(name="🎖️ LEVEL",value="🔥 LEGEND — 5jt+\n👑 SULTAN — 1jt+",inline=True);e.set_image(url=TOP_SULTAN_IMAGE);e.set_footer(text="MIPI STORE • Top Sultan • All Time");e.timestamp=datetime.now();return e
    except: return discord.Embed(title="Top Sultan",description="Error",color=0xff0000)
def build_top_sultan_embed_bulanan():
    try:
        data=load_leaderboard_bulanan();bulan_ini=datetime.now().strftime("%Y-%m");users=data.get(bulan_ini,{});s=sorted(users.items(),key=lambda x: x[1].get("total_rp",0),reverse=True)[:10];nama_bulan=datetime.now().strftime("%B %Y");total_bulan=sum(v.get("total_rp",0) for v in users.values());total_tr=sum(v.get("transaksi",0) for v in users.values())
        e=discord.Embed(title=f"🌸 TOP BULANAN • {nama_bulan.upper()}",description="♡ **MIPI STORE — BULAN INI** ♡\n*Reset tiap tanggal 1.*\n\n・゜✿ ─── ✿ ゜・",color=0xFF8FAB)
        if not s: e.add_field(name="🌷 Belum Ada Pembeli Bulan Ini",value="> Yuk jadi yang pertama!",inline=False)
        else:
            t=s[0][1];e.add_field(name="🌸 QUEEN / KING BULAN INI",value=f"<@{s[0][0]}> • **{t.get('username','User')}**\n💗 {format_rp(t.get('total_rp',0))} • {t.get('total',0):,} R$ • {t.get('transaksi',0)}x".replace(",","."),inline=False)
            lines="";icons=["🌸","🌷","🌺","💗","💖","✨","🎀","🌼","🌹","💐"]
            for i,(uid,info) in enumerate(s):
                icon=icons[i] if i<10 else "🌸";mx=max(1,s[0][1].get('total_rp',1));pct=int(info.get('total_rp',0)/mx*100);lines+=f"{icon} **#{i+1}** <@{uid}> — {info.get('username','User')}\n╰ 💗 {format_rp(info.get('total_rp',0))} • {info.get('total',0):,} R$ • {info.get('transaksi',0)}x • {pct}%\n".replace(",",".")
            e.add_field(name=f"✨ TOP 10 — {nama_bulan}",value=lines,inline=False)
        e.add_field(name="💗 TOTAL BULAN INI",value=f"**{format_rp(total_bulan)}**\n🧾 **{total_tr}** Transaksi • 👥 **{len(users)}** Pembeli",inline=True);e.add_field(name="📅 PERIODE",value=f"**{nama_bulan}**\nReset: Tanggal 1",inline=True);e.set_image(url=TOP_BULANAN_IMAGE);e.set_footer(text="MIPI STORE • Top Bulanan • Reset Tiap Tanggal 1");e.timestamp=datetime.now();return e
    except: return discord.Embed(title="Top Bulanan",description="Error",color=0xff0000)
async def update_top_sultan(g):
    try:
        ch=get_top_sultan_channel(g)
        if not ch: return
        emb=build_top_sultan_embed_semua()
        async for msg in ch.history(limit=20):
            if msg.author==g.me and msg.embeds and "TOP SULTAN" in str(msg.embeds[0].title): await msg.edit(embed=emb);return
        await ch.send(embed=emb)
    except: pass
async def update_top_bulanan(g):
    try:
        ch=get_top_bulanan_channel(g)
        if not ch: return
        emb=build_top_sultan_embed_bulanan()
        async for msg in ch.history(limit=20):
            if msg.author==g.me and msg.embeds and "TOP BULANAN" in str(msg.embeds[0].title): await msg.edit(embed=emb);return
        await ch.send(embed=emb)
    except: pass
async def update_all_top(g): await update_top_sultan(g);await update_top_bulanan(g)
@tasks.loop(minutes=5)
async def auto_update_top_sultan():
    for g in bot.guilds:
        try: await update_all_top(g)
        except: pass
async def check_auto_role(g,uid,total):
    try:
        m=g.get_member(int(uid))
        if not m: return None
        target=None
        if total>=5000000: target="LEGEND"
        elif total>=1000000: target="SULTAN"
        elif total>=500000: target="VIP"
        elif total>=100000: target="Regular"
        if not target: return None
        role=None
        for r in g.roles:
            if r.name.upper()==target: role=r;break
        if not role:
            try: role=await g.create_role(name=target,colour=discord.Colour.gold() if target in ["SULTAN","LEGEND"] else discord.Colour.pink(),mentionable=True)
            except: return None
        if role not in m.roles: await m.add_roles(role);return target
        return None
    except: return None
def is_admin_or_owner(user,g):
    try:
        if user.id==g.owner_id: return True
        if user.guild_permissions.administrator: return True
        rn=[r.name.lower() for r in user.roles];return any(x in rn for x in ["admin","owner","staff","moderator","adm"])
    except: return False
class KonfirmasiSaldoView(discord.ui.View):
    def __init__(self,oid):
        super().__init__(timeout=None);self.order_id=oid
    @discord.ui.button(label="✅ Konfirmasi Masuk Saldo",style=discord.ButtonStyle.success,custom_id="saldo_confirm_btn")
    async def confirm_btn(self,i:discord.Interaction,b:discord.ui.Button):
        if not is_admin_or_owner(i.user,i.guild): await i.response.send_message("❌ Hanya Admin!",ephemeral=True);return
        pend=load_pending()
        if self.order_id not in pend: await i.response.send_message("❌ Udah diproses!",ephemeral=True);return
        d=pend[self.order_id];add_to_leaderboard(int(d["user_id"]),d["username"],d["paket"],kategori=d.get("kategori","via_username"),robux_jumlah=d.get("robux"),harga_akhir=d.get("harga"));del pend[self.order_id];save_pending(pend)
        kt=""
        if d.get("referral_by"):
            k=add_referral_komisi(d["referral_by"],d["harga"],d["username"]);kt=f"\n💸 Referral: <@{d['referral_by']}> dapet {format_rp(k)} (5%)!"
        await i.response.send_message(f"✅ **SALDO DIKONFIRMASI!**\nBuyer: <@{d['user_id']}>\nPaket: {d['paket']}\n+{d['robux']} R$ masuk saldo!{kt}",ephemeral=False)
        for item in self.children: item.disabled=True
        try: await i.message.edit(view=self)
        except: pass
        try:
            tr,_,_=get_total_belanja(int(d["user_id"]));await check_auto_role(i.guild,int(d["user_id"]),tr)
        except: pass
        try: await update_all_top(i.guild)
        except: pass
    @discord.ui.button(label="❌ Tolak / Order Palsu",style=discord.ButtonStyle.danger,custom_id="saldo_reject_btn")
    async def reject_btn(self,i:discord.Interaction,b:discord.ui.Button):
        if not is_admin_or_owner(i.user,i.guild): await i.response.send_message("❌ Hanya Admin!",ephemeral=True);return
        pend=load_pending()
        if self.order_id not in pend: await i.response.send_message("❌ Udah diproses!",ephemeral=True);return
        d=pend[self.order_id];del pend[self.order_id];save_pending(d);await i.response.send_message(f"❌ Order {self.order_id} DITOLAK!",ephemeral=False)
        for item in self.children: item.disabled=True
        try: await i.message.edit(view=self)
        except: pass
PROMO_FILE="promo.json"
def load_promo(): return _load(PROMO_FILE,{})
def save_promo(d): _save(PROMO_FILE,d)
def cek_promo(kode,harga_awal,jumlah=0):
    try:
        if not kode or not str(kode).strip(): return harga_awal,0,None
        kode=str(kode).upper().strip();d=load_promo()
        if kode not in d: return harga_awal,0,"Kode promo gak ketemu!"
        p=d[kode]
        if jumlah<500: return harga_awal,0,"Minimal 500 Robux!"
        if p.get("dipakai",0)>=p.get("max",999): return harga_awal,0,"Promo habis!"
        diskon=int(harga_awal*p["diskon"]/100) if p["tipe"]=="persen" else int(p["diskon"]);return max(0,harga_awal-diskon),diskon,None
    except: return harga_awal,0,None
giveaway_data={}
class GiveawayView(discord.ui.View):
    def __init__(self,gid):
        super().__init__(timeout=None);self.giveaway_id=gid
    @discord.ui.button(label="JOIN GIVEAWAY",style=discord.ButtonStyle.success,custom_id="join_giveaway",emoji="🎉")
    async def join_btn(self,i:discord.Interaction,b:discord.ui.Button):
        d=giveaway_data.get(self.giveaway_id)
        if not d or d["ended"]: await i.response.send_message("Giveaway berakhir!",ephemeral=True);return
        if i.user.id in d["peserta"]: await i.response.send_message("Udah join!",ephemeral=True);return
        d["peserta"].append(i.user.id);await i.response.send_message("Berhasil join!",ephemeral=True)
async def end_giveaway(g,ch_id,msg_id,gid):
    try:
        d=giveaway_data.get(gid)
        if not d or d["ended"]: return
        d["ended"]=True;ch=g.get_channel(ch_id)
        if not ch: return
        if len(d["peserta"])==0: await ch.send("Giveaway berakhir, gak ada yang join!");return
        n=min(d["pemenang"],len(d["peserta"]));winners=random.sample(d["peserta"],n);wm=", ".join([f"<@{w}>" for w in winners]);await ch.send(f"GIVEAWAY BERAKHIR!\nHadiah: {d['hadiah']}\nPemenang: {wm}")
    except Exception as e: print(f"gw err {e}")
BANNED_WORDS=["wts robux","jual robux","sell robux","jual rb","wts rb","jual limited","wts limited","sell limited","jual robux murah","robux murah","top up robux"]
SCAM_LINKS=["discord.gg/","bit.ly/","tinyurl.com/","free-robux","robux-free"]
def is_banned_selling(t): return any(w in str(t).lower() for w in BANNED_WORDS)
def is_scam_link(t): return any(s in str(t).lower() for s in SCAM_LINKS)
def hitung_harga(paket_text,kategori="via_username",robux_jumlah=None,harga_akhir=None):
    try:
        if robux_jumlah is not None:
            j=int(robux_jumlah);h=int(harga_akhir) if harga_akhir else get_harga(j,kategori);return str(j),format_rp(h)
        m=re.search(r'(\d+)',str(paket_text).replace('.','').replace(',',''))
        if not m: return "500",format_rp(get_harga(500,kategori))
        j=int(m.group(1));return str(j),format_rp(get_harga(j,kategori))
    except: return "500",format_rp(get_harga(500,kategori))
def get_status_channel(g):
    for ch in g.text_channels:
        if "order-status" in ch.name.lower(): return ch
    return None
def get_history_channel(g):
    for ch in g.text_channels:
        if "history" in ch.name.lower(): return ch
    return None
def get_ticket_category(g):
    for c in g.categories:
        if "TICKET" in c.name.upper(): return c
    return None
def get_vouch_channel(g):
    for ch in g.channels:
        if "vouch" in ch.name.lower(): return ch
    return None
def get_omset_channel(g):
    for ch in g.text_channels:
        if "omset" in ch.name.lower() or "rekap" in ch.name.lower() or "history" in ch.name.lower(): return ch
    return get_history_channel(g)
async def send_status_update(g,num,uname,uid,paket,status,color):
    try:
        ch=get_status_channel(g)
        if not ch: return
        e=discord.Embed(title=f"Order Status - Ticket #{num}",description=f"Customer: <@{uid}> ({uname})\nPaket: {paket}\nStatus: {status}",color=color);await ch.send(embed=e)
    except: pass
async def send_history_log(g,ch,data,admin):
    try:
        hc=get_history_channel(g)
        if not hc: return
        jumlah,harga=hitung_harga(data.get("paket","500 Robux"),data.get("kategori","via_username"),robux_jumlah=data.get("robux_jumlah"),harga_akhir=data.get("harga_akhir"))
        e=discord.Embed(color=0x2b2d31);e.description=f"Ticket Log\n\nTicket\n{ch.name if ch else 'ticket'}\nMember\n<@{data['user_id']}>\nNickname\n{data.get('nickname','-')}\nUsername\n{data.get('roblox_username','-')}\nJumlah\n{jumlah}\nTotal\n{harga}\nAdmin\n{admin.mention if admin else 'Auto-Close'}";e.set_image(url=THANKYOU_URL);await hc.send(embed=e)
    except: pass
async def send_vouch(g,user,paket,stars,komentar,tn=0):
    try:
        ch=get_vouch_channel(g)
        if not ch: return
        jumlah,harga=hitung_harga(paket);e=discord.Embed(color=0x2b2d31);e.description=f"VOUCH RECEIVED\n\nTicket ID\n{tn}\nNominal\n{harga}\nBuyer\n<@{user.id}>\nRating\n{'⭐'*stars}\nKomentar\n{komentar} 💗";e.set_thumbnail(url=user.display_avatar.url);await ch.send(embed=e)
    except: pass
def get_statistik():
    try:
        ds=load_leaderboard_sultan();db=load_leaderboard_bulanan();b=datetime.now().strftime("%Y-%m");br=sum(v.get("total_rp",0) for v in db.get(b,{}).values());bt=sum(v.get("transaksi",0) for v in db.get(b,{}).values());ar=sum(v.get("total_rp",0) for v in ds.values());at=sum(v.get("transaksi",0) for v in ds.values());pend=load_pending();hr=sum(d.get("harga",0) for d in pend.values());ht=len(pend);return {"hari_rp":hr,"hari_tr":ht,"bulan_rp":br,"bulan_tr":bt,"all_rp":ar,"all_tr":at}
    except: return {"hari_rp":0,"hari_tr":0,"bulan_rp":0,"bulan_tr":0,"all_rp":0,"all_tr":0}
async def do_auto_close(g,ch,data,reason="auto-closed",admin=None):
    try:
        num=data["number"];uid=data["user_id"];paket=data.get("paket","ORDER ROBUX");user_last_ticket[uid]={"number":num,"paket":paket,"ticket_name":ch.name if ch else "","seller_id":g.owner_id}
        try: await send_history_log(g,ch,data,admin)
        except: pass
        try:
            u=await bot.fetch_user(uid);e=discord.Embed(title="Rate Your Experience",description=f"Hi {u.name}! Ticket #{num} sudah selesai.\nRate ya!",color=0x2b2d31);await u.send(embed=e,view=RatingView(num))
        except: pass
        try:
            oid=add_to_pending(uid,data.get("username","User"),paket,num,ch.name if ch else "",kategori=data.get("kategori","via_username"),robux_jumlah=data.get("robux_jumlah"),harga_akhir=data.get("harga_akhir"),referral_by=data.get("referral_by"))
            if oid:
                cp=get_history_channel(g) or get_status_channel(g)
                if cp:
                    jt,ht=hitung_harga(paket,data.get("kategori","via_username"),robux_jumlah=data.get("robux_jumlah"),harga_akhir=data.get("harga_akhir"));ep=discord.Embed(title=f"⏳ PENDING SALDO - {oid}",description=f"Buyer: <@{uid}>\nPaket: {paket}\nRobux: {jt} R$\nHarga: {ht}\nTicket: #{num}\n\nAdmin pencet ✅ dulu baru masuk saldo!",color=0xfee75c);await cp.send(embed=ep,view=KonfirmasiSaldoView(oid))
        except Exception as e: print(f"pending err {e}")
        if ch.id in ticket_data: del ticket_data[ch.id]
        try: await ch.delete()
        except: pass
    except Exception as e: print(f"close err {e}")
@tasks.loop(minutes=1)
async def check_inactive():
    try:
        now=time.time()
        for cid,d in list(ticket_data.items()):
            last=d.get("last_activity",d["created_at"])
            if now-last>15*60:
                ch=bot.get_channel(cid)
                if not ch: del ticket_data[cid];continue
                await do_auto_close(ch.guild,ch,d)
    except: pass
@tasks.loop(minutes=60)
async def auto_rekap_omset():
    try:
        now=datetime.now()
        if now.hour!=0: return
        for g in bot.guilds:
            s=get_statistik();ch=get_omset_channel(g)
            if not ch: continue
            e=discord.Embed(title="📊 REKAP OMSET HARIAN",description=f"📅 {now.strftime('%d %B %Y')}\n\n💰 Bulan Ini: {format_rp(s['bulan_rp'])} ({s['bulan_tr']} transaksi)\n👑 All Time: {format_rp(s['all_rp'])} ({s['all_tr']} transaksi)",color=0xff69b4);await ch.send(embed=e)
    except: pass
class RatingView(discord.ui.View):
    def __init__(self,tn):
        super().__init__(timeout=None);self.ticket_number=tn
    async def send_thanks(self,i,stars):
        user_ratings[i.user.id]=stars;e=discord.Embed(title="Terima Kasih! 💗",description=f"Kamu memberi rating {'⭐'*stars} ({stars}/5)!",color=0xff69b4);e.set_image(url=THANKYOU_URL);await i.response.edit_message(embed=e,view=self)
    @discord.ui.button(label="⭐ 1",style=discord.ButtonStyle.secondary,custom_id="rate1")
    async def r1(self,i:discord.Interaction,b:discord.ui.Button): await self.send_thanks(i,1)
    @discord.ui.button(label="⭐ 2",style=discord.ButtonStyle.secondary,custom_id="rate2")
    async def r2(self,i:discord.Interaction,b:discord.ui.Button): await self.send_thanks(i,2)
    @discord.ui.button(label="⭐ 3",style=discord.ButtonStyle.primary,custom_id="rate3")
    async def r3(self,i:discord.Interaction,b:discord.ui.Button): await self.send_thanks(i,3)
    @discord.ui.button(label="⭐ 4",style=discord.ButtonStyle.success,custom_id="rate4")
    async def r4(self,i:discord.Interaction,b:discord.ui.Button): await self.send_thanks(i,4)
    @discord.ui.button(label="⭐ 5",style=discord.ButtonStyle.success,custom_id="rate5")
    async def r5(self,i:discord.Interaction,b:discord.ui.Button): await self.send_thanks(i,5)
    @discord.ui.button(label="📝 Add Comment",style=discord.ButtonStyle.secondary,custom_id="add_comment",row=1)
    async def comment(self,i:discord.Interaction,b:discord.ui.Button): await i.response.send_modal(CommentModal(ticket_number=self.ticket_number))
    @discord.ui.button(label="❌ No Thanks",style=discord.ButtonStyle.secondary,custom_id="no_thanks",row=1)
    async def no_thanks(self,i:discord.Interaction,b:discord.ui.Button): await i.response.edit_message(content="Oke! Terima kasih sudah order di MIPI STORE 💗",embed=None,view=None)
class CommentModal(discord.ui.Modal,title="Komentar / Testimoni"):
    def __init__(self,tn):
        super().__init__();self.ticket_number=tn
    komentar=discord.ui.TextInput(label="Komentar kamu",placeholder="satset poll",style=discord.TextStyle.paragraph,required=True)
    async def on_submit(self,i:discord.Interaction):
        stars=user_ratings.get(i.user.id,5);last=user_last_ticket.get(i.user.id,{});paket=last.get("paket","500 Robux")
        for g in bot.guilds:
            if get_vouch_channel(g): await send_vouch(g,i.user,paket,stars,self.komentar.value,ticket_number=self.ticket_number);break
        await i.response.send_message("Terima kasih! 💗 Vouch kamu sudah muncul!",ephemeral=True)
class StatusView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="⏳ Menunggu Pembayaran",style=discord.ButtonStyle.secondary,custom_id="status_waiting")
    async def waiting(self,i:discord.Interaction,b:discord.ui.Button):
        await i.response.defer(ephemeral=True)
        if not is_admin_or_owner(i.user,i.guild): await i.followup.send("Hanya Admin!",ephemeral=True);return
        d=ticket_data.get(i.channel.id,{});await i.followup.send("Status: Menunggu Pembayaran");await send_status_update(i.guild,d.get("number","?"),d.get("username",""),d.get("user_id",i.user.id),d.get("paket","ORDER"),"Menunggu Pembayaran",0xfee75c)
    @discord.ui.button(label="🔄 Diproses",style=discord.ButtonStyle.primary,custom_id="status_process")
    async def process(self,i:discord.Interaction,b:discord.ui.Button):
        await i.response.defer(ephemeral=True)
        if not is_admin_or_owner(i.user,i.guild): await i.followup.send("Hanya Admin!",ephemeral=True);return
        d=ticket_data.get(i.channel.id,{});await i.followup.send("Status: Diproses");await send_status_update(i.guild,d.get("number","?"),d.get("username",""),d.get("user_id",i.user.id),d.get("paket","ORDER"),"Diproses",0x5865f2)
    @discord.ui.button(label="✅ Selesai",style=discord.ButtonStyle.success,custom_id="status_done")
    async def done(self,i:discord.Interaction,b:discord.ui.Button):
        await i.response.defer(ephemeral=True)
        if not is_admin_or_owner(i.user,i.guild): await i.followup.send("Hanya Admin!",ephemeral=True);return
        d=ticket_data.get(i.channel.id,{});await i.followup.send("Status: Selesai!");await send_status_update(i.guild,d.get("number","?"),d.get("username",""),d.get("user_id",i.user.id),d.get("paket","ORDER"),"Selesai",0x57f287)
class CloseView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🔒 CLOSE TICKET",style=discord.ButtonStyle.danger,custom_id="close_ticket")
    async def close_btn(self,i:discord.Interaction,b:discord.ui.Button):
        await i.response.defer(ephemeral=True)
        if not is_admin_or_owner(i.user,i.guild): await i.followup.send("Hanya Admin!",ephemeral=True);return
        ch=i.channel;d=ticket_data.get(ch.id)
        if not d: await ch.delete();return
        await i.followup.send("Ticket ditutup...");await do_auto_close(i.guild,ch,d,reason="closed",admin=i.user)
class SaldoView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="💳 CEK SALDO SAYA",style=discord.ButtonStyle.primary,custom_id="cek_saldo_btn")
    async def cek_saldo(self,i:discord.Interaction,b:discord.ui.Button):
        tr,tro,tt=get_total_belanja(i.user.id);lvl=get_level(tr);nxt,sisa=get_next_level(tr);poin=get_poin(i.user.id);e=discord.Embed(color=0xff1493);e.description=f"INFORMASI SALDO\n\nHalo {i.user.mention}\n\n🏆 Level: {lvl}\n➡️ Next: {nxt} (kurang {format_rp(sisa)})\n\nTotal Belanja: {format_rp(tr)}\nTotal Robux: {tro} R$\nTotal Transaksi: {tt}x\n🎁 Poin: {poin} poin";await i.response.send_message(embed=e,ephemeral=True)
def build_ticket_panel_baru_embed():
    e=discord.Embed(title="🎫 Mipi Store - Ticket Order",description="💎 **Robux Via Username**\n🔑 **Robux Vlog**\n💠 **Beli Limited Item**\n💰 **Jual Limited Item**\n🎁 **Beli Item Offsale**\n⭐ **Beli Roblox Plus**\n🛡️ **Rekber/MM**\n🐱 **Other/Nanya**\n👥 **Via Komunitas**\n💃 **Beli Akun**\n\n✨ **V8:** 3x Add Saldo! Sultan 👑 / Bulanan 🌸 / Dua-duanya!\nMipi Store 💗",color=0x2B2D31);e.set_image(url=WELCOME_URL);e.set_footer(text="Mipi Store - Pilih tombol di bawah!");return e
class OrderModalBaru(discord.ui.Modal):
    def __init__(self,jenis:str):
        self.jenis=jenis;super().__init__(title=f"Order - {jenis} | MIPI STORE")
        if jenis in ["VIA SEND","VIA LOGIN","VIA KOMUNITAS"]:
            self.f1=discord.ui.TextInput(label="Username Roblox (Pakai @)",placeholder="Contoh: @RafixMP",required=True,max_length=100)
            self.f2=discord.ui.TextInput(label="Nickname Roblox",placeholder="Contoh: Rafi",required=True,max_length=100)
            self.f3=discord.ui.TextInput(label="Nominal Robux",placeholder="Contoh: 200",required=True,max_length=100)
            self.add_item(self.f1);self.add_item(self.f2);self.add_item(self.f3)
            self.promo=discord.ui.TextInput(label="Kode Promo (Opsional)",placeholder="Kosongkan jika tidak ada",required=False,max_length=20)
            self.ref=discord.ui.TextInput(label="Kode Referral (Opsional)",placeholder="Kosongkan jika tidak ada",required=False,max_length=20)
            self.add_item(self.promo);self.add_item(self.ref)
        else:
            if jenis in ["BELI LIMITED","JUAL LIMITED","OFFSALE"]: l1,l2,l3="Nama Item","Harga / Budget","Username Roblox";p1,p2,p3="Contoh: Classic Fedora","Contoh: 50000","Contoh: @RafixMP"
            elif jenis=="BELI AKUN": l1,l2,l3="Akun Yang Dicari","Budget","Username Discord";p1,p2,p3="Contoh: Akun 2018+","Contoh: 100000","Contoh: m.rafii"
            elif jenis=="REKBER": l1,l2,l3="Barang Yang Direkber","Nominal","Username Penjual/Pembeli";p1,p2,p3="Contoh: Limited Fedora","Contoh: 200000","Contoh: @pembeli"
            else: l1,l2,l3="Keperluan","Detail","Username Roblox";p1,p2,p3="Contoh: Mau nanya stok","Tulis detailnya","Contoh: @RafixMP"
            self.f1=discord.ui.TextInput(label=l1,placeholder=p1,required=True,max_length=100);self.f2=discord.ui.TextInput(label=l2,placeholder=p2,required=True,max_length=100);self.f3=discord.ui.TextInput(label=l3,placeholder=p3,required=False,max_length=100,style=discord.TextStyle.paragraph);self.add_item(self.f1);self.add_item(self.f2);self.add_item(self.f3)
            self.promo=None;self.ref=None
    async def on_submit(self,i:discord.Interaction):
        try:
            global ticket_counter;ticket_counter+=1;g=i.guild;ov={g.default_role:discord.PermissionOverwrite(read_messages=False),i.user:discord.PermissionOverwrite(read_messages=True,send_messages=True),g.me:discord.PermissionOverwrite(read_messages=True,send_messages=True)};cat=get_ticket_category(g);prefix=self.jenis.lower().replace(" ","-").replace("/","-");ch=await g.create_text_channel(name=f"{prefix}-{ticket_counter}-{i.user.name}",overwrites=ov,category=cat)
            if self.jenis in ["VIA SEND","VIA LOGIN","VIA KOMUNITAS"]:
                roblox_val=self.f1.value.strip()
                if not roblox_val.startswith("@"): roblox_val="@"+roblox_val
                nick_val=self.f2.value.strip();nominal_val=self.f3.value.strip()
            else:
                roblox_val=self.f1.value;nick_val=self.f1.value;nominal_val=self.f2.value
            paket_text=f"{self.jenis} - {nominal_val}";harga_akhir=0;kat=jenis_to_kategori(self.jenis);robux_fix=0;ref_by=None
            if self.jenis in ["VIA SEND","VIA LOGIN","VIA KOMUNITAS"]:
                mt=re.search(r'(\d+)',str(nominal_val).replace('.','').replace(',',''));ji=int(mt.group(1)) if mt else 500;robux_fix=ji;ha=get_harga(ji,kat);kode_input=self.promo.value.strip() if self.promo and self.promo.value else "";harga_akhir,diskon,err=cek_promo(kode_input,ha,ji)
                if kode_input and not err and diskon>0:
                    pd=load_promo();ku=kode_input.upper()
                    if ku in pd: pd[ku]["dipakai"]=pd[ku].get("dipakai",0)+1;save_promo(pd)
                if self.ref and self.ref.value: ref_by=claim_referral(i.user.id,self.ref.value.strip())
            elif self.jenis in ["BELI LIMITED","JUAL LIMITED","OFFSALE","BELI AKUN","REKBER"]:
                mt=re.search(r'(\d+)',str(nominal_val).replace('.','').replace(',',''))
                harga_akhir=int(mt.group(1)) if mt else 0
            ticket_data[ch.id]={"user_id":i.user.id,"username":i.user.name,"nickname":nick_val,"roblox_username":roblox_val,"pembayaran":"QRIS","created_at":time.time(),"last_activity":time.time(),"number":ticket_counter,"paket":paket_text,"promo":(self.promo.value if self.promo else ""),"harga_akhir":harga_akhir,"robux_jumlah":robux_fix,"kategori":kat,"referral_by":ref_by}
            if self.jenis in ["VIA SEND","VIA LOGIN","VIA KOMUNITAS"]:
                desc_text=f"**Jenis:** {self.jenis}\n**Username Roblox:** {roblox_val}\n**Nickname Roblox:** {nick_val}\n**Nominal Robux:** {nominal_val}\n\nTicket #{ticket_counter}\nKirim bukti di sini ya 💗"
            else:
                desc_text=f"**Jenis:** {self.jenis}\n**{self.f1.label}:** {self.f1.value}\n**{self.f2.label}:** {self.f2.value}\n**{self.f3.label}:** {self.f3.value}\n\nTicket #{ticket_counter}\nKirim bukti di sini ya 💗"
            e=discord.Embed(title=f"Ticket Baru - {self.jenis} - {i.user.name}",description=desc_text,color=0xff69b4);e.set_image(url=WELCOME_URL);await ch.send(i.user.mention+" Halo! Selamat datang di MIPI STORE! 🌸",embed=e,view=CloseView());eq=discord.Embed(title="Scan QRIS Disini",description="Silahkan scan QRIS ini ya 💗",color=0xff69b4);eq.set_image(url=QRIS_URL);await ch.send(embed=eq);await ch.send("STATUS ORDER - Owner only:",view=StatusView());await send_status_update(g,ticket_counter,i.user.name,i.user.id,paket_text,"Ticket Baru Dibuat",0xff69b4);gv=discord.ui.View();gv.add_item(discord.ui.Button(label="BUKA TICKET SAYA",style=discord.ButtonStyle.link,url=f"https://discord.com/channels/{g.id}/{ch.id}",emoji="🚀"));await i.response.send_message(f"Ticket **{self.jenis}** kamu sudah dibuat!\n{ch.mention}",view=gv,ephemeral=True)
        except Exception as e:
            print(f"modal err {e}");traceback.print_exc()
            try:
                if i.response.is_done(): await i.followup.send(f"❌ Gagal: {e}",ephemeral=True)
                else: await i.response.send_message(f"❌ Gagal: {e}",ephemeral=True)
            except: pass
class ButtonTicket(discord.ui.Button):
    def __init__(self,label,cid,row,emoji):
        super().__init__(label=label,style=discord.ButtonStyle.primary,custom_id=cid,row=row,emoji=emoji);self.jenis_map={"t_via_send":"VIA SEND","t_via_login":"VIA LOGIN","t_beli_limited":"BELI LIMITED","t_jual_limited":"JUAL LIMITED","t_pluss":"ROBLOX PLUSS","t_offsale":"BELI ITEM OFFSALE","t_rekber":"REKBER","t_other":"OTHER","t_komunitas":"VIA KOMUNITAS","t_beli_akun":"BELI AKUN"}
    async def callback(self,i:discord.Interaction):
        try:
            v=TicketTypeView()
            if not await v.cek_store(i): return
            jenis=self.jenis_map.get(self.custom_id,"VIA SEND");ks=jenis_to_kategori(jenis)
            if jenis=="REKBER": ks="rekber"
            elif jenis=="BELI AKUN": ks="beli_akun"
            elif jenis=="OTHER": ks="other"
            if not is_open(ks): await i.response.send_message(f"❌ Maaf, **{jenis}** lagi **HABIS / TUTUP**!",ephemeral=True);return
            await i.response.send_modal(OrderModalBaru(jenis))
        except Exception as e:
            try: await i.response.send_message(f"❌ Error: {e}",ephemeral=True)
            except: pass
class TicketTypeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        def _label(b,ks): return b if is_open(ks) else b+" - HABIS"
        btns=[("Robux Via Username","t_via_send",0,"<a:robux:1563387482182254725>","via_username"),("Robux Vlog","t_via_login",0,"<:emoji_10:1431192496876027975>","via_login"),("Beli Limited Item","t_beli_limited",1,"<a:diamond:1516624681585869041>","limited"),("Jual Limited Item","t_jual_limited",1,"<a:moneybag:1512329138172596265>","limited"),("Beli Roblox Plus","t_pluss",2,"<:b_RobloxPlus:1499160341983006730>","plus"),("Beli Item Offsale","t_offsale",2,"<a:emoji_20:1550165111333986354>","limited"),("Rekber/MM","t_rekber",3,"<a:emoji_39:1555770513907916822>","rekber"),("Other/Nanya","t_other",3,"<a:b_bluequestion:1345684551502008340>","other"),("Via Komunitas","t_komunitas",4,"<a:rbx:1530537752729223308>","via_komunitas"),("Beli Akun","t_beli_akun",4,"<a:star_purple:1303353812374913035>","beli_akun")]
        for label,cid,row,emoji,ks in btns:
            b=ButtonTicket(_label(label,ks),cid,row=row,emoji=emoji)
            if not is_open(ks): b.disabled=True;b.style=discord.ButtonStyle.secondary
            self.add_item(b)
    async def cek_store(self,i):
        if STORE_STATUS=="break": await i.response.send_message("MIPI STORE LAGI BREAK! ☕ 15-30 menit!",ephemeral=True);return False
        if STORE_STATUS=="closed": await i.response.send_message("MIPI STORE UDAH TUTUP! 💤 Balik besok!",ephemeral=True);return False
        return True
OrderView=TicketTypeView
class EditHargaModal(discord.ui.Modal,title="✏️ Edit Harga"):
    def __init__(self,kat,nom,hl):
        super().__init__();self.kategori=kat;self.nominal=nom;self.harga_lama=hl;self.harga_input=discord.ui.TextInput(label=f"Harga Baru {nom} ({kat})",placeholder=f"Lama: {hl} - Contoh: 75000",required=True,max_length=10);self.add_item(self.harga_input)
    async def on_submit(self,i:discord.Interaction):
        try:
            teks=self.harga_input.value.replace("Rp","").replace(".","").replace(",","").replace(" ","").strip();hb=int(teks)
            if self.kategori=="limited": d=load_pricelist("limited");d[str(self.nominal)]=hb;save_pricelist(d,"limited")
            else: d=load_pricelist(self.kategori);d[int(self.nominal)]=hb;save_pricelist(d,self.kategori)
            try: await update_all_panels(i.guild)
            except: pass
            await i.response.send_message(f"✅ Harga {self.kategori} {self.nominal} jadi {format_rp(hb)}!",ephemeral=True)
        except: await i.response.send_message("❌ Harga harus angka! Contoh: 75000",ephemeral=True)
class EditPricelistView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None);self.kategori="via_username";self.nominal=500;self._build()
    def _build(self):
        for ch in list(self.children):
            if getattr(ch,'custom_id','')=="edit_pilih_nominal": self.remove_item(ch)
        opts=[]
        for n in get_nominal_list(self.kategori):
            label=LIMITED_ITEMS.get(n,{}).get("nama",str(n)) if self.kategori=="limited" else f"{n} Robux"+(" - LARIS" if n==500 else "")+(" - SULTAN" if n==10000 else "")
            opts.append(discord.SelectOption(label=label,value=str(n)))
        s=discord.ui.Select(placeholder=f"2️⃣ Pilih Nominal {self.kategori}!",custom_id="edit_pilih_nominal",options=opts,row=1);s.callback=self.pilih_nominal;self.add_item(s)
    @discord.ui.select(placeholder="1️⃣ Pilih Kategori Dulu",custom_id="edit_pilih_kategori",options=[discord.SelectOption(label="💎 Via Username",value="via_username",emoji="💎"),discord.SelectOption(label="🔑 Via Login",value="via_login",emoji="🔑"),discord.SelectOption(label="👥 Via Komunitas",value="via_komunitas",emoji="👥"),discord.SelectOption(label="⭐ Plus",value="plus",emoji="⭐"),discord.SelectOption(label="💠 Limited",value="limited",emoji="💠")],row=0)
    async def pilih_kategori(self,i:discord.Interaction,s:discord.ui.Select):
        self.kategori=s.values[0]
        if self.kategori=="limited": self.nominal="8bit_royal_crown"
        elif self.kategori=="plus": self.nominal=1000
        else: self.nominal=500
        self._build();await i.response.edit_message(view=self);await i.followup.send(f"✅ Kategori: **{self.kategori}**! Pilih nominal di bawah, terus ✏️ Edit!",ephemeral=True)
    async def pilih_nominal(self,i:discord.Interaction):
        v=i.data['values'][0]
        if self.kategori=="limited": self.nominal=v;harga=get_harga(v,"limited")
        else: self.nominal=int(v);harga=get_harga(self.nominal,self.kategori)
        await i.response.send_message(f"✅ Dipilih: **{self.nominal}**\nHarga: **{format_rp(harga)}**\nPencet ✏️ Edit Harga Ini!",ephemeral=True)
    @discord.ui.button(label="✏️ Edit Harga Ini",style=discord.ButtonStyle.primary,custom_id="edit_harga_ini",emoji="✏️",row=2)
    async def edit_ini(self,i:discord.Interaction,b:discord.ui.Button): await i.response.send_modal(EditHargaModal(self.kategori,self.nominal,get_harga(self.nominal,self.kategori)))
    @discord.ui.button(label="👀 Lihat Harga",style=discord.ButtonStyle.secondary,custom_id="edit_lihat_harga",emoji="👀",row=2)
    async def lihat(self,i:discord.Interaction,b:discord.ui.Button): await i.response.send_message(embed=build_pricelist_embed(self.kategori),ephemeral=True)
    @discord.ui.button(label="➕ Semua +5k",style=discord.ButtonStyle.success,custom_id="edit_plus_5k",emoji="➕",row=3)
    async def plus_5k(self,i:discord.Interaction,b:discord.ui.Button):
        d=load_pricelist(self.kategori)
        for k in list(d.keys()): d[k]=int(d[k])+5000
        save_pricelist(d,self.kategori);await i.response.send_message(f"✅ Semua {self.kategori} naik +5k!",ephemeral=True)
    @discord.ui.button(label="➖ Semua -5k",style=discord.ButtonStyle.secondary,custom_id="edit_min_5k",emoji="➖",row=3)
    async def min_5k(self,i:discord.Interaction,b:discord.ui.Button):
        d=load_pricelist(self.kategori)
        for k in list(d.keys()): d[k]=max(1000,int(d[k])-5000)
        save_pricelist(d,self.kategori);await i.response.send_message(f"✅ Semua {self.kategori} turun -5k!",ephemeral=True)
    @discord.ui.button(label="🎁 Diskon 10%",style=discord.ButtonStyle.success,custom_id="edit_diskon_10",emoji="🎁",row=3)
    async def diskon_10(self,i:discord.Interaction,b:discord.ui.Button):
        d=load_pricelist(self.kategori)
        for k in list(d.keys()): d[k]=int(round(int(d[k])*0.90/500)*500)
        save_pricelist(d,self.kategori);await i.response.send_message(f"✅ Semua {self.kategori} diskon 10%!",ephemeral=True)
    @discord.ui.button(label="🔄 Reset",style=discord.ButtonStyle.danger,custom_id="edit_reset",emoji="🔄",row=3)
    async def reset(self,i:discord.Interaction,b:discord.ui.Button):
        d=DEFAULT_PRICELIST_PER_KATEGORI.get(self.kategori,{}).copy();save_pricelist(d,self.kategori);await i.response.send_message(f"✅ {self.kategori} di-reset!",ephemeral=True)
class TambahProdukModal(discord.ui.Modal,title="➕ Tambah Produk"):
    def __init__(self): super().__init__()
    kode=discord.ui.TextInput(label="Kode Produk (tanpa spasi)",placeholder="Contoh: akun_korblox",required=True,max_length=30);nama=discord.ui.TextInput(label="Nama Produk",placeholder="Contoh: Akun Korblox",required=True,max_length=50);harga=discord.ui.TextInput(label="Harga (angka aja)",placeholder="Contoh: 500000",required=True,max_length=10);stok=discord.ui.TextInput(label="Stok (angka)",placeholder="Contoh: 5 / 9999",required=True,max_length=10);deskripsi=discord.ui.TextInput(label="Deskripsi",placeholder="Contoh: Akun Korblox full email",style=discord.TextStyle.paragraph,required=False,max_length=200)
    async def on_submit(self,i:discord.Interaction):
        try: kb=self.kode.value.lower().replace(" ","_");hi=int(self.harga.value.replace(".","").replace(",",""));si=int(self.stok.value.replace(".",""));d=load_produk();d[kb]={"nama":self.nama.value,"harga":hi,"stok":si,"deskripsi":self.deskripsi.value or "-","emoji":"📦","kategori":"other"};save_produk(d);await i.response.send_message(f"✅ Produk **{self.nama.value}** ditambah! {format_rp(hi)} Stok {si}",ephemeral=True)
        except: await i.response.send_message("❌ Harga & Stok harus angka!",ephemeral=True)
class KuranginProdukModal(discord.ui.Modal,title="➖ Kurangin / Hapus Produk"):
    def __init__(self): super().__init__()
    kode=discord.ui.TextInput(label="Kode Produk",placeholder="Contoh: akun_sultan",required=True,max_length=30);jumlah=discord.ui.TextInput(label="Kurangin berapa? / HAPUS",placeholder="Contoh: 1 / HAPUS",required=True,max_length=10)
    async def on_submit(self,i:discord.Interaction):
        kb=self.kode.value.lower().strip();d=load_produk()
        if kb not in d: await i.response.send_message(f"❌ Kode `{kb}` gak ketemu!",ephemeral=True);return
        if self.jumlah.value.strip().upper()=="HAPUS": del d[kb];save_produk(d);await i.response.send_message(f"✅ Produk dihapus!",ephemeral=True);return
        try: kurang=int(self.jumlah.value);d[kb]["stok"]=max(0,d[kb].get("stok",0)-kurang);save_produk(d);await i.response.send_message(f"✅ Stok dikurangin! Sisa {d[kb]['stok']}",ephemeral=True)
        except: await i.response.send_message("❌ Jumlah harus angka / HAPUS!",ephemeral=True)
class TambahStokModal(discord.ui.Modal,title="📦 Tambah Stok"):
    def __init__(self): super().__init__()
    kode=discord.ui.TextInput(label="Kode Produk",placeholder="Contoh: akun_sultan",required=True,max_length=30);jumlah=discord.ui.TextInput(label="Tambah berapa?",placeholder="Contoh: 5",required=True,max_length=10)
    async def on_submit(self,i:discord.Interaction):
        kb=self.kode.value.lower().strip();d=load_produk()
        if kb not in d: await i.response.send_message("❌ Kode gak ketemu!",ephemeral=True);return
        try: d[kb]["stok"]=d[kb].get("stok",0)+int(self.jumlah.value);save_produk(d);await i.response.send_message(f"✅ Stok ditambah! Sekarang {d[kb]['stok']}",ephemeral=True)
        except: await i.response.send_message("❌ Jumlah harus angka!",ephemeral=True)
class PanelProdukView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="➕ Tambah Produk",style=discord.ButtonStyle.success,custom_id="produk_tambah",emoji="➕",row=0)
    async def tambah(self,i:discord.Interaction,b:discord.ui.Button):
        if not is_admin_or_owner(i.user,i.guild): await i.response.send_message("❌ Hanya Admin!",ephemeral=True);return
        await i.response.send_modal(TambahProdukModal())
    @discord.ui.button(label="➖ Kurangin / Hapus",style=discord.ButtonStyle.danger,custom_id="produk_kurang",emoji="➖",row=0)
    async def kurang(self,i:discord.Interaction,b:discord.ui.Button):
        if not is_admin_or_owner(i.user,i.guild): await i.response.send_message("❌ Hanya Admin!",ephemeral=True);return
        await i.response.send_modal(KuranginProdukModal())
    @discord.ui.button(label="📦 Tambah Stok",style=discord.ButtonStyle.primary,custom_id="produk_tambah_stok",emoji="📦",row=1)
    async def tambah_stok(self,i:discord.Interaction,b:discord.ui.Button):
        if not is_admin_or_owner(i.user,i.guild): await i.response.send_message("❌ Hanya Admin!",ephemeral=True);return
        await i.response.send_modal(TambahStokModal())
    @discord.ui.button(label="🛍️ Lihat Katalog",style=discord.ButtonStyle.secondary,custom_id="produk_lihat",emoji="🛍️",row=1)
    async def lihat(self,i:discord.Interaction,b:discord.ui.Button): await i.response.send_message(embed=build_produk_embed(),ephemeral=True)
class PricelistPublicView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.select(placeholder="Pilih Kategori Produk >",custom_id="mipi_pricelist_public",options=[discord.SelectOption(label="Robux Via Username (Visend)",value="via_username",emoji="💎"),discord.SelectOption(label="Robux Via Login (Vilog)",value="via_login",emoji="🔑"),discord.SelectOption(label="Robux Via Komunitas",value="via_komunitas",emoji="👥"),discord.SelectOption(label="Roblox Plus",value="plus",emoji="⭐"),discord.SelectOption(label="Limited Item",value="limited",emoji="💠"),discord.SelectOption(label="Rekber / Middleman",value="rekber",emoji="🛡️")])
    async def pilih_kategori_public(self,i:discord.Interaction,s:discord.ui.Select):
        try:
            kat=s.values[0];e=build_rekber_embed() if kat=="rekber" else build_pricelist_embed(kat);await i.response.send_message(embed=e,ephemeral=True)
        except Exception as e: print(f"select err {e}")
def build_pricelist_public_embed():
    e=discord.Embed(title="💎 DAFTAR HARGA ROBUX • MIPI STORE",description="💗 **Pilih kategori di dropdown bawah:**\n\n💎 Via Username\n🔑 Via Login\n👥 Via Komunitas\n⭐ Roblox Plus\n💠 Limited Item\n🛡️ Rekber\n\n💗 **Mipi Store**",color=0xff69b4);e.set_image(url=WELCOME_URL);e.set_footer(text="MIPI STORE • Pilih kategori di bawah!");return e
# ===== PANEL SALDO - FIXED =====
panel_saldo_state={}
class TargetUserSelect(discord.ui.UserSelect):
    def __init__(self, parent_view):
        super().__init__(placeholder="1️⃣ Pilih siapa yang mau di-setting? 👤", row=0)
        self.parent_view = parent_view
    async def callback(self, i: discord.Interaction):
        if i.user.id != self.parent_view.admin_id:
            await i.response.send_message("❌ Ini panel orang lain!", ephemeral=True); return
        self.parent_view.get_state()["target"] = self.values[0].id
        await i.response.edit_message(embed=self.parent_view.build_embed(), view=self.parent_view)
class PanelSaldoView(discord.ui.View):
    def __init__(self,admin_id):
        super().__init__(timeout=300);self.admin_id=admin_id
        if admin_id not in panel_saldo_state: panel_saldo_state[admin_id]={"target":None,"mode":"robux","kategori":"via_username","aksi":"add_sultan"}
        self.add_item(TargetUserSelect(self))
    def get_state(self): return panel_saldo_state[self.admin_id]
    def build_embed(self):
        s=self.get_state();target_txt=f"<@{s['target']}>" if s['target'] else "❌ Belum pilih!";mode_txt="🪙 Robux" if s['mode']=="robux" else "💵 Rupiah"
        aksi_map={"add_sultan":"👑 + Sultan doang (Bulanan GAK ikut)","min_sultan":"👑 - Sultan doang (Bulanan GAK ikut)","add_bulanan":"🌸 + Bulanan doang (Sultan IKUT!)","min_bulanan":"🌸 - Bulanan doang (Sultan IKUT kurang!)","add_both":"✅ + Dua-duanya","min_both":"✅ - Dua-duanya"}
        e=discord.Embed(title="⚙️ PANEL SALDO - MIPI STORE",description=f"**Tinggal klik-klik, gak perlu ngetik!**\n\n👤 **Target:** {target_txt}\n🪙 **Mode:** {mode_txt}\n📦 **Kategori:** {s['kategori']}\n🎯 **Aksi:** {aksi_map.get(s['aksi'])}\n\n**Cara:**\n1️⃣ Pilih orang\n2️⃣ Pilih Mode + Kategori + Aksi\n3️⃣ Pencet **✅ LANJUT - KETIK JUMLAH**",color=0xff69b4);e.set_footer(text="MIPI STORE • Panel Saldo");return e
    @discord.ui.select(placeholder="2️⃣ Pilih Mode: Robux / Rupiah",options=[discord.SelectOption(label="🪙 Robux",value="robux",emoji="🪙"),discord.SelectOption(label="💵 Rupiah",value="rupiah",emoji="💵")],row=1)
    async def pilih_mode(self,i:discord.Interaction,select:discord.ui.Select):
        if i.user.id!=self.admin_id: await i.response.send_message("❌ Ini panel orang lain!",ephemeral=True);return
        self.get_state()["mode"]=select.values[0];await i.response.edit_message(embed=self.build_embed(),view=self)
    @discord.ui.select(placeholder="3️⃣ Pilih Kategori",options=[discord.SelectOption(label="💎 Via Username",value="via_username",emoji="💎"),discord.SelectOption(label="🔑 Via Login",value="via_login",emoji="🔑"),discord.SelectOption(label="👥 Via Komunitas",value="via_komunitas",emoji="👥"),discord.SelectOption(label="⭐ Plus",value="plus",emoji="⭐"),discord.SelectOption(label="💠 Limited",value="limited",emoji="💠")],row=2)
    async def pilih_kategori(self,i:discord.Interaction,select:discord.ui.Select):
        if i.user.id!=self.admin_id: await i.response.send_message("❌ Ini panel orang lain!",ephemeral=True);return
        self.get_state()["kategori"]=select.values[0];await i.response.edit_message(embed=self.build_embed(),view=self)
    @discord.ui.select(placeholder="4️⃣ Pilih Aksi: + / - Sultan / Bulanan",options=[discord.SelectOption(label="👑 + Sultan Doang",value="add_sultan",emoji="👑",description="Bulanan GAK ikut"),discord.SelectOption(label="👑 - Sultan Doang",value="min_sultan",emoji="👑",description="Bulanan GAK ikut"),discord.SelectOption(label="🌸 + Bulanan Doang",value="add_bulanan",emoji="🌸",description="Sultan IKUT!"),discord.SelectOption(label="🌸 - Bulanan Doang",value="min_bulanan",emoji="🌸",description="Sultan IKUT kurang!"),discord.SelectOption(label="✅ + Dua-duanya",value="add_both",emoji="✅",description="Sultan + Bulanan"),discord.SelectOption(label="✅ - Dua-duanya",value="min_both",emoji="✅",description="Sultan + Bulanan")],row=3)
    async def pilih_aksi(self,i:discord.Interaction,select:discord.ui.Select):
        if i.user.id!=self.admin_id: await i.response.send_message("❌ Ini panel orang lain!",ephemeral=True);return
        self.get_state()["aksi"]=select.values[0];await i.response.edit_message(embed=self.build_embed(),view=self)
    @discord.ui.button(label="✅ LANJUT - KETIK JUMLAH",style=discord.ButtonStyle.success,emoji="✅",row=4)
    async def lanjut(self,i:discord.Interaction,b:discord.ui.Button):
        if i.user.id!=self.admin_id: await i.response.send_message("❌ Ini panel orang lain!",ephemeral=True);return
        s=self.get_state()
        if not s["target"]: await i.response.send_message("❌ Pilih orang dulu lek! Di dropdown paling atas!",ephemeral=True);return
        await i.response.send_modal(PanelJumlahModal(self.admin_id))
    @discord.ui.button(label="🔄 Refresh",style=discord.ButtonStyle.secondary,emoji="🔄",row=4)
    async def refresh(self,i:discord.Interaction,b:discord.ui.Button): await i.response.edit_message(embed=self.build_embed(),view=self)
class PanelJumlahModal(discord.ui.Modal,title="Ketik Jumlah - Panel Saldo"):
    def __init__(self,admin_id):
        super().__init__();self.admin_id=admin_id;s=panel_saldo_state.get(admin_id,{"mode":"robux"});label="Ketik Robux (Contoh: 1000)" if s["mode"]=="robux" else "Ketik Rupiah (Contoh: 150000)";self.jumlah_input=discord.ui.TextInput(label=label,placeholder="Angka aja!",required=True,max_length=15);self.add_item(self.jumlah_input)
    async def on_submit(self,i:discord.Interaction):
        try:
            s=panel_saldo_state.get(self.admin_id)
            if not s or not s["target"]: await i.response.send_message("❌ Pilih orang dulu di panel!",ephemeral=True);return
            teks=self.jumlah_input.value.replace("Rp","").replace(".","").replace(",","").replace(" ","").strip();jumlah=int(teks)
            if jumlah<=0: await i.response.send_message("❌ Harus lebih dari 0!",ephemeral=True);return
            kat=kategori_alias(s["kategori"]);robux,harga=konversi_input(jumlah,s["mode"],kat);target=await bot.fetch_user(s["target"]);aksi=s["aksi"];mode_txt=f"🪙 {robux} R$" if s["mode"]=="robux" else f"💵 {format_rp(jumlah)} (= {robux} R$)"
            if aksi=="add_sultan":
                add_to_sultan_only(target.id,target.name,f"{robux} Robux",kategori=kat,robux_jumlah=robux,harga_akhir=harga);await i.response.send_message(f"👑 **+{mode_txt}** ke **TOP SULTAN** doang!\n{target.mention} • {format_rp(harga)}\n📅 Bulanan: GAK IKUT! ❌",ephemeral=False)
                try: await update_top_sultan(i.guild)
                except: pass
            elif aksi=="min_sultan":
                hasil=kurang_sultan_only(target.id,robux,harga)
                if hasil is None: await i.response.send_message(f"❌ {target.mention} belum ada di Top Sultan!",ephemeral=True);return
                await i.response.send_message(f"👑 **-{mode_txt}** dari **TOP SULTAN** doang!\n{target.mention}\nSisa: **{hasil.get('total',0):,} R$** ({format_rp(hasil.get('total_rp',0))})".replace(",","."),ephemeral=False)
                try: await update_top_sultan(i.guild)
                except: pass
            elif aksi=="add_bulanan":
                add_to_bulanan_only(target.id,target.name,f"{robux} Robux",kategori=kat,robux_jumlah=robux,harga_akhir=harga);await i.response.send_message(f"🌸 **+{mode_txt}** ke **TOP BULANAN** doang!\n{target.mention} • {format_rp(harga)}\n👑 Sultan: **IKUT!** ✅ (All Time)",ephemeral=False)
                try: await update_all_top(i.guild)
                except: pass
            elif aksi=="min_bulanan":
                hasil=kurang_bulanan_only(target.id,robux,harga)
                if hasil is None: await i.response.send_message(f"❌ {target.mention} belum ada di Top Bulanan!",ephemeral=True);return
                await i.response.send_message(f"🌸 **-{mode_txt}** dari **TOP BULANAN** doang!\n{target.mention}\nSisa Bulanan: **{hasil.get('total',0):,} R$** ({format_rp(hasil.get('total_rp',0))})\n👑 Sultan: **IKUT KURANG!** ✅".replace(",","."),ephemeral=False)
                try: await update_all_top(i.guild)
                except: pass
            elif aksi=="add_both":
                add_to_leaderboard(target.id,target.name,f"{robux} Robux",kategori=kat,robux_jumlah=robux,harga_akhir=harga);await i.response.send_message(f"✅ **+{mode_txt}** ke **DUA-DUANYA!**\n{target.mention} • {format_rp(harga)}",ephemeral=False)
                try: await update_all_top(i.guild)
                except: pass
            elif aksi=="min_both":
                kurang_dua_duanya(target.id,robux,harga);await i.response.send_message(f"✅ **-{mode_txt}** dari **DUA-DUANYA!**\n{target.mention}",ephemeral=False)
                try: await update_all_top(i.guild)
                except: pass
        except Exception as e: await i.response.send_message(f"❌ Harus angka ya lek! Error: {e}",ephemeral=True)
class PanelUtamaAdminView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="⚙️ PANEL SALDO",style=discord.ButtonStyle.primary,custom_id="panel_utama_saldo",emoji="⚙️",row=0)
    async def saldo(self,i:discord.Interaction,b:discord.ui.Button):
        if not is_admin_or_owner(i.user,i.guild): await i.response.send_message("❌ Hanya Admin!",ephemeral=True);return
        view=PanelSaldoView(i.user.id);await i.response.send_message(embed=view.build_embed(),view=view,ephemeral=True)
    @discord.ui.button(label="💎 EDIT PRICELIST",style=discord.ButtonStyle.primary,custom_id="panel_utama_pricelist",emoji="💎",row=0)
    async def pricelist(self,i:discord.Interaction,b:discord.ui.Button):
        if not is_admin_or_owner(i.user,i.guild): await i.response.send_message("❌ Hanya Admin!",ephemeral=True);return
        e=discord.Embed(title="💎 EDIT PRICELIST",description="1️⃣ Pilih Kategori\n2️⃣ Pilih Nominal\n3️⃣ Pencet ✏️ Edit!",color=0xff69b4);await i.response.send_message(embed=e,view=EditPricelistView(),ephemeral=True)
    @discord.ui.button(label="🛍️ KELOLA PRODUK",style=discord.ButtonStyle.success,custom_id="panel_utama_produk",emoji="🛍️",row=0)
    async def produk(self,i:discord.Interaction,b:discord.ui.Button):
        if not is_admin_or_owner(i.user,i.guild): await i.response.send_message("❌ Hanya Admin!",ephemeral=True);return
        e=discord.Embed(title="🛍️ KELOLA PRODUK",description="➕ Tambah / ➖ Kurangin / 📦 Tambah Stok",color=0xff69b4);await i.response.send_message(embed=e,view=PanelProdukView(),ephemeral=True)
    @discord.ui.button(label="🎫 PANEL TICKET",style=discord.ButtonStyle.secondary,custom_id="panel_utama_ticket",emoji="🎫",row=1)
    async def ticket(self,i:discord.Interaction,b:discord.ui.Button):
        if not is_admin_or_owner(i.user,i.guild): await i.response.send_message("❌ Hanya Admin!",ephemeral=True);return
        await i.response.send_message(embed=build_ticket_panel_baru_embed(),view=TicketTypeView(),ephemeral=True)
    @discord.ui.button(label="💰 PANEL PRICELIST",style=discord.ButtonStyle.secondary,custom_id="panel_utama_pricelist_pub",emoji="💰",row=1)
    async def pricelist_pub(self,i:discord.Interaction,b:discord.ui.Button):
        if not is_admin_or_owner(i.user,i.guild): await i.response.send_message("❌ Hanya Admin!",ephemeral=True);return
        await i.response.send_message(embed=build_pricelist_public_embed(),view=PricelistPublicView(),ephemeral=True)
    @discord.ui.button(label="🏪 BUKA TOKO",style=discord.ButtonStyle.success,custom_id="panel_utama_open",emoji="🏪",row=2)
    async def open_toko(self,i:discord.Interaction,b:discord.ui.Button):
        global STORE_STATUS
        if not is_admin_or_owner(i.user,i.guild): await i.response.send_message("❌ Hanya Admin!",ephemeral=True);return
        STORE_STATUS="open";await i.response.send_message("✅ Mipi Store **DIBUKA**!",ephemeral=True)
    @discord.ui.button(label="☕ BREAK",style=discord.ButtonStyle.primary,custom_id="panel_utama_break",emoji="☕",row=2)
    async def break_toko(self,i:discord.Interaction,b:discord.ui.Button):
        global STORE_STATUS
        if not is_admin_or_owner(i.user,i.guild): await i.response.send_message("❌ Hanya Admin!",ephemeral=True);return
        STORE_STATUS="break";await i.response.send_message("☕ Mipi Store **BREAK** 15-30 menit!",ephemeral=True)
    @discord.ui.button(label="💤 TUTUP TOKO",style=discord.ButtonStyle.danger,custom_id="panel_utama_close",emoji="💤",row=2)
    async def close_toko(self,i:discord.Interaction,b:discord.ui.Button):
        global STORE_STATUS
        if not is_admin_or_owner(i.user,i.guild): await i.response.send_message("❌ Hanya Admin!",ephemeral=True);return
        STORE_STATUS="closed";await i.response.send_message("💤 Mipi Store **TUTUP**!",ephemeral=True)
PANEL_FILE="panel.json"
def load_panel():
    try:
        with open(PANEL_FILE,"r") as f: return json.load(f)
    except: return {}
def save_panel(d):
    try:
        with open(PANEL_FILE,"w") as f: json.dump(d,f,indent=2)
    except: pass
async def update_all_panels(g):
    try:
        panels=load_panel()
        for key,info in list(panels.items()):
            try:
                ch=g.get_channel(int(info["channel_id"]))
                if not ch: continue
                msg=await ch.fetch_message(int(info["message_id"]))
                if key=="ticket": await msg.edit(embed=build_ticket_panel_baru_embed(),view=TicketTypeView())
                elif key=="pricelist": await msg.edit(embed=build_pricelist_public_embed(),view=PricelistPublicView())
                elif key=="produk": await msg.edit(embed=build_produk_embed(),view=PanelProdukView())
                elif key=="admin": await msg.edit(embed=discord.Embed(title="⚙️ PANEL ADMIN - MIPI STORE",description="Semua tinggal pencet! Gak perlu ngetik!",color=0xff69b4),view=PanelUtamaAdminView())
            except: pass
    except: pass
async def refresh_ticket_panel(g):
    try: await update_all_panels(g)
    except: pass
@bot.event
async def on_message(m):
    try:
        if m.author.bot: return
        if m.guild and "market" in m.channel.name.lower():
            if m.author.id!=m.guild.owner_id and not m.author.guild_permissions.administrator:
                if is_banned_selling(m.content) or is_scam_link(m.content):
                    try: await m.delete()
                    except: pass
                    await m.channel.send(f"{m.author.mention} DILARANG JUALAN / LINK SCAM!",delete_after=10);return
        if m.channel.id in ticket_data: ticket_data[m.channel.id]["last_activity"]=time.time()
        await bot.process_commands(m)
    except: pass
@bot.event
async def on_ready():
    print(f"Login {bot.user} - MIPI STORE V8 FIX!")
    bot.add_view(OrderView());bot.add_view(TicketTypeView());bot.add_view(CloseView());bot.add_view(StatusView());bot.add_view(RatingView(0));bot.add_view(SaldoView());bot.add_view(GiveawayView("dummy"));bot.add_view(EditPricelistView());bot.add_view(PanelProdukView());bot.add_view(PricelistPublicView());bot.add_view(PanelUtamaAdminView())
    for oid in load_pending().keys():
        try: bot.add_view(KonfirmasiSaldoView(oid))
        except: pass
    if not check_inactive.is_running(): check_inactive.start()
    if not auto_update_top_sultan.is_running(): auto_update_top_sultan.start()
    if not auto_rekap_omset.is_running(): auto_rekap_omset.start()
    for g in bot.guilds:
        try: await update_all_top(g)
        except: pass
    try: synced=await bot.tree.sync();print(f"Synced {len(synced)} commands!")
    except Exception as e: print(f"Sync err {e}")
@bot.tree.command(name="ticket",description="Tampilkan panel order MIPI STORE")
async def ticket(i:discord.Interaction):
    try:
        await safe_defer(i,ephemeral=False);ch_target=i.guild.get_channel(OPEN_TICKET_CHANNEL_ID) or i.channel;panels=load_panel()
        if "ticket" in panels:
            try: ch=i.guild.get_channel(int(panels["ticket"]["channel_id"]));msg=await ch.fetch_message(int(panels["ticket"]["message_id"]));await msg.edit(embed=build_ticket_panel_baru_embed(),view=TicketTypeView());await safe_followup(i,content=f"✅ Panel di-update! Cek {ch.mention}",ephemeral=True);return
            except: pass
        msg=await ch_target.send(embed=build_ticket_panel_baru_embed(),view=TicketTypeView());panels["ticket"]={"channel_id":str(msg.channel.id),"message_id":str(msg.id)};save_panel(panels);await safe_followup(i,content=f"✅ Panel dikirim ke {ch_target.mention}!",ephemeral=True)
    except Exception as e: await safe_followup(i,content=f"❌ Error: {e}",ephemeral=True)
@bot.tree.command(name="pricelist",description="Lihat pricelist dropdown!")
async def pricelist_baru(i:discord.Interaction):
    try:
        await safe_defer(i,ephemeral=True);e=build_pricelist_public_embed();msg=await i.channel.send(embed=e,view=PricelistPublicView());panels=load_panel();panels["pricelist"]={"channel_id":str(msg.channel.id),"message_id":str(msg.id)};save_panel(panels);await safe_followup(i,content="✅ Pricelist dikirim!",ephemeral=True)
    except Exception as e: await safe_followup(i,content=f"❌ Error: {e}",ephemeral=True)
@bot.tree.command(name="panel-admin",description="Buka SEMUA PANEL ADMIN - Tinggal pencet! ⚙️")
async def panel_admin_cmd(i:discord.Interaction):
    await safe_defer(i,ephemeral=True)
    if not is_admin_or_owner(i.user,i.guild): await safe_followup(i,content="❌ Hanya Admin!",ephemeral=True);return
    e=discord.Embed(title="⚙️ PANEL ADMIN - MIPI STORE",description="**Semua tinggal pencet! Gak perlu ngetik!**\n\n⚙️ **PANEL SALDO** - Tambah / Kurang Sultan / Bulanan\n💎 **EDIT PRICELIST** - Ganti harga\n🛍️ **KELOLA PRODUK** - Tambah produk\n🎫 **PANEL TICKET** - Panel order\n💰 **PANEL PRICELIST** - Panel harga\n🏪 **BUKA / BREAK / TUTUP TOKO** - Tinggal pencet!",color=0xff69b4);e.set_image(url=WELCOME_URL)
    msg=await i.channel.send(embed=e,view=PanelUtamaAdminView());panels=load_panel();panels["admin"]={"channel_id":str(msg.channel.id),"message_id":str(msg.id)};save_panel(panels);await safe_followup(i,content="✅ Panel Admin dikirim!",ephemeral=True)
@bot.tree.command(name="panel-saldo",description="Buka PANEL SALDO - Tinggal pencet! ⚙️")
async def panel_saldo_cmd(i:discord.Interaction):
    await safe_defer(i,ephemeral=True)
    if not is_admin_or_owner(i.user,i.guild): await safe_followup(i,content="❌ Hanya Admin!",ephemeral=True);return
    view=PanelSaldoView(i.user.id);await safe_followup(i,embed=view.build_embed(),view=view,ephemeral=True)
@bot.tree.command(name="open",description="Buka toko")
async def open_cmd(i:discord.Interaction):
    global STORE_STATUS;await safe_defer(i,ephemeral=True)
    if not is_admin_or_owner(i.user,i.guild): await safe_followup(i,content="Cuma admin!",ephemeral=True);return
    STORE_STATUS="open";await safe_followup(i,content="✅ Mipi Store **DIBUKA**!")
@bot.tree.command(name="break",description="Toko break sebentar")
async def break_cmd(i:discord.Interaction):
    global STORE_STATUS;await safe_defer(i,ephemeral=True)
    if not is_admin_or_owner(i.user,i.guild): await safe_followup(i,content="Cuma admin!",ephemeral=True);return
    STORE_STATUS="break";await safe_followup(i,content="☕ Mipi Store **BREAK** 15-30 menit!")
@bot.tree.command(name="close",description="Tutup toko")
async def close_cmd(i:discord.Interaction):
    global STORE_STATUS;await safe_defer(i,ephemeral=True)
    if not is_admin_or_owner(i.user,i.guild): await safe_followup(i,content="Cuma admin!",ephemeral=True);return
    STORE_STATUS="closed";await safe_followup(i,content="💤 Mipi Store **TUTUP**!")
@bot.tree.command(name="panel-edit-pricelist",description="Buka panel edit pricelist (Admin)")
async def panel_edit_pricelist(i:discord.Interaction):
    await safe_defer(i,ephemeral=True)
    if not is_admin_or_owner(i.user,i.guild): await safe_followup(i,content="❌ Hanya Admin!",ephemeral=True);return
    e=discord.Embed(title="💎 EDIT PRICELIST",description="1️⃣ Pilih Kategori\n2️⃣ Pilih Nominal\n3️⃣ Pencet ✏️ Edit!",color=0xff69b4);await i.channel.send(embed=e,view=EditPricelistView());await safe_followup(i,content="✅ Panel Edit dikirim!",ephemeral=True)
@bot.tree.command(name="panel-produk",description="Buka panel produk (Admin)")
async def panel_produk(i:discord.Interaction):
    await safe_defer(i,ephemeral=True)
    if not is_admin_or_owner(i.user,i.guild): await safe_followup(i,content="❌ Hanya Admin!",ephemeral=True);return
    e=discord.Embed(title="🛍️ KELOLA PRODUK",description="➕ Tambah / ➖ Kurangin / 📦 Tambah Stok",color=0xff69b4);await i.channel.send(embed=e,view=PanelProdukView());await safe_followup(i,content="✅ Panel Produk dikirim!",ephemeral=True)
@bot.tree.command(name="list-produk",description="Lihat semua produk")
async def list_produk(i:discord.Interaction): await safe_defer(i,ephemeral=True);await safe_followup(i,embed=build_produk_embed(),ephemeral=True)
@bot.tree.command(name="tutup-kategori",description="Tutup 1 tombol (Admin)")
async def tutup_kategori(i:discord.Interaction,kategori:str):
    await safe_defer(i,ephemeral=True)
    if not is_admin_or_owner(i.user,i.guild): await safe_followup(i,content="Hanya Admin!",ephemeral=True);return
    kat=kategori_alias(kategori);set_stock(kat,False);await refresh_ticket_panel(i.guild);await safe_followup(i,content=f"🔴 **{kat.upper()} DITUTUP!**",ephemeral=True)
@bot.tree.command(name="buka-kategori",description="Buka lagi 1 tombol (Admin)")
async def buka_kategori(i:discord.Interaction,kategori:str):
    await safe_defer(i,ephemeral=True)
    if not is_admin_or_owner(i.user,i.guild): await safe_followup(i,content="Hanya Admin!",ephemeral=True);return
    kat=kategori_alias(kategori);set_stock(kat,True);await refresh_ticket_panel(i.guild);await send_notify_restock(i.guild,kat);await safe_followup(i,content=f"🟢 **{kat.upper()} DIBUKA LAGI!**",ephemeral=True)
@bot.tree.command(name="cek-stock",description="Cek stock")
async def cek_stock(i:discord.Interaction):
    try:
        await safe_defer(i,ephemeral=True);s=load_stock();txt="📦 **STATUS STOCK**\n\n"
        for k in ["via_username","via_login","via_komunitas","plus","limited","rekber","beli_akun","other"]: txt+=f"{'🟢 BUKA' if s.get(k,True) else '🔴 TUTUP'} — {k}\n"
        await safe_followup(i,content=txt,ephemeral=True)
    except Exception as e: await safe_followup(i,content=f"❌ Error: {e}",ephemeral=True)
@bot.tree.command(name="notify",description="DM otomatis kalo restock!")
async def notify_cmd(i:discord.Interaction,kategori:str): await safe_defer(i,ephemeral=True);kat=kategori_alias(kategori);add_notify(i.user.id,kat);await safe_followup(i,content=f"🔔 Oke! Kalo **{kat}** restock, kamu aku DM! 💗",ephemeral=True)
@bot.tree.command(name="saldo",description="Cek saldo kamu")
async def saldo_cmd(i:discord.Interaction,user:discord.User=None):
    await safe_defer(i,ephemeral=True);t=user or i.user;tr,tro,tt=get_total_belanja(t.id);lvl=get_level(tr);nxt,sisa=get_next_level(tr);poin=get_poin(t.id);e=discord.Embed(color=0xff1493);e.description=f"Saldo {t.mention}\n\n🏆 Level: {lvl}\n➡️ Next: {nxt} (kurang {format_rp(sisa)})\n\nTotal Belanja: {format_rp(tr)}\nTotal Robux: {tro} R$\nTransaksi: {tt}x\n🎁 Poin: {poin}";await safe_followup(i,embed=e,ephemeral=True)
@bot.tree.command(name="top-sultan",description="Lihat Top Sultan ALL TIME 👑")
async def top_sultan_cmd(i:discord.Interaction):
    try: await safe_defer(i,ephemeral=True);e=build_top_sultan_embed_semua();await safe_followup(i,embed=e,ephemeral=True)
    except Exception as e: await safe_followup(i,content=f"❌ Error: {e}",ephemeral=True)
@bot.tree.command(name="top-bulanan",description="Lihat Top Bulanan 🌸")
async def top_bulanan_cmd(i:discord.Interaction):
    try: await safe_defer(i,ephemeral=True);e=build_top_sultan_embed_bulanan();await safe_followup(i,embed=e,ephemeral=True)
    except Exception as e: await safe_followup(i,content=f"❌ Error: {e}",ephemeral=True)
@bot.tree.command(name="reset-bulanan",description="Reset Top Bulanan (Admin)")
async def reset_bulanan_cmd(i:discord.Interaction):
    await safe_defer(i,ephemeral=True)
    if not is_admin_or_owner(i.user,i.guild): await safe_followup(i,content="Hanya Admin!",ephemeral=True);return
    save_leaderboard_bulanan({});await update_top_bulanan(i.guild);await safe_followup(i,content="✅ **Top Bulanan di-reset!** Top Sultan aman!",ephemeral=True)
@bot.tree.command(name="statistik",description="Lihat statistik omset")
async def statistik_cmd(i:discord.Interaction):
    await safe_defer(i,ephemeral=True);s=get_statistik();e=discord.Embed(title="📊 STATISTIK MIPI STORE",description=f"📅 Hari Ini: {format_rp(s['hari_rp'])}\n📅 Bulan Ini: {format_rp(s['bulan_rp'])} ({s['bulan_tr']} transaksi)\n👑 All Time: {format_rp(s['all_rp'])} ({s['all_tr']} transaksi)",color=0xff69b4);await safe_followup(i,embed=e,ephemeral=True)
@bot.tree.command(name="referral",description="Lihat kode referral kamu")
async def referral_cmd(i:discord.Interaction):
    await safe_defer(i,ephemeral=True);d=load_referral();uid=str(i.user.id);code=get_referral_code(i.user.id)
    if uid not in d: d[uid]={"code":code,"total_komisi":0,"total_referral":0,"history":[]};save_referral(d)
    info=d[uid];await safe_followup(i,content=f"💸 **REFERRAL KAMU**\n\n🔑 Kode: **{info['code']}**\n💰 Komisi: {format_rp(info['total_komisi'])}\n👥 Temen: {info['total_referral']} orang",ephemeral=True)
@bot.tree.command(name="daily",description="Claim daily reward!")
async def daily_cmd(i:discord.Interaction):
    await safe_defer(i,ephemeral=True);bonus,total,err=claim_daily(i.user.id)
    if err: await safe_followup(i,content=f"❌ {err}\nPoin: {total}",ephemeral=True)
    else: await safe_followup(i,content=f"🎁 **DAILY BERHASIL!** +{bonus} poin! Total: {total} poin",ephemeral=True)
@bot.tree.command(name="tuker-poin",description="Tuker poin jadi Robux!")
async def tuker_poin(i:discord.Interaction,jumlah:int):
    await safe_defer(i,ephemeral=True);poin=get_poin(i.user.id)
    if poin<jumlah: await safe_followup(i,content=f"❌ Poin cuma {poin}!",ephemeral=True);return
    if jumlah<100: await safe_followup(i,content="❌ Minimal 100 poin!",ephemeral=True);return
    if not use_poin(i.user.id,jumlah): await safe_followup(i,content="❌ Gagal!",ephemeral=True);return
    oid=add_to_pending(i.user.id,i.user.name,f"TUKER POIN - {jumlah} Robux",999999,f"tuker-poin-{i.user.name}",kategori="via_username",robux_jumlah=jumlah,harga_akhir=0);await safe_followup(i,content=f"✅ Tuker berhasil! +{jumlah} Robux PENDING! ID: {oid}",ephemeral=True)
@bot.tree.command(name="buat-voucher",description="Bikin voucher (Admin)")
async def buat_voucher(i:discord.Interaction,kode:str,diskon:int,tipe:str="persen",max_pakai:int=10):
    await safe_defer(i,ephemeral=True)
    if not is_admin_or_owner(i.user,i.guild): await safe_followup(i,content="Hanya Admin!",ephemeral=True);return
    d=load_voucher();d[kode.upper()]={"diskon":int(diskon),"tipe":tipe.lower(),"max":int(max_pakai),"dipakai":0,"used_by":[]};save_voucher(d);await safe_followup(i,content=f"✅ Voucher **{kode.upper()}** dibuat!",ephemeral=True)
@bot.tree.command(name="redeem-voucher",description="Redeem voucher!")
async def redeem_voucher_cmd(i:discord.Interaction,kode:str):
    await safe_defer(i,ephemeral=True);v,err=redeem_voucher(i.user.id,kode)
    if err: await safe_followup(i,content=f"❌ {err}",ephemeral=True)
    else: await safe_followup(i,content=f"✅ Voucher {kode.upper()} diredeem! Diskon {v['diskon']} {v['tipe']}!",ephemeral=True)
@bot.tree.command(name="tebak-harga",description="Main tebak harga!")
async def tebak_harga(i:discord.Interaction):
    await safe_defer(i,ephemeral=True);nominal,harga,pilihan=start_tebak_harga();game_data[i.user.id]={"nominal":nominal,"harga":harga,"pilihan":pilihan};txt=f"🎮 **TEBAK HARGA**\n\nBerapa harga **{nominal} Robux Via Username**?\n\n"
    for idx,p in enumerate(pilihan,1): txt+=f"{idx}. {format_rp(p)}\n"
    txt+="\nJawab pake `/jawab-tebak <nomor>`!";await safe_followup(i,content=txt,ephemeral=True)
@bot.tree.command(name="jawab-tebak",description="Jawab tebak harga!")
async def jawab_tebak(i:discord.Interaction,nomor:int):
    await safe_defer(i,ephemeral=True)
    if i.user.id not in game_data: await safe_followup(i,content="Ketik /tebak-harga dulu!",ephemeral=True);return
    g=game_data.pop(i.user.id)
    if g["pilihan"][nomor-1]==g["harga"]:
        kode=f"GAME-{i.user.id%10000:04d}";d=load_voucher();d[kode]={"diskon":5,"tipe":"persen","max":1,"dipakai":0,"used_by":[]};save_voucher(d);await safe_followup(i,content=f"🎉 BENAR! Kamu dapet voucher **{kode}** (5%)!",ephemeral=True)
    else: await safe_followup(i,content=f"❌ Salah! Harganya {format_rp(g['harga'])}!",ephemeral=True)
@bot.tree.command(name="tambah-promo",description="Tambah promo (Admin)")
async def tambah_promo(i:discord.Interaction,kode:str,diskon:int,tipe:str="persen",max_pakai:int=999):
    await safe_defer(i,ephemeral=True)
    if not is_admin_or_owner(i.user,i.guild): await safe_followup(i,content="Hanya Admin!",ephemeral=True);return
    d=load_promo();d[kode.upper()]={"diskon":int(diskon),"tipe":tipe.lower(),"max":int(max_pakai),"dipakai":0};save_promo(d);await safe_followup(i,content=f"✅ Promo **{kode.upper()}** ditambah!",ephemeral=True)
@bot.tree.command(name="lihat-promo",description="Lihat semua promo")
async def lihat_promo(i:discord.Interaction):
    await safe_defer(i,ephemeral=True);d=load_promo()
    if not d: await safe_followup(i,content="Belum ada promo!",ephemeral=True);return
    txt="🎁 **DAFTAR PROMO**\n\n"
    for k,v in d.items(): txt+=f"**{k}** — {v.get('diskon')} {v.get('tipe')} — {v.get('dipakai',0)}/{v.get('max',999)}\n"
    await safe_followup(i,content=txt,ephemeral=True)
@bot.tree.command(name="giveaway",description="Bikin giveaway (Admin)")
async def giveaway_cmd(i:discord.Interaction,hadiah:str,pemenang:int=1,menit:int=60):
    await safe_defer(i,ephemeral=True)
    if not is_admin_or_owner(i.user,i.guild): await safe_followup(i,content="Hanya Admin!",ephemeral=True);return
    gid=f"GW-{int(time.time())}";giveaway_data[gid]={"hadiah":hadiah,"host_mention":i.user.mention,"peserta":[],"pemenang":int(pemenang),"ended":False};e=discord.Embed(title="🎉 GIVEAWAY MIPI STORE!",description=f"Hadiah: {hadiah}\nHost: {i.user.mention}\nPeserta: 0 orang",color=0xff69b4);msg=await i.channel.send(embed=e,view=GiveawayView(gid));await safe_followup(i,content=f"✅ Giveaway dibuat! Berakhir {menit} menit lagi!",ephemeral=True);await asyncio.sleep(int(menit)*60);await end_giveaway(i.guild,msg.channel.id,msg.id,gid)
@bot.tree.command(name="pending",description="Lihat pending (Admin)")
async def pending_cmd(i:discord.Interaction):
    await safe_defer(i,ephemeral=True)
    if not is_admin_or_owner(i.user,i.guild): await safe_followup(i,content="Hanya Admin!",ephemeral=True);return
    d=load_pending()
    if not d: await safe_followup(i,content="✅ Gak ada pending!",ephemeral=True);return
    txt="⏳ **PENDING SALDO**\n\n"
    for oid,dd in d.items(): txt+=f"**{oid}** — <@{dd['user_id']}> — {dd['paket']} — {dd['robux']} R$ — {format_rp(dd['harga'])}\n"
    await safe_followup(i,content=txt,ephemeral=True)
@bot.tree.command(name="lihat-harga",description="Lihat harga pricelist")
async def lihat_harga(i:discord.Interaction,kategori:str="via_username"): await safe_defer(i,ephemeral=True);kat=kategori_alias(kategori);await safe_followup(i,embed=build_pricelist_embed(kat),ephemeral=True)
@bot.tree.command(name="pricelist-rekber",description="Pricelist Rekber")
async def pricelist_rekber(i:discord.Interaction): await safe_defer(i,ephemeral=True);await i.channel.send(embed=build_rekber_embed(),view=RekberView(guild_id=i.guild.id));await safe_followup(i,content="✅ Pricelist Rekber dikirim!",ephemeral=True)
@bot.tree.command(name="help-mipi",description="Lihat semua command")
async def help_mipi(i:discord.Interaction):
    await safe_defer(i,ephemeral=True);txt="💗 **HELP - MIPI STORE V8**\n\n**PANEL (TINGGAL PENCET!):** `/panel-admin` `/panel-saldo` `/ticket` `/pricelist`\n**SALDO:** `/saldo` `/top-sultan` `/top-bulanan` `/pending`\n**STOCK:** `/tutup-kategori` `/buka-kategori` `/cek-stock` `/notify`\n**V8:** `/referral` `/daily` `/tuker-poin` `/buat-voucher` `/redeem-voucher` `/tebak-harga`\n**TOKO:** `/open` `/break` `/close`\n**ADMIN:** `/tambah-promo` `/lihat-promo` `/giveaway` `/reset-bulanan`";await safe_followup(i,content=txt,ephemeral=True)
bot.run(os.getenv("DISCORD_TOKEN"))
