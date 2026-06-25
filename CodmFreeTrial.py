from flask import Flask, request, jsonify, render_template_string, redirect, session
import psycopg2
import os
import time
import random
import string
import uuid

app = Flask(__name__)
app.secret_key = "slider_super_secure_local_pass_key_12213"

# ==========================================
# DATABASE URL
# ==========================================
DATABASE_URL = os.getenv("DATABASE_URL")

# ==========================================
# ADMIN PASSWORD
# ==========================================
ADMIN_PASSWORD = "slider123"
# ==========================================
# FREE KEY LOCK
# ==========================================
FREE_KEY_ENABLED = True

# ==========================================
# DB CONNECTION FIX (IMPORTANT)
# ==========================================
def get_db_connection():
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise Exception("DATABASE_URL is missing in environment variables")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    return psycopg2.connect(db_url, sslmode="require")

# ==========================================
# INIT DB (FIXED - NO BROKEN CODE)
# ==========================================
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS free_keys_table (
            license_key TEXT PRIMARY KEY,
            hwid TEXT,
            expiry_timestamp BIGINT,
            game TEXT DEFAULT 'CODM'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS free_tokens (
            token TEXT PRIMARY KEY,
            used BOOLEAN DEFAULT FALSE,
            created_at BIGINT
        )
    """)

    # BAGONG TABLE PARA SA IP TRACKING
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ip_access_logs (
            ip_address TEXT,
            access_date TEXT,
            PRIMARY KEY (ip_address, access_date)
        )
    """)

    conn.commit()
    conn.close()
    
# ==========================================
# USER LANDING TEMPLATE (FIXED ARROW & ROW)
# ==========================================
FREE_LANDING_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Kaze Lider Mods - Registration</title>

<style>

body{
    background:#ffffff;
    color:#000000;
    font-family:sans-serif;
    padding:20px;
    margin:0;
}

.vip-link{
    font-size:20px;
    font-weight:bold;
    color:#0000ff;
    text-decoration:underline;
    display:inline-block;
    margin-bottom:25px;
}

.info-text{
    font-size:16px;
    margin-bottom:20px;
}

.pricelist-title{
    font-weight:bold;
    margin-top:15px;
    margin-bottom:10px;
    font-size:18px;
}

.price-item{
    margin:6px 0;
    font-size:16px;
}

.payment-methods{
    margin-top:15px;
    font-size:16px;
}

.divider{
    margin:20px 0;
    color:#5f6368;
}

.trial-container{
    display:flex;
    align-items:center;
    justify-content:center;
    gap:4px;
    margin-top:35px;
    flex-wrap:nowrap; 
}

.tap-here{
    background:#00a2e8;
    color:white;
    font-size:9px;
    font-weight:bold;
    padding:4px 12px 4px 6px;
    text-transform:uppercase;
    white-space:nowrap;
    display:inline-block;
    clip-path: polygon(0% 20%, 75% 20%, 75% 0%, 100% 50%, 75% 100%, 75% 80%, 0% 80%);
    animation: bounceSolidArrow 0.35s infinite alternate;
}

@keyframes bounceSolidArrow{
    0%{ transform:translateX(0); }
    100%{ transform:translateX(5px); }
}

.trial-link-btn{
    background:none;
    border:none;
    color:#008000;
    font-size:16px;
    font-weight:bold;
    text-decoration:underline;
    cursor:pointer;
    white-space:nowrap;
    padding:0;
    margin:0;
}

.temporary-text{
    color:#ff0000;
    font-size:14px;
    font-weight:bold;
    white-space:nowrap;
    margin:0;
}

</style>
</head>

<body>

<a href="https://t.me/KAZELIDERMODS/380" target="_blank" class="vip-link">
Purchase VIP, No ads, More features
</a>

<div class="info-text">

<div class="pricelist-title">
𝘒𝘌𝘠 𝘓𝘖𝘎𝘐𝘕 𝘗𝘙𝘐𝘊𝘌 :
</div>

<div class="price-line">-------------------------------------</div>

