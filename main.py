from flask import Flask, request, jsonify
import requests
import os
import cohere

app = Flask(__name__)

# Configuración de entorno para Render
TOKEN = os.getenv("WHATSAPP_TOKEN")  # Define esto en las ENV VARS de Render
ID_NUMERO = os.getenv("ID_NUMERO")   # Define esto también en Render
COHERE_API_KEY = os.getenv("COHERE_API_KEY")  # Define tu key de Cohere

API_URL = f"https://graph.facebook.com/v18.0/{ID_NUMERO}/messages"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

estados_usuarios = {}

def enviar_respuesta(numero, mensaje):
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": mensaje}
    }
    response = requests.post(API_URL, headers=HEADERS, json=data)
    print("Respuesta enviada:", response.status_code, response.text)

def responder_con_ia(mensaje_usuario):
    co = cohere.Client(COHERE_API_KEY)
    respuesta = co.chat(message=mensaje_usuario)
    return respuesta.text

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        return challenge if token == "token-verificacion" else "Verificación fallida"

    if request.method == "POST":
        data = request.get_json()
        try:
            for entry in data["entry"]:
                for change in entry["changes"]:
                    value = change["value"]
                    if "messages" in value:
                        message = value["messages"][0]
                        texto = message.get("text", {}).get("body")
                        numero = message["from"]

                        if numero not in estados_usuarios:
                            estados_usuarios[numero] = {"paso": 1}
                            enviar_respuesta(numero, "👋 ¡Hola! Soy el asistente de *InnovastyleWeb*. ¿Cuál es tu nombre?")
                            return jsonify({"status": "ok"}), 200

                        paso = estados_usuarios[numero]["paso"]

                        if paso == 1:
                            estados_usuarios[numero]["nombre"] = texto
                            estados_usuarios[numero]["paso"] = 2
                            enviar_respuesta(numero,
                                "👍 Gracias. ¿Qué servicio estás buscando?\n"
                                "- Diseño de página web\n"
                                "- Tienda virtual\n"
                                "- Identidad visual\n"
                                "- Mantenimiento web\n"
                                "- Otro\n"
                                "- *Ver servicios*"
                            )

                        elif paso == 2:
                            if texto.lower() == "ver servicios":
                                enviar_respuesta(numero,
                                    "👗 Servicios disponibles:\n"
                                    "✅ Diseño web profesional\n"
                                    "✅ Tiendas virtuales\n"
                                    "✅ Branding\n"
                                    "✅ Mantenimiento web\n"
                                    "✅ Automatización con IA\n\n"
                                    "Responde con el servicio que deseas."
                                )
                            else:
                                estados_usuarios[numero]["servicio"] = texto
                                estados_usuarios[numero]["paso"] = 3
                                enviar_respuesta(numero, "💰 ¿Cuál es tu presupuesto aproximado?")

                        elif paso == 3:
                            estados_usuarios[numero]["presupuesto"] = texto
                            estados_usuarios[numero]["paso"] = 4
                            enviar_respuesta(numero, "⏱️ ¿Para cuándo necesitas el servicio?")

                        elif paso == 4:
                            estados_usuarios[numero]["plazo"] = texto
                            estados_usuarios[numero]["paso"] = 5
                            enviar_respuesta(numero, "📧 ¿Cuál es tu correo electrónico?")

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
                                "Ahora puedes preguntarme cualquier cosa sobre nuestros servicios. 🤖"
                            )
                            enviar_respuesta(numero, resumen)
                            estados_usuarios[numero]["paso"] = "ia"

                        elif paso == "ia":
                            respuesta = responder_con_ia(texto)
                            enviar_respuesta(numero, respuesta)

        except Exception as e:
            print("❌ Error:", e)

        return jsonify({"status": "ok"}), 200

@app.route("/", methods=["GET"])
def home():
    return "Servidor de WhatsApp con IA y flujo activo 🚀", 200
# Necesario para Render
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

      
