"""Basa Khuji AI - powered by Gemma. Run: python app.py  ->  http://127.0.0.1:8000"""
import os, sys, re, json, sqlite3, time, requests
from flask import Flask, jsonify, request, send_from_directory

BASE = os.path.dirname(os.path.abspath(__file__))
# tiny .env loader (no extra dependency, works on Windows)
try:
    for line in open(os.path.join(BASE, ".env"), encoding="utf-8"):
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.strip().split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
except FileNotFoundError:
    pass

API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL = os.environ.get("GEMMA_MODEL", "gemma-3-27b-it")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
MODELS = {"gemma": MODEL, "gemini": GEMINI_MODEL}
def endpoint(name): return f"https://generativelanguage.googleapis.com/v1beta/models/{name}:generateContent"
SYSTEM_PROMPT = open(os.path.join(BASE, "system_prompt.txt"), encoding="utf-8").read()
app = Flask(__name__, static_folder=os.path.join(BASE, "static"))

DEMO_REPORT = """## 🚨 BASA KHUJI: DHAKA REALITY REPORT
**📊 Bachelor Survival Score:** 23/100
**Survival Meter:** 🟩🟩🟥🟥🟥🟥🟥🟥🟥🟥
**Official Verdict:** 💀 CHADER NICHE TANDOORI TRAP
**Detected Area Vibe:** Mirpur-10 — where "near Metro" means a rickshaw, a prayer, and a negotiation.

### 🤥 What They Wrote vs. Brutal Dhaka Reality
| 🪧 What the To-Let Claims | 💀 What It Actually Means in Dhaka |
|---|---|
| "5 min from Metro" | 2.5 km, 1,200 BDT/month in rickshaw fare, and one existential crisis at Kazipara. |
| "Airy 7th floor room" | Chader niche. In April the ceiling doubles as a tandoor. |
| "Family preferred" | Bachelors may apply only if they are secretly a BCS cadet. |
| ⚠️ Gas/water not mentioned | Titas wakes at 2 AM; WASA water has the aroma of rusty iron. |

### 💸 The "Actual" Monthly Damage Calculator
**Advertised Rent:** 8,000 BDT
**Hidden Dhaka Bachelor Tax:** +3,100 BDT
**Breakdown:** +1,200 rickshaw fare; +800 extra fan bill for 7th-floor heat; +1,100 "service charge" (Darowan's mood)
**🔥 REAL MONTHLY DAMAGE: 11,100 BDT / month**

### 📞 The "Uncle-Approved" Phone Alibi Script
🗣️ "Assalamu Alaikum Uncle. Ami BCS-er preparation nicchi, pach owakto moshjide namaz porhi, raat 9:45 e ghumai, gaan-baajna sigarette kichu pochondo kori na, ar Dhaka te amar kono bondhu-o nai."

**🧠 Street-Smart Viewing Tip:** Wear a panjabi, carry a tasbih, and greet the Darowan before the Bariwala.

---
### 🥊 LEVEL 2 UNLOCKED: LIVE "BARIWALA BOSS FIGHT"
**Target Boss:** Alhajj Abdul Kader (Retired Govt Officer from Mirpur who watches CCTV 14 hours a day)
**Uncle's Current Approval:** 20/100 🟥🟥⬜⬜⬜⬜⬜⬜⬜⬜

👴🏾 **Bariwala Uncle (On the Phone):** "হ্যালো?! সাইনবোর্ডে ফ্যামিলি লেখা দেখেন নাই? ব্যাচেলর হয়ে ফোন দিছেন কোন সাহসে? রাখি ফোন!"
"""

DB = os.environ.get("DB_PATH", os.path.join(BASE, "basa.db"))
def db():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c
with db() as c:
    c.execute("CREATE TABLE IF NOT EXISTS listings(id INTEGER PRIMARY KEY, title TEXT, area TEXT, rent INTEGER, beds INTEGER, floor TEXT, pref TEXT, description TEXT, phone TEXT, photo TEXT, created REAL)")
    if c.execute("SELECT COUNT(*) FROM listings").fetchone()[0] == 0:
        seed = [("2-bed flat near Mirpur-10", "Mirpur-10", 8000, 2, "7th", "Family", "Airy 7th floor flat, 5 min from Metro. Call after Asr.", ""),
                ("Bachelor mess seat", "Mohammadpur", 3500, 1, "3rd", "Bachelor", "Gas and water 24 hrs, advance 2 months. Strictly no smoking.", ""),
                ("Sublet room, ready flat", "Uttara Sector 10", 6500, 1, "5th", "Any", "Near everything. bKash advance 5000 to confirm.", "")]
        for t in seed:
            c.execute("INSERT INTO listings(title,area,rent,beds,floor,pref,description,phone,photo,created) VALUES(?,?,?,?,?,?,?,?,?,?)", (*t[:7], "", "", time.time()))