<div class="price-item">₱150  |  $2.57  •  3 Days</div>
<div class="price-item">₱300  |  $5.15  •  7 Days</div>
<div class="price-item">₱500  |  $8.58  •  15 Days</div>
<div class="price-item">₱730  |  $12.87 •  30 Days</div>
<div class="price-item">₱2,000 | Permanent Access ∞</div>

<div class="payment-methods">
GCash • PayPal • Binance • Wise
</div>

<div class="payment-methods">
DM:
<a 
href="http://t.me/phia_maganda"
target="_blank"
style="color:#0088cc;text-decoration:none;font-weight:bold;"
>
@phia_maganda
</a>
</div>

</div>

<div class="divider">
=======================================
</div>

{% if free_enabled %}

<form action="/free/process" method="POST">

<div class="trial-container">

<div class="tap-here">
TAP HERE
</div>

<button type="submit" class="trial-link-btn">
Free trial link 1.
</button>

<span class="temporary-text">
(CODM GARENA / GLOBAL)
</span>

</div>

</form>

{% else %}

<div style="
margin-top:35px;
text-align:center;
">

<div style="
color:red;
font-size:28px;
font-weight:bold;
margin-bottom:20px;
">
WALA PANG FREE KEY DITO MAG AVAIL KANA LANG!
</div>

<div style="
font-size:18px;
line-height:1.7;
">
Free trial is currently unavailable.<br>
Please wait for free access to reopen<br>
OR avail ViP access 🙂
</div>

</div>

{% endif %}

</body>
</html>
"""

# ==========================================
# KULANG NA CODE 1: FREE GENERATED KEY TEMPLATE
# ==========================================
FREE_GENERATED_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Free Key</title>
    <style>
        body { background:#ffffff; color:#000000; font-family:sans-serif; padding:20px; text-align:center; }
        .key-container { background:#f3f3f3; padding:15px; border-radius:5px; border:2px dashed #008000; display:inline-block; margin-top:20px; font-size:18px; font-weight:bold; color:#008000; word-break:break-all; }
        .btn-back { display:inline-block; margin-top:25px; padding:10px 20px; background:#00a2e8; color:white; text-decoration:none; border-radius:5px; font-weight:bold; }
    </style>
</head>
<body>
    <h2>SUCCESSFULLY GENERATED!</h2>
    <p>I-copy ang key na ito at ilagay sa iyong mod menu login:</p>
    <div class="key-container">{{ key }}</div>
    <br>
    <a href="/free" class="btn-back">Bumalik sa Home</a>
</body>
</html>
"""

