# WhatsApp Bot con Flask e IA Cohere 🤖💬

Este proyecto es un chatbot para WhatsApp desarrollado con **Flask**, que responde automáticamente a los mensajes de los usuarios usando un **flujo personalizado de InnovastyleWeb** o una **IA conversacional de Cohere**.

### 🚀 Funcionalidades

- Webhook conectado con **WhatsApp Cloud API**
- Flujo de atención paso a paso: nombre, servicio, presupuesto, plazo, email
- Consulta de servicios disponibles
- Modo de conversación libre con **Cohere AI**
- Despliegue en **Render** gratuito
- Código limpio, seguro y listo para producción

---

### 🧠 IA Integrada con Cohere

El bot puede responder preguntas generales usando IA. Simplemente el usuario debe escribir "IA" y luego su consulta. También se activa la IA automáticamente si el mensaje no coincide con el flujo definido.

---

### 📦 Requisitos

Este bot usa Python. Las dependencias están en `requirements.txt`:

```txt
flask
requests
cohere
gunicorn


