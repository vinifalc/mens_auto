from flask import Flask, request
import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = "meu-token-super-secreto"
PAGE_ACCESS_TOKEN = "EAAIOQ55PK3ABOzQKWLVAVb831ZCo90vEe1irA2wkaMFN2fCAwQsNEgELOt1ZADFAoGxjVGJI2tK1XFBZC0W3m2SEqb2cmH9iVu2Yj7bdI9OLC6CKndCZAtOKtqs5bZASammXZB4qmWr5O6RZBwiSV9QyOAhv0nQEsFkjdP5wspJzNKZCMqGUnbaz5xeiMGDN81J61DQ0TQZDZD"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "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")

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    response = requests.post(url, json=payload)
    print(response.status_code, response.text)

# Função para obter resposta da IA (OpenAI GPT-4.1-nano)
def get_ai_response(user_message):
    try:
        print("Pergunta para IA:", user_message)
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4.1-nano",
            "messages": [
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": user_message}
            ]
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

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if token == VERIFY_TOKEN:
            return challenge, 200
        return 'Token inválido', 403
    if request.method == 'POST':
        data = request.json
        print(data)  # Veja todo o JSON recebido para entender a estrutura
        if data.get('object') == 'page':
            for entry in data['entry']:
                for messaging_event in entry.get('messaging', []):
                    sender_id = messaging_event['sender']['id']
                    if 'message' in messaging_event:
                        mensagem = messaging_event['message'].get('text', '')
                        print("Mensagem recebida:", mensagem)
                        resposta_ia = get_ai_response(mensagem)
                        print("Resposta da IA:", resposta_ia)
                        resposta_ia = resposta_ia[:2000]
                        send_message(sender_id, resposta_ia)
                for change in entry.get('changes', []):
                    if change.get('field') == 'feed' and change['value'].get('item') == 'comment':
                        commenter_id = change['value'].get('from', {}).get('id')
                        comment_message = change['value'].get('message', '')
                        if commenter_id and comment_message:
                            print("Comentário recebido:", comment_message)
                            resposta_ia = get_ai_response(comment_message)
                            print("Resposta da IA para comentário:", resposta_ia)
                            resposta_ia = resposta_ia[:2000]
                            send_message(commenter_id, resposta_ia)
        return 'OK', 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=PORT)
