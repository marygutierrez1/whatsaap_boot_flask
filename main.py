from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import os
import cohere

# Carga el archivo .env
load_dotenv()
app = Flask(__name__)

# Variables de entorno
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "maryinnova")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "EAARZBLR6Ufh8BPKaVMyRsrvEUFrmmXJrDHZCHc4qujNLORZCqWD2ITMyBJwqcDZAzEyX5pL73r7ZBgRlGf1tf9c7CIcHUCBPmptKaM8GajYzRJUerSBh00nbGsk0NMap2guQj6HSu8lYQEnjdMirC7XoD5JZCZCKpfU7Uns6NQ7sbYd5SiBVUVXffZBm9S0PdZCEjZC58beC9e9l0b1tACU8WVl7D11Nbbj831IZC893879LZBAKoQZDZD")
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "1uipgy5hyF7DgqndvZqKSv9FcWipVc66lNnLmS0E")

# Imprime para verificar (opcional)
print("VERIFY_TOKEN:", VERIFY_TOKEN)
print("ACCESS_TOKEN:", ACCESS_TOKEN)
print("COHERE_API_KEY:", COHERE_API_KEY)


# Cliente Cohere
co = cohere.Client(COHERE_API_KEY)

# Estado temporal de usuarios
user_state = {}

@app.route("/", methods=["GET"])
def home():
    return "Servidor WhatsApp con flujo e IA activo"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        token_sent = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token_sent == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Token inválido", 403

    if request.method == "POST":
        data = request.get_json()
        if data.get("entry"):
            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages")
                    if messages:
                        for message in messages:
                            phone_id = value["metadata"]["phone_number_id"]
                            from_number = message["from"]
                            text = message["text"]["body"]
                            response = manejar_flujo_usuario(from_number, text)
                            enviar_mensaje(phone_id, from_number, response)
        return "OK", 200

def manejar_flujo_usuario(user_id, text):
    text = text.strip().lower()

    # Iniciar flujo si dice "hola"
    if text == "hola":
        user_state[user_id] = {"step": "nombre"}
        return "Hola 👋, bienvenido a *InnovastyleWeb*. ¿Cuál es tu nombre?"

    if user_id in user_state:
        state = user_state[user_id]

        if state["step"] == "nombre":
            state["nombre"] = text
            state["step"] = "servicio"
            return f"Gracias {text.title()} 💬. ¿Qué servicio necesitas? (Ej: Diseño web, tienda virtual, bot con IA)"

        elif state["step"] == "servicio":
            state["servicio"] = text
            state["step"] = "presupuesto"
            return "¿Cuál es tu presupuesto estimado?"

        elif state["step"] == "presupuesto":
            state["presupuesto"] = text
            state["step"] = "plazo"
            return "¿En cuántos días necesitas el servicio?"

        elif state["step"] == "plazo":
            state["plazo"] = text
            state["step"] = "email"
            return "Por favor, proporciona tu correo electrónico 📧"

        elif state["step"] == "email":
            state["email"] = text
            resumen = (
                f"📝 *Resumen del pedido:*\n"
                f"Nombre: {state['nombre'].title()}\n"
                f"Servicio: {state['servicio']}\n"
                f"Presupuesto: {state['presupuesto']}\n"
                f"Plazo: {state['plazo']} días\n"
                f"Email: {state['email']}\n\n"
                "✅ ¡Gracias por confiar en InnovastyleWeb! Te contactaremos pronto."
            )
            del user_state[user_id]  # Limpiar estado
            return resumen

    # Opción "ver servicios"
    if "servicios" in text:
        return (
            "👗 Nuestros servicios:\n"
            "1. Diseño Web 💻\n"
            "2. Tiendas virtuales 🛒\n"
            "3. Bots con IA 🤖\n"
            "4. Branding y logos 🎨\n\n"
            "Escribe *hola* para iniciar un pedido o *IA* para hacer una consulta libre."
        )

    # Opción usar IA
    if "ia" in text:
        return "🧠 Escribe tu consulta y nuestra IA te responderá."

    # Si no está en flujo ni es comando, usar IA
    return consulta_ia(text)

def consulta_ia(texto):
    try:
        respuesta = co.chat(message=texto)
        return respuesta.text
    except Exception as e:
        return "⚠️ Ocurrió un error al consultar la IA. Intenta más tarde."

def enviar_mensaje(phone_id, to, texto):
    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": texto}
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Lanza un error si la respuesta no es 2xx
        print("Mensaje enviado correctamente:", response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar mensaje: {e}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
