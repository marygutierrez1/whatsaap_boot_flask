import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
ID_NUMERO = os.getenv("ID_NUMERO")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "miverifytoken")

estados_usuarios = {}

def enviar_respuesta(numero, mensaje):
    url = f"https://graph.facebook.com/v17.0/{ID_NUMERO}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": mensaje}
    }
    requests.post(url, headers=headers, json=data)

def responder_con_ia(mensaje):
    url = "https://api.cohere.ai/v1/chat"
    headers = {
        "Authorization": f"bearer {COHERE_API_KEY}",
        "Content-Type": "application/json",
        "Cohere-Version": "2022-12-06"
    }
    data = {
        "message": mensaje,
        "temperature": 0.9
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get("text", "No tengo una respuesta en este momento.")
    else:
        return "Ocurrió un error al procesar tu solicitud con IA."

@app.route("/", methods=["GET"])
def home():
    return "Servidor de WhatsApp con IA y flujo activo 🚀"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Verificación fallida", 403

    data = request.get_json()
    if data.get("object") == "whatsapp_business_account":
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                mensajes = value.get("messages", [])
                if mensajes:
                    mensaje = mensajes[0]
                    numero = mensaje["from"]
                    texto = mensaje["text"]["body"].strip()
                    if numero not in estados_usuarios:
                        estados_usuarios[numero] = {"paso": 1}
                        enviar_respuesta(numero, "👋 ¡Hola! Bienvenido a *InnovastyleWeb*.
Por favor, dime tu nombre para comenzar.")
                    else:
                        paso = estados_usuarios[numero]["paso"]
                        if texto.lower() == "ver servicios":
                            enviar_respuesta(numero, "📋 *Servicios disponibles:*
- Diseño de página web
- Tienda virtual
- Identidad visual
- Mantenimiento web")
                        elif paso == 1:
                            estados_usuarios[numero]["nombre"] = texto
                            estados_usuarios[numero]["paso"] = 2
                            enviar_respuesta(numero, "👍 Gracias. ¿Qué servicio estás buscando?
- Diseño de página web
- Tienda virtual
- Identidad visual
- Mantenimiento web
- Otro")
                        elif paso == 2:
                            estados_usuarios[numero]["servicio"] = texto
                            estados_usuarios[numero]["paso"] = 3
                            enviar_respuesta(numero, "💰 ¿Cuál es tu presupuesto aproximado para este servicio?")
                        elif paso == 3:
                            estados_usuarios[numero]["presupuesto"] = texto
                            estados_usuarios[numero]["paso"] = 4
                            enviar_respuesta(numero, "⏱️ ¿Para cuándo necesitas tener listo el trabajo?")
                        elif paso == 4:
                            estados_usuarios[numero]["plazo"] = texto
                            estados_usuarios[numero]["paso"] = 5
                            enviar_respuesta(numero, "📧 ¿Cuál es tu correo electrónico para enviarte una propuesta?")
                        elif paso == 5:
                            estados_usuarios[numero]["email"] = texto
                            nombre = estados_usuarios[numero]["nombre"]
                            servicio = estados_usuarios[numero]["servicio"]
                            presupuesto = estados_usuarios[numero]["presupuesto"]
                            plazo = estados_usuarios[numero]["plazo"]
                            resumen = (
                                f"🙌 ¡Gracias, {nombre}!
"
                                f"🛠 Servicio: *{servicio}*
"
                                f"💵 Presupuesto: *{presupuesto}*
"
                                f"🗓️ Plazo: *{plazo}*
"
                                f"📩 Email: *{texto}*

"
                                "Ahora puedes preguntarme lo que quieras sobre nuestros servicios. ¡Estoy aquí para ayudarte!"
                            )
                            enviar_respuesta(numero, resumen)
                            estados_usuarios[numero]["paso"] = "ia"
                        elif paso == "ia":
                            respuesta_ia = responder_con_ia(texto)
                            enviar_respuesta(numero, respuesta_ia)

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)