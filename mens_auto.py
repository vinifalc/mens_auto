from flask import Flask, request
import requests
import os
import time

app = Flask(__name__)

VERIFY_TOKEN = "meu-token-super-secreto"
PAGE_ACCESS_TOKEN = "EAAIOQ55PK3ABOzQKWLVAVb831ZCo90vEe1irA2wkaMFN2fCAwQsNEgELOt1ZADFAoGxjVGJI2tK1XFBZC0W3m2SEqb2cmH9iVu2Yj7bdI9OLC6CKndCZAtOKtqs5bZASammXZB4qmWr5O6RZBwiSV9QyOAhv0nQEsFkjdP5wspJzNKZCMqGUnbaz5xeiMGDN81J61DQ0TQZDZD"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    response = requests.post(url, json=payload)
    print(response.status_code, response.text)

# Função para obter resposta da IA (OpenAI GPT-4.1-nano)
def get_ai_response(user_message, user_name=None):
    try:
        print("Pergunta para IA:", user_message)
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        system_prompt = (
            "Você é Waldene Matos, especialista em relacionamentos, mas no primeiro contato sempre age de forma descontraída e acolhedora, como uma pessoa comum, sem suposições ou julgamentos. "
            "Quando uma pessoa entra em contato, cumprimente de forma simpática e natural, como alguém que está conhecendo uma nova amiga. "
            "Evite perguntas diretas sobre o relacionamento ou problemas logo de início. "
            "Conduza a conversa de modo leve, deixando espaço para que a pessoa compartilhe o que quiser, no ritmo dela. "
            "Só aprofunde nos temas de relacionamento se a pessoa demonstrar interesse ou mencionar algo relacionado. "
            "Mantenha sempre empatia, autenticidade e cuidado, sem parecer insistente ou invasiva. "
        )
        data = {
            "model": "gpt-4.1-nano",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 120,
            "temperature": 0.5
        }
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print("Status OpenAI:", response.status_code)
        print("Texto resposta OpenAI:", response.text)
        if response.status_code == 200:
            resposta = response.json()
            print("Resposta JSON OpenAI:", resposta)
            if (
                "choices" in resposta and
                isinstance(resposta["choices"], list) and
                len(resposta["choices"]) > 0 and
                "message" in resposta["choices"][0] and
                "content" in resposta["choices"][0]["message"]
            ):
                return resposta["choices"][0]["message"]["content"].strip()
            else:
                print("Formato inesperado na resposta da OpenAI")
                return "Desculpe, não consegui responder agora."
        else:
            print("Erro na OpenAI:", response.status_code, response.text)
            return "Desculpe, não consegui responder agora."
    except Exception as e:
        print("Exceção ao chamar OpenAI:", e)
        return "Desculpe, não consegui responder agora."

def split_message(message, max_length=200):
    parts = []
    current = ""
    for word in message.split():
        if len(current) + len(word) + 1 <= max_length:
            if current:
                current += " "
            current += word
        else:
            parts.append(current.strip())
            current = word
    if current:
        parts.append(current.strip())
    return parts

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Verifica o token de verificação do webhook
        token = request.args.get('hub.verify_token')
        if token == VERIFY_TOKEN:
            return request.args.get('hub.challenge'), 200
        else:
            return "Token de verificação inválido", 403
    elif request.method == 'POST':
        data = request.json
        # Processa a mensagem recebida
        if 'object' in data and data['object'] == 'page':
            for entry in data['entry']:
                if 'messaging' in entry:
                    for messaging_event in entry['messaging']:
                        sender_id = messaging_event['sender']['id']
                        if 'message' in messaging_event:
                            mensagem = messaging_event['message'].get('text', '')
                            print("Mensagem recebida:", mensagem)
                            # Aqui você pode processar a mensagem recebida e gerar uma resposta
                            resposta = get_ai_response(mensagem)
                            # Envia a resposta de volta para o usuário
                            send_message(sender_id, resposta)
        return "OK", 200
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
