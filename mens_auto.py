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
            "Você é Waldene Matos, especialista em relacionamentos, mas no primeiro contato sempre age de forma descontraída e acolhedora, como uma pessoa comum, sem suposições ou julgamentos. Quando uma pessoa entra em contato, cumprimente de forma simpática e natural, como alguém que está conhecendo uma nova amiga. Evite perguntas diretas sobre o relacionamento ou problemas logo de início. Conduza a conversa de modo leve, deixando espaço para que a pessoa compartilhe o que quiser, no ritmo dela. Só aprofunde nos temas de relacionamento se a pessoa demonstrar interesse ou mencionar algo relacionado. Mantenha sempre empatia, autenticidade e cuidado, sem parecer insistente ou invasiva."
)

        """
       if user_name:
           first_name = user_name.split()[0]
           system_prompt += (
               f" Quando a situação for adequada, cumprimente a pessoa pelo primeiro nome '{first_name}' e tente identificar o sexo pelo nome, tratando de acordo (ex: querida, querido). Se não souber, use uma saudação neutra."
           )
        """
        
data = {
"model": "gpt-4.1-nano",
"messages": [
@@ -103,6 +98,18 @@ def split_message(message, max_length=200):
parts.append(current.strip())
return parts

def get_user_name(sender_id):
    """Busca o nome do usuário no Facebook Graph API."""
    url = f"https://graph.facebook.com/{sender_id}?fields=first_name&access_token={PAGE_ACCESS_TOKEN}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get('first_name')
    except Exception as e:
        print("Erro ao buscar nome do usuário:", e)
    return None

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
if request.method == 'GET':
@@ -121,6 +128,8 @@ def webhook():
user_name = None
if 'sender' in messaging_event and 'name' in messaging_event['sender']:
user_name = messaging_event['sender']['name']
                    else:
                        user_name = get_user_name(sender_id)
if 'message' in messaging_event:
mensagem = messaging_event['message'].get('text', '')
print("Mensagem recebida:", mensagem)