@app.route("/api/listings", methods=["GET", "POST"])
def listings():
    if request.method == "GET":
        with db() as c:
            return jsonify([dict(r) for r in c.execute("SELECT * FROM listings ORDER BY id DESC LIMIT 60")])
    d = request.get_json(force=True)
    try:
        title, area = str(d["title"]).strip()[:80], str(d["area"]).strip()[:60]
        rent, beds = int(d["rent"]), int(d.get("beds", 1))
        floor, desc = str(d.get("floor", "")).strip()[:10], str(d.get("description", "")).strip()[:500]
        pref = d.get("pref") if d.get("pref") in ("Family", "Bachelor", "Student", "Any") else "Any"
        phone = re.sub(r"[^0-9+\-]", "", str(d.get("phone", "")))[:16]
        photo = d.get("photo") or ""
        if not title or not area or not 500 <= rent <= 500000 or not 0 <= beds <= 10:
            raise ValueError
        if photo and (not photo.startswith("data:image/jpeg;base64,") or len(photo) > 700000):
            raise ValueError
    except (KeyError, ValueError, TypeError):
        return jsonify(error="Please fill title, area and a rent between 500 and 500000 (photo under ~500 KB)."), 400
    with db() as c:
        c.execute("INSERT INTO listings(title,area,rent,beds,floor,pref,description,phone,photo,created) VALUES(?,?,?,?,?,?,?,?,?,?)",
                  (title, area, rent, beds, floor, pref, desc, phone, photo, time.time()))
    return jsonify(ok=True)

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

def clean(t):  # models sometimes wrap the answer in a markdown code fence
    t = t.strip()
    return re.sub(r"^```[a-z]*\n|\n```$", "", t).strip()

@app.route("/api/status")
def status():
    return jsonify(model=MODEL, gemini=GEMINI_MODEL, live=bool(API_KEY))

@app.route("/api/chat", methods=["POST"])
def chat():
    d = request.get_json(force=True)
    history, message, image = d.get("history", []), (d.get("message") or "").strip(), d.get("image")
    if not API_KEY:  # demo mode so the UI always works on stage
        if history:
            return jsonify(reply='👴🏾 **Bariwala Uncle:** "হুম... গলার আওয়াজ তো ভদ্র মনে হইতেছে। BCS-এর পড়া কেমন চলে?"\n\n📊 **Uncle Approval Meter:** 45/100 🟨🟨🟨🟨⬜⬜⬜⬜⬜⬜\n**Status:** 🤔 Warming Up\n\n*(demo mode: add GEMINI_API_KEY for live Gemma)*', demo=True)
        return jsonify(reply=DEMO_REPORT + "\n*(demo mode: add GEMINI_API_KEY for live Gemma)*", demo=True)
    contents = []
    for i, t in enumerate(history):
        text = SYSTEM_PROMPT + "\n\n--- USER INPUT ---\n" + t["text"] if i == 0 and t["role"] == "user" else t["text"]
        parts = [{"text": text}]
        if t.get("image"):
            parts.append({"inline_data": {"mime_type": t["image"]["mime"], "data": t["image"]["data"]}})
        contents.append({"role": t["role"], "parts": parts})
    if history:
        parts = [{"text": message}]
    else:
        parts = [{"text": SYSTEM_PROMPT + "\n\n--- USER INPUT (MODE 1) ---\n" + (message or "Decode this To-Let sign photo.")}]
    if image:
        parts.append({"inline_data": {"mime_type": image["mime"], "data": image["data"]}})
    contents.append({"role": "user", "parts": parts})
    choice = d.get("model", "gemma")
    order = [choice] + [m for m in ("gemma", "gemini") if m != choice]  # auto-fallback to the other model
    last = ""
    for key in order[:2]:
        try:
            r = requests.post(endpoint(MODELS.get(key, MODEL)), params={"key": API_KEY}, timeout=90,
                              json={"contents": contents, "generationConfig": {"temperature": 1.0, "maxOutputTokens": 2048}})
            if r.status_code == 200:
                return jsonify(reply=clean(r.json()["candidates"][0]["content"]["parts"][0]["text"]), used=MODELS[key], fallback=key != choice)
            last = f"{MODELS[key]} {r.status_code}: {r.text[:200]}"
        except Exception as e:
            last = f"{MODELS[key]}: {e}"
    return jsonify(error=last), 502

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"\n  Basa Khuji AI  |  model: {MODEL}  |  {'LIVE' if API_KEY else 'DEMO MODE (no GEMINI_API_KEY)'}")
    print(f"  Open  http://127.0.0.1:{port}\n")
    app.run(host="0.0.0.0" if os.environ.get("PORT") else "127.0.0.1", port=port, debug=False)
