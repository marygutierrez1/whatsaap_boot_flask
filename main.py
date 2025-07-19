from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import cohere

# Cargar variables de entorno
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# Inicializar Flask y Cohere
app = Flask(__name__)
co = cohere.Client(COHERE_API_KEY)

# Estados por usuario
estados_usuarios = {}

# Función para enviar mensaje por WhatsApp
def enviar_respuesta(numero, mensaje):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": mensaje}
    }
    response = requests.post(url, headers=headers, json=data)
    print("✅ Respuesta enviada:", response.status_code, response.text)

# Función para responder con Cohere
def responder_con_ia(texto_usuario):
    try:
        respuesta = co.chat(
            message=texto_usuario,
            model="command-r",
            temperature=0.7
        )
        return respuesta.text.strip()
    except Exception as e:
        print("❌ Error con Cohere:", str(e))
        return "Ocurrió un error al procesar tu mensaje con IA."

# Ruta de inicio
@app.route("/")
def home():
    return "Servidor de WhatsApp con IA y flujo activo 🚀"

# Webhook de verificación
@app.route("/webhook", methods=["GET"])
def verify():
    verify_token = "mari123"
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == verify_token:
        return challenge, 200
    return "Verificación fallida", 403

# Webhook para recibir mensajes
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("📥 Webhook recibido:", data)

    # Verificar si hay mensaje entrante
    try:
        mensaje = data["entry"][0]["changes"][0]["value"]["messages"][0]
    except (KeyError, IndexError):
        return jsonify({"status": "ok"}), 200

    numero = mensaje["from"]
    texto = mensaje["text"]["body"].strip()
    print(f"🧠 Mensaje de {numero}: {texto}")

    # Flujo de preguntas
    if numero not in estados_usuarios:
        estados_usuarios[numero] = {"paso": 1}
        enviar_respuesta(numero, "👋 ¡Hola! Soy el asistente de *InnovastyleWeb*. ¿Cuál es tu nombre?")
        return jsonify({"status": "ok"}), 200

    paso = estados_usuarios[numero]["paso"]

    if paso == 1:
        estados_usuarios[numero]["nombre"] = texto
        estados_usuarios[numero]["paso"] = 2
        enviar_respuesta(numero, "👍 Gracias. ¿Qué servicio estás buscando?\n- Diseño de página web\n- Tienda virtual\n- Identidad visual\n- Mantenimiento web\n- Otro")

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
            f"🙌 ¡Gracias, {nombre}!\n"
            f"🛠 Servicio: *{servicio}*\n"
            f"💵 Presupuesto: *{presupuesto}*\n"
            f"🗓️ Plazo: *{plazo}*\n"
            f"📩 Email: *{texto}*\n\n"
            "Ahora puedes preguntarme lo que quieras sobre nuestros servicios. ¡Estoy aquí para ayudarte!"
        )
        enviar_respuesta(numero, resumen)
        estados_usuarios[numero]["paso"] = "ia"

    elif paso == "ia":
        respuesta_ia = responder_con_ia(texto)
        enviar_respuesta(numero, respuesta_ia)

    return jsonify({"status": "ok"}), 200

# Ejecutar servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
