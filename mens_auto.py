from flask import Flask, request
import requests

app = Flask(__name__)

VERIFY_TOKEN = "meu-token-super-secreto"
PAGE_ACCESS_TOKEN = "EAAIOQ55PK3ABOzQKWLVAVb831ZCo90vEe1irA2wkaMFN2fCAwQsNEgELOt1ZADFAoGxjVGJI2tK1XFBZC0W3m2SEqb2cmH9iVu2Yj7bdI9OLC6CKndCZAtOKtqs5bZASammXZB4qmWr5O6RZBwiSV9QyOAhv0nQEsFkjdP5wspJzNKZCMqGUnbaz5xeiMGDN81J61DQ0TQZDZD"
HUGGINGFACE_API_TOKEN = "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"

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    response = requests.post(url, json=payload)
    print(response.status_code, response.text)

# Função para obter resposta da IA (modelo open source via Hugging Face)
def get_ai_response(user_message):
    try:
        print("Pergunta para IA:", user_message)
        url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "inputs": f"[INST] {user_message} [/INST]"
        }
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print("Status Hugging Face:", response.status_code)
        print("Texto resposta HF:", response.text)
        if response.status_code == 200:
            resposta = response.json()
            print("Resposta JSON HF:", resposta)
            if isinstance(resposta, list) and len(resposta) > 0 and 'generated_text' in resposta[0]:
                return resposta[0]['generated_text'].replace('[INST]', '').replace('[/INST]', '').strip()
            elif isinstance(resposta, dict) and 'generated_text' in resposta:
                return resposta['generated_text'].replace('[INST]', '').replace('[/INST]', '').strip()
            else:
                print("Formato inesperado na resposta da IA")
                return "Desculpe, não consegui responder agora."
        else:
            print("Erro na Hugging Face:", response.status_code, response.text)
            return "Desculpe, não consegui responder agora."
    except Exception as e:
        print("Exceção ao chamar Hugging Face:", e)
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
    import os
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=PORT)
