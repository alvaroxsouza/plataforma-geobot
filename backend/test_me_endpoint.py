import requests

# Primeiro fazer login
login_response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"email": "teste@geobot.com", "senha": "Teste@123456"}
)

if login_response.status_code == 200:
    data = login_response.json()
    token = data.get("access_token")
    print(f"✅ Login OK - Token: {token[:20]}...")
    
    # Testar endpoint /me
    me_response = requests.get(
        "http://localhost:8000/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"\n📊 Status /me: {me_response.status_code}")
    print(f"📦 Resposta:\n{me_response.json()}")
else:
    print(f"❌ Login falhou: {login_response.status_code}")
    print(login_response.text)