# ==========================================
# KULANG NA CODE 2: ADMIN LOGIN TEMPLATE
# ==========================================
ADMIN_LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login</title>
    <style>
        body { background:#0f0f0f; color:white; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; margin:0; }
        .login-box { background:#1a1a1a; padding:30px; border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,0.5); text-align:center; width:280px; }
        input[type="password"] { width:90%; padding:10px; margin:15px 0; border:none; border-radius:5px; background:#2b2b2b; color:white; text-align:center; }
        button { background:#4caf50; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer; width:100%; font-weight:bold; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Slider Panel Login</h2>
        <form method="POST">
            <input type="password" name="password" placeholder="Enter Admin Password" required>
            <br>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
"""

# ==========================================
# ADMIN PANEL TEMPLATE
# ==========================================
ADMIN_PANEL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>

<title>Admin Panel</title>

<style>

body{
    background:#0f0f0f;
    color:white;
    font-family:sans-serif;
    padding:20px;
}

table{
    width:100%;
    border-collapse:collapse;
    margin-top:20px;
}

th, td{
    border:1px solid #333;
    padding:12px;
    text-align:center;
}

th{
    background:#1f1f1f;
}

tr:nth-child(even){
    background:#181818;
}

.delete-btn{
    background:red;
    color:white;
    padding:8px 12px;
    text-decoration:none;
    border-radius:5px;
}

.reset-btn{
    background:#2196f3;
    color:white;
    padding:8px 12px;
    text-decoration:none;
    border-radius:5px;
    margin-right:5px;
}

.logout-btn{
    background:#444;
    color:white;
    padding:10px 15px;
    text-decoration:none;
    border-radius:5px;
}

</style>

</head>

<body>

<h1>Generated Keys</h1>

<a href="/admin/logout" class="logout-btn">
Logout
</a>

<div style="margin-bottom:20px; margin-top:20px;">

<a href="/admin/free/lock"
style="
background:red;
padding:10px 15px;
color:white;
text-decoration:none;
border-radius:5px;
margin-right:10px;
">
LOCK FREE KEY
</a>

<a href="/admin/free/unlock"
style="
background:green;
padding:10px 15px;
color:white;
text-decoration:none;
border-radius:5px;
">
UNLOCK FREE KEY
</a>

</div>

<div style="
background:#1a1a1a;
padding:20px;
border-radius:10px;
margin-top:20px;
margin-bottom:25px;
">

<h2>Create Key</h2>

<form action="/admin/generate_key" method="POST">

<div style="
display:flex;
gap:10px;
flex-wrap:wrap;
align-items:center;
">

<input type="number" name="days" placeholder="Days"
style="
padding:10px;
width:90px;
border:none;
border-radius:5px;
">

<input type="number" name="hours" placeholder="Hours"
style="
padding:10px;
width:90px;
border:none;
border-radius:5px;
">

<input type="number" name="minutes" placeholder="Minutes"
style="
padding:10px;
width:90px;
border:none;
border-radius:5px;
">

<input type="text" name="custom_key" placeholder="Custom Key"
style="
padding:10px;
width:220px;
border:none;
border-radius:5px;
">

<select name="game"
style="
padding:10px;
border:none;
border-radius:5px;
">
<option value="CODM">CODM</option>
<option value="MLBB">MLBB</option>
</select>

<button type="submit"
style="
background:#4caf50;
color:white;
border:none;
padding:10px 18px;
border-radius:5px;
cursor:pointer;
">
Generate
</button>

</div>

</form>

</div>

<table>

<tr>
<th>License Key</th>
<th>HWID</th>
<th>Expiry</th>
<th>Game</th>
<th>Action</th>
</tr>

{% for key in keys %}

<tr>

<td>{{ key[0] }}</td>
<td>{{ key[1] }}</td>
<td>{{ key[2] }}</td>
<td>{{ key[3] }}</td>

<td>

<div style="
display:flex;
flex-direction:column;
gap:5px;
align-items:center;
">

<button
style="
background:#ff9800;
color:white;
border:none;
padding:8px 12px;
border-radius:5px;
cursor:pointer;
"
onclick='copyKey("{{ key[0] }}")'>
Copy Key
</button>

<a class="reset-btn"
href="/admin/reset_hwid/{{ key[0] }}">
HWID
</a>

<a class="delete-btn"
href="/admin/delete/{{ key[0] }}">
Delete
</a>

</div>

</td>

</tr>

{% endfor %}

</table>

<script>

function copyKey(key){

    navigator.clipboard.writeText(key)
    .then(function(){
        alert("Copied Key:\n\n" + key);
    })
    .catch(function(){
        prompt("Copy Key:", key);
    });

}

</script>

</body>
</html>
"""

# ==========================================
# USER ROUTES
# ==========================================
@app.route('/free')
def free_landing():

    return render_template_string(
        FREE_LANDING_TEMPLATE,
        free_enabled=FREE_KEY_ENABLED
    )

@app.route('/free/process', methods=['POST'])
def free_process_route():

    global FREE_KEY_ENABLED

    if not FREE_KEY_ENABLED:
        return '<script>alert("Free Key Locked");window.location="/free";</script>'

    if request.headers.getlist("X-Forwarded-For"):
        user_ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
    else:
        user_ip = request.remote_addr

    current_date = time.strftime("%Y-%m-%d", time.gmtime()) 

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM ip_access_logs WHERE ip_address=%s AND access_date=%s",
        (user_ip, current_date)
    )
    already_accessed = cursor.fetchone()

    if already_accessed:
        conn.close()
        return '<script>alert("You have already used your free trial for today. try again tomorrow");window.location="/free";</script>'

    try:
        cursor.execute(
            "INSERT INTO ip_access_logs (ip_address, access_date) VALUES (%s, %s)",
            (user_ip, current_date)
        )
    except psycopg2.IntegrityError:
        conn.rollback()
        conn.close()
        return '<script>alert("Masyadong mabilis lods, dahan-dahan lang.");window.location="/free";</script>'

    token = str(uuid.uuid4())

    session["free_token"] = token
    session["passed_safelink"] = False

    cursor.execute(
        "INSERT INTO free_tokens (token, used, created_at) VALUES (%s,%s,%s)",
        (token, False, int(time.time()))
    )

    conn.commit()
    conn.close()

    return redirect("https://gplinks.co/k2AXw")
    
# =========================
# RETURN ROUTE
# =========================
@app.route('/free/return')
def free_return():

    global FREE_KEY_ENABLED

    if not FREE_KEY_ENABLED:
        return '<script>alert("Free Key Locked");window.location="/free";</script>'

    token = session.get("free_token")

    if not token:
        return '<script>alert("Missing Token");window.location="/free";</script>'

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT used FROM free_tokens WHERE token=%s",
        (token,)
    )

    result = cursor.fetchone()
    conn.close()

    if not result:
        return '<script>alert("Invalid Token");window.location="/free";</script>'

    if result[0]:
        return '<script>alert("Already Used");window.location="/free";</script>'

    session["passed_safelink"] = True
    return redirect("/free/generate/direct")


# ==========================================
# FREE GENERATE KEY
# ==========================================
@app.route('/free/generate/direct')
def free_generate_direct():

    global FREE_KEY_ENABLED

    if not FREE_KEY_ENABLED:
        return '<script>alert("Free Key Locked");window.location="/free";</script>'

    if not session.get("passed_safelink"):
        return '<script>alert("Bypass pa kupal!");window.location="/free";</script>'

    token = session.get("free_token")

    if not token:
        return '<script>alert("Session Expired");window.location="/free";</script>'

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT used FROM free_tokens WHERE token=%s",
        (token,)
    )

    result = cursor.fetchone()

    if not result:
        conn.close()
        return '<script>alert("Invalid Token");window.location="/free";</script>'

    if result[0]:
        conn.close()
        return '<script>alert("Already Used");window.location="/free";</script>'

    cursor.execute(
        "UPDATE free_tokens SET used=TRUE WHERE token=%s",
        (token,)
    )

    now = int(time.time())

    new_key = "Slider_12h" + ''.join(
        random.choices(
            string.ascii_letters + string.digits,
            k=15
        )
    )

    expiry = now + (3 * 3600)

    cursor.execute(
        "INSERT INTO free_keys_table (license_key, hwid, expiry_timestamp, game) VALUES (%s,%s,%s,%s)",
        (new_key, '', expiry, 'CODM')
    )

    conn.commit()
    conn.close()

    session.pop("passed_safelink", None)
    session.pop("free_token", None)

    return render_template_string(
        FREE_GENERATED_TEMPLATE,
        key=new_key
    )

# ==========================================
# VERIFY API
# ==========================================
@app.route('/verify', methods=['POST'])
def verify_key():
    try:
        key = request.form.get('key', '').strip()
        device_id = request.form.get('device_id', '').strip()
        game = request.form.get('game', '').strip()

        if not key:
            return jsonify({"status": 1, "msg": "Invalid Key"})

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT hwid, expiry_timestamp, game FROM free_keys_table WHERE license_key = %s",
            (key,)
        )

        result = cursor.fetchone()

        if not result:
            conn.close()
            return jsonify({"status": 1, "msg": "Invalid Key"})

        saved_hwid, expiry_timestamp, db_game = result
        now = int(time.time())

        if now > expiry_timestamp:
            conn.close()
            return jsonify({"status": 3, "msg": "Key Expired"})

        if game != db_game:
            conn.close()
            return jsonify({"status": 1, "msg": "Wrong Game"})

        if saved_hwid == "":
            cursor.execute(
                "UPDATE free_keys_table SET hwid = %s WHERE license_key = %s",
                (device_id, key)
            )
            conn.commit()

        elif saved_hwid != device_id:
            conn.close()
            return jsonify({"status": 2, "msg": "Key Used On Another Device"})

        conn.close()

        return jsonify({
            "status": 0,
            "msg": "Login Success",
            "expiry": expiry_timestamp
        })

    except Exception as e:
        return jsonify({"status": 1, "msg": str(e)})
        
