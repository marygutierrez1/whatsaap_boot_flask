from flask import Flask, request, jsonify
import requests
import os
import cohere

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "innovastyle123")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "EAAG...")
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "your-cohere-key")

co = cohere.Client(COHERE_API_KEY)

@app.route("/", methods=["GET"])
def home():
    return "Servidor WhatsApp con flujo e IA activo"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        token_sent = request.args.get("hub.verify_token")
        return request.args.get("hub.challenge") if token_sent == VERIFY_TOKEN else "Verification token mismatch", 403

    if request.method == "POST":
        data = request.get_json()
        if data.get("entry"):
            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages")
                    if messages:
                        for message in messages:
                            phone_number_id = value["metadata"]["phone_number_id"]
                            from_number = message["from"]
                            text = message["text"]["body"]
                            response = handle_message(text)
                            send_message(phone_number_id, from_number, response)
        return "OK", 200

def handle_message(text):
    # Flujo simple
    if "hola" in text.lower():
        return "Hola 👋, bienvenido a *InnovastyleWeb*. ¿Deseas ver nuestros servicios o hablar con la IA?"
    elif "servicios" in text.lower():
        return "Ofrecemos:
1. Diseño Web 💻
2. Tiendas virtuales 🛒
3. Bots con IA 🤖

¿Cuál te interesa?"
    elif "ia" in text.lower():
        return "Escribe lo que desees consultar y nuestra IA te ayudará 🤖"
    else:
        return consulta_ia(text)

def consulta_ia(text):
    try:
        response = co.chat(message=text)
        return response.text
    except Exception as e:
        return "Lo siento, hubo un error con la IA."

def send_message(phone_number_id, to, text):
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
