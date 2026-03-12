import streamlit as st
import streamlit.components.v1 as components
import requests
from datetime import datetime, timedelta
import time
import base64, os

st.set_page_config(
    page_title="Jadwal Sholat · AL-AZHAR SYIFA BUDI TALAGA BESTARI",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
/* Sembunyikan semua elemen bawaan Streamlit */
#MainMenu, header, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stHeader"],
[data-testid="stBottom"],
[data-testid="stFullScreenFrame"],
.stDeployButton,
[data-testid="collapsedControl"] { display:none !important; }

/* Hapus semua padding dan background putih */
.block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
    background: transparent !important;
}
.appview-container, .main {
    background: #0b1a2e !important;
    padding: 0 !important;
}
html, body, [class*="css"] {
    overflow: hidden !important;
    background: #0b1a2e !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Hapus background putih di semua wrapper div */
.element-container, .stMarkdown, section.main > div {
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Iframe tanpa border dan background */
iframe {
    border: none !important;
    display: block !important;
    background: #0b1a2e !important;
}
</style>""", unsafe_allow_html=True)

# ── Fetch jadwal Kabupaten Tangerang ──────────────────────────────
@st.cache_data(ttl=3600)
def fetch_jadwal():
    try:
        url    = "http://api.aladhan.com/v1/timingsByCity"
        # ── Ubah city di sini untuk kota lain ──
        params = {"city": "Tangerang", "country": "Indonesia", "method": 11}
        r = requests.get(url, params=params, timeout=10)
        t = r.json()["data"]["timings"]
        return {
            "Subuh":   t["Fajr"],
            "Terbit":  t["Sunrise"],
            "Dzuhur":  t["Dhuhr"],
            "Ashar":   t["Asr"],
            "Maghrib": t["Maghrib"],
            "Isya":    t["Isha"],
        }
    except:
        return {}

def waktu_berikutnya(jadwal):
    # Gunakan UTC+7 manual agar benar di server Streamlit Cloud (UTC)
    from datetime import timezone
    now_utc = datetime.now(timezone.utc)
    now = now_utc.astimezone(timezone(timedelta(hours=7)))
    now_naive = now.replace(tzinfo=None)

    lst = []
    for nama, jam_str in jadwal.items():
        try:
            h, m = map(int, jam_str.split(":"))
            w = now_naive.replace(hour=h, minute=m, second=0, microsecond=0)
            if w <= now_naive:
                w += timedelta(days=1)
            lst.append((nama, w))
        except:
            pass
    if not lst:
        return "─", "─", 0, 0, 0
    nama, w = min(lst, key=lambda x: x[1])
    sec = int((w - now_naive).total_seconds())
    return nama, w.strftime("%H:%M"), sec // 3600, (sec % 3600) // 60, sec % 60

def img_b64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()
    return ""

# ── Data ──────────────────────────────────────────────────────────
jadwal              = fetch_jadwal()
from datetime import timezone as _tz
now = datetime.now(_tz.utc).astimezone(_tz(timedelta(hours=7))).replace(tzinfo=None)
nama_b, jam_b, h, m, s = waktu_berikutnya(jadwal)
img_src             = img_b64("Masjid_Al_Irsyad.jpeg")

hari_id  = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"]
bulan_id = ["","Januari","Februari","Maret","April","Mei","Juni",
            "Juli","Agustus","September","Oktober","November","Desember"]
tgl_str  = hari_id[now.weekday()] + ", " + str(now.day) + " " + bulan_id[now.month] + " " + str(now.year)
clock_str = now.strftime('%H:%M:%S')
hh = str(h).zfill(2)
mm = str(m).zfill(2)
ss = str(s).zfill(2)

prayers = [
    ("🌙", "SUBUH",   jadwal.get("Subuh",   "─")),
    ("🌅", "TERBIT",  jadwal.get("Terbit",  "─")),
    ("☀️", "DZUHUR",  jadwal.get("Dzuhur",  "─")),
    ("🌤️","ASHAR",   jadwal.get("Ashar",   "─")),
    ("🌇", "MAGHRIB", jadwal.get("Maghrib", "─")),
    ("🌃", "ISYA",    jadwal.get("Isya",    "─")),
]

cards_html = ""
for ikon, nama, waktu in prayers:
    active = nama.lower() == nama_b.lower()
    cls    = "prayer-card active" if active else "prayer-card"
    badge  = '<span class="badge">BERIKUTNYA</span>' if active else ""
    cards_html += (
        '<div class="' + cls + '">'
        '<span class="ci">' + ikon + '</span>'
        '<div class="ci2">'
        '<div class="cn">' + nama + '</div>'
        '<div class="ct">' + waktu + '</div>'
        '</div>'
        + badge +
        '</div>'
    )

# ── CSS ───────────────────────────────────────────────────────────
css = """
<style>
:root{--gold:#DBF227;--dark:#0b1a2e;--panel:#112240;--text:#e8f4ff;--muted:#7a9abf;--border:#1e3a5c;}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:100%;height:100vh;overflow:hidden;background:var(--dark);font-family:'Lato',sans-serif;color:var(--text);}
canvas{position:fixed;inset:0;z-index:0;pointer-events:none;}
.root{position:relative;z-index:1;width:100%;height:100vh;display:grid;grid-template-rows:58px 1fr;padding:10px;gap:8px;}

/* TOPBAR */
.topbar{display:flex;align-items:center;justify-content:space-between;background:#112240cc;border:1px solid var(--border);border-radius:10px;padding:0 20px;}
.tl{display:flex;align-items:center;gap:12px;}
.ti{font-size:1.6rem;}
.tt{font-family:'Cinzel',serif;font-size:clamp(1rem,1.6vw,1.25rem);color:var(--gold);letter-spacing:.15em;line-height:1.2;}
.ts{font-size:.68rem;color:var(--muted);letter-spacing:.12em;}
.tc{font-family:'Cinzel',serif;font-size:clamp(1.5rem,2.8vw,2.2rem);color:#fff;letter-spacing:.1em;text-shadow:0 0 24px rgba(219,242,39,.5);line-height:1;}
.td{font-size:.7rem;color:var(--gold);letter-spacing:.1em;margin-top:2px;text-align:right;}

/* MAIN */
.main{display:grid;grid-template-columns:70% 1fr;gap:10px;min-height:0;}

/* LEFT */
.lp{display:grid;grid-template-rows:70% 1fr;gap:8px;min-height:0;}

/* IMAGE */
.ib{border-radius:12px;overflow:hidden;position:relative;min-height:0;border:1px solid var(--border);}
.ib img{width:100%;height:100%;object-fit:cover;object-position:center 30%;display:block;filter:brightness(.85) saturate(.9);}
.io{position:absolute;inset:0;background:linear-gradient(to bottom,transparent 40%,rgba(11,26,46,.7) 100%);}
.ilbl{position:absolute;bottom:10px;left:12px;font-size:.6rem;color:rgba(219,242,39,.8);letter-spacing:.2em;text-transform:uppercase;}

/* COUNTDOWN */
.cb{background:var(--panel);border:1px solid var(--border);border-radius:12px;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:14px;min-height:0;position:relative;overflow:hidden;}
.cb::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 50% 0%,rgba(219,242,39,.09) 0%,transparent 70%);}
.cl{font-size:.65rem;letter-spacing:.28em;color:var(--muted);text-transform:uppercase;margin-bottom:6px;}
.ct2{font-family:'Cinzel',serif;font-size:clamp(2.2rem,4.5vw,3.8rem);color:var(--gold);letter-spacing:.1em;line-height:1;text-shadow:0 0 28px rgba(219,242,39,.55);}
.cn2{font-size:.85rem;color:#fff;letter-spacing:.12em;margin-top:8px;opacity:.95;}
.br{font-size:.58rem;color:#2a4a6a;letter-spacing:.12em;margin-top:10px;}

/* RIGHT */
.rp{display:flex;flex-direction:column;gap:7px;min-height:0;}
.prayer-card{flex:1;min-height:0;background:var(--panel);border:1px solid var(--border);border-radius:10px;display:flex;align-items:center;padding:0 18px;gap:14px;position:relative;overflow:hidden;transition:all .3s;}
.prayer-card.active{border-color:rgba(219,242,39,.55);background:rgba(219,242,39,.07);box-shadow:0 0 20px rgba(219,242,39,.1);}
.prayer-card::before{content:'';position:absolute;left:0;top:18%;height:64%;width:4px;border-radius:4px;background:transparent;transition:background .3s;}
.prayer-card.active::before{background:var(--gold);}
.ci{font-size:clamp(1.1rem,1.8vw,1.6rem);flex-shrink:0;}
.ci2{flex:1;min-width:0;}
.cn{font-size:clamp(.6rem,.9vw,.78rem);letter-spacing:.28em;color:var(--muted);text-transform:uppercase;margin-bottom:2px;}
.prayer-card.active .cn{color:var(--gold);font-weight:700;}
.ct{font-family:'Cinzel',serif;font-size:clamp(1.4rem,2.2vw,2rem);color:var(--text);letter-spacing:.05em;line-height:1;}
.prayer-card.active .ct{color:#fff;}
.badge{font-size:clamp(.55rem,.78vw,.68rem);font-weight:700;letter-spacing:.12em;background:var(--gold);color:var(--dark);padding:3px 9px;border-radius:20px;flex-shrink:0;animation:pulse 1.4s infinite;}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
</style>
"""

# ── JS (no curly braces from f-string) ───────────────────────────
js = """
<script>
var cv=document.getElementById('cv'),cx=cv.getContext('2d'),st=[];
function rs(){
  cv.width=innerWidth;cv.height=innerHeight;st=[];
  for(var i=0;i<110;i++) st.push({x:Math.random()*innerWidth,y:Math.random()*innerHeight,r:Math.random()*1.3+.3,p:Math.random()*Math.PI*2,s:Math.random()*.022+.006});
}
function dr(t){
  cx.clearRect(0,0,cv.width,cv.height);
  for(var i=0;i<st.length;i++){var s=st[i];var a=.15+.65*(.5+.5*Math.sin(s.p+t*s.s));cx.beginPath();cx.arc(s.x,s.y,s.r,0,Math.PI*2);cx.fillStyle='rgba(219,242,39,'+a+')';cx.fill();}
  requestAnimationFrame(dr);
}
window.addEventListener('resize',rs);rs();dr(0);

function tickClock(){
  var n=new Date();
  var el=document.getElementById('clk');
  if(el) el.textContent=n.toTimeString().slice(0,8);
}
setInterval(tickClock,1000);

var cdH=parseInt(document.getElementById('cdH').value);
var cdM=parseInt(document.getElementById('cdM').value);
var cdS=parseInt(document.getElementById('cdS').value);
var totalSec=cdH*3600+cdM*60+cdS;
function tickCountdown(){
  if(totalSec>0) totalSec--;
  var h=Math.floor(totalSec/3600);
  var m=Math.floor((totalSec%3600)/60);
  var s=totalSec%60;
  function z(n){return n<10?'0'+n:''+n;}
  var el=document.getElementById('cdt');
  if(el) el.textContent=z(h)+' : '+z(m)+' : '+z(s);
}
setInterval(tickCountdown,1000);
</script>
"""

# ── Assemble HTML ─────────────────────────────────────────────────
html = (
    "<!DOCTYPE html><html><head>"
    "<meta charset='UTF-8'>"
    "<link href='https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Lato:wght@300;400&display=swap' rel='stylesheet'>"
    + css +
    "</head><body>"
    "<canvas id='cv'></canvas>"
    "<div class='root'>"

    "<div class='topbar'>"
    "<div class='tl'><span class='ti'>🕌</span>"
    "<div><div class='tt'>SEKOLAH AL-AZHAR SYIFA BUDI TALAGA BESTARI</div><div class='ts'>Kab. Tangerang · Banten, Indonesia</div></div>"
    "</div>"
    "<div style='text-align:right'>"
    "<div class='tc' id='clk'>" + clock_str + "</div>"
    "<div class='td'>" + tgl_str + "</div>"
    "</div></div>"

    "<div class='main'>"

    "<div class='lp'>"
    "<div class='ib'>"
    "<img src='" + img_src + "' alt='Masjid Al Irsyad'>"
    "<div class='io'></div>"
    "<div class='ilbl'>SEKOLAH AL-AZHAR SYIFA BUDI TALAGA BESTARI · CIKUPA</div>"
    "</div>"
    "<div class='cb'>"
    "<div class='cl'>Menuju adzan berikutnya</div>"
    "<div class='ct2' id='cdt'>" + hh + " : " + mm + " : " + ss + "</div>"
    "<div class='cn2'>⟶  Menuju " + nama_b + "  (" + jam_b + ")</div>"
    "<div class='br'>by ASBTB · ASBATB.com</div>"
    "</div></div>"

    "<div class='rp'>" + cards_html + "</div>"
    "</div>"
    "</div>"

    "<input type='hidden' id='cdH' value='" + str(h) + "'>"
    "<input type='hidden' id='cdM' value='" + str(m) + "'>"
    "<input type='hidden' id='cdS' value='" + str(s) + "'>"
    + js +
    "</body></html>"
)

# Inject CSS tambahan untuk hapus margin di luar iframe
st.markdown("""
<style>
div[data-testid="stComponentsContainer"] > div,
div[data-testid="stComponentsContainer"] {
    padding: 0 !important;
    margin: 0 !important;
    line-height: 0 !important;
}
</style>""", unsafe_allow_html=True)

components.html(html, height=780, scrolling=False)

time.sleep(60)
st.rerun()