# ==========================================
# ADMIN LOGIN (FIXED INTERNAL SERVER ERROR)
# ==========================================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():

    if request.method == "POST":
        password = request.form.get("password")

        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin/panel")

        return "<script>alert('Wrong Password');window.location='/admin/login';</script>"

    return render_template_string(ADMIN_LOGIN_TEMPLATE)


# ==========================================
# ADMIN PANEL
# ==========================================
@app.route('/admin/panel')
def admin_panel():

    if not session.get("admin"):
        return redirect("/admin/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM free_keys_table")
    raw_keys = cursor.fetchall()

    conn.close()

    keys = []
    now = int(time.time())

    for key in raw_keys:
        remaining = key[2] - now
        if remaining <= 0:
            expiry_text = "EXPIRED"
        else:
            days = remaining // 86400
            hours = (remaining % 86400) // 3600
            minutes = (remaining % 3600) // 60
            expiry_text = f"{days}D {hours}H {minutes}M"

        keys.append((
            key[0],   
            key[1],   
            expiry_text,
            key[3]    
        ))

    return render_template_string(
        ADMIN_PANEL_TEMPLATE,
        keys=keys
    )

# ==========================================
# LOCK FREE KEY
# ==========================================
@app.route('/admin/free/lock')
def lock_free_key():
    global FREE_KEY_ENABLED
    if not session.get("admin"):
        return redirect("/admin/login")
    FREE_KEY_ENABLED = False
    return redirect("/admin/panel")

# ==========================================
# UNLOCK FREE KEY
# ==========================================
@app.route('/admin/free/unlock')
def unlock_free_key():
    global FREE_KEY_ENABLED
    if not session.get("admin"):
        return redirect("/admin/login")
    FREE_KEY_ENABLED = True
    return redirect("/admin/panel")

# ==========================================
# DELETE KEY
# ==========================================
@app.route('/admin/delete/<key>')
def delete_key(key):
    if not session.get("admin"):
        return redirect("/admin/login")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM free_keys_table WHERE license_key=%s", (key,))
    conn.commit()
    conn.close()
    return redirect("/admin/panel")
    
# ==========================================
# RESET HWID
# ==========================================
@app.route('/admin/reset_hwid/<key>')
def reset_hwid(key):
    if not session.get("admin"):
        return redirect("/admin/login")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE free_keys_table SET hwid='' WHERE license_key=%s", (key,))
    conn.commit()
    conn.close()
    return redirect("/admin/panel")

# ==========================================
# LOGOUT
# ==========================================
@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect("/admin/login")
    
# ==========================================
# ADMIN GENERATE KEY
# ==========================================
@app.route('/admin/generate_key', methods=['POST'])
def admin_generate_key():
    if not session.get("admin"):
        return redirect("/admin/login")
    try:
        days = int(request.form.get("days") or 0)
        hours = int(request.form.get("hours") or 0)
        minutes = int(request.form.get("minutes") or 0)
        game = request.form.get("game") or "CODM"

        total_seconds = ((days * 86400) + (hours * 3600) + (minutes * 60))
        if total_seconds <= 0:
            return redirect("/admin/panel")

        custom_key = request.form.get("custom_key", "").strip()
        if custom_key:
            new_key = custom_key
        else:
            new_key = "Slider_" + ''.join(random.choices(string.ascii_letters + string.digits, k=20))

        expiry = int(time.time()) + total_seconds

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO free_keys_table (license_key, hwid, expiry_timestamp, game) VALUES (%s,%s,%s,%s)",
            (new_key, '', expiry, game)
        )
        conn.commit()
        conn.close()
        return redirect("/admin/panel")
    except Exception as e:
        print(e)
        return redirect("/admin/panel")

# ==========================================
# INIT DB ON START
# ==========================================
init_db()

# ==========================================
# RUN SERVER
# ==========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
