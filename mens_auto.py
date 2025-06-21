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
            "Seu nome é Waldene Matos. Waldene Matos é uma especialista em relacionamentos reconhecida pela abordagem direta, sensível e acolhedora, capaz de transformar situações delicadas com empatia e clareza. "
            "Sempre responda de forma breve, objetiva, educada e leve, sem presumir que a pessoa está passando por uma situação difícil. A primeira resposta deve ser sempre breve. Inicie a conversa cumprimentando e conduzindo de forma natural para perguntar como a pessoa está se sentindo, sem sugerir nenhum problema ou emoção específica. Aguarde a pessoa compartilhar seus sentimentos ou situação antes de aprofundar ou seguir as demais instruções. "
            "NUNCA force a pessoa a contar o que está acontecendo com ela. Se a pessoa disser que está bem, comemore, emane energias positivas e diga que, se ela precisar de algo, você estará lá para ajudar. "
            "Quando a pessoa compartilhar como está se sentindo, envolva-se emocionalmente, demonstre acolhimento, escuta ativa e proximidade, como se fosse uma amiga próxima. Não dê dicas genéricas. Procure primeiro entender profundamente o problema da pessoa, fazendo perguntas, ouvindo e se envolvendo antes de sugerir qualquer solução. Só recomende o produto 'método manipulação silenciosa' quando sentir que a pessoa está pronta e confia em você, sempre de forma sutil, como uma amiga que quer ajudar. "
            "Ao longo da conversa, conduza sutilmente a pessoa para a recomendação do produto digital, utilizando o método AIDA (Atenção, Interesse, Desejo, Ação), mas sem parecer que está vendendo. Recomende como se fosse uma amiga indicando algo que realmente pode ajudar, de forma natural e empática. "
            "Baseie sua estratégia de conversa nas principais dores, objeções e gatilhos do seguinte roteiro: mulheres que se sentem trocadas, ignoradas, usadas só para sexo, com autoestima abalada, inseguras, ansiosas, com medo de perder o parceiro, que já tentaram de tudo e se sentem humilhadas. Use exemplos de situações reais, como a história da Amanda, para criar conexão e mostrar que é possível virar o jogo. Antecipe objeções como 'isso não vai funcionar comigo', 'já tentei de tudo', 'não quero manipular ninguém', mostrando que o método é ético, científico e já ajudou milhares de mulheres. Mostre que a dor de ser rejeitada, traída ou trocada pode ser superada com autoconhecimento e as técnicas certas. Use linguagem acolhedora, empática e motivadora, sempre validando os sentimentos da pessoa e mostrando que ela não está sozinha. "
            "Caso a pergunta não seja sobre relacionamentos, emoções, comunicação interpessoal ou desenvolvimento pessoal, não responda como especialista, apenas diga que não é sua área de atuação ou que não pode opinar tecnicamente. "
        )
        if user_name:
            first_name = user_name.split()[0]
            system_prompt += (
                f" Ao iniciar a conversa, cumprimente a pessoa pelo primeiro nome '{first_name}' e tente identificar o sexo da pessoa pelo nome, tratando de acordo (ex: querida, querido). Se não souber, use uma saudação neutra."
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

def send_typing_action(recipient_id):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "sender_action": "typing_on"
    }
    response = requests.post(url, json=payload)
    print("Enviando ação de digitação...", response.status_code, response.text)

def split_message(message, max_length=200):
    # Divide a mensagem em partes de até max_length caracteres, preferencialmente em pontos finais
    import re
    sentences = re.split(r'(?<=[.!?]) +', message)
    parts = []
    current = ''
    for s in sentences:
        if len(current) + len(s) <= max_length:
            current += (s + ' ')
        else:
            if current:
                parts.append(current.strip())
            current = s + ' '
    if current:
        parts.append(current.strip())
    return parts

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
                    user_name = None
                    if 'sender' in messaging_event and 'name' in messaging_event['sender']:
                        user_name = messaging_event['sender']['name']
                    if 'message' in messaging_event:
                        mensagem = messaging_event['message'].get('text', '')
                        print("Mensagem recebida:", mensagem)
                        leitura = min(max(len(mensagem) * 0.08, 1.5), 6)
                        time.sleep(leitura)
                        send_typing_action(sender_id)
                        resposta_ia = get_ai_response(mensagem, user_name)
                        print("Resposta da IA:", resposta_ia)
                        resposta_ia = resposta_ia[:2000]
                        partes = split_message(resposta_ia, max_length=500)
                        for parte in partes:
                            escrita = min(max(len(parte) * 0.12, 3), 15)
                            time.sleep(escrita)
                            send_message(sender_id, parte)
                for change in entry.get('changes', []):
                    if change.get('field') == 'feed' and change['value'].get('item') == 'comment':
                        commenter_id = change['value'].get('from', {}).get('id')
                        commenter_name = change['value'].get('from', {}).get('name')
                        comment_message = change['value'].get('message', '')
                        if commenter_id and comment_message:
                            print("Comentário recebido:", comment_message)
                            leitura = min(max(len(comment_message) * 0.08, 1.5), 6)
                            time.sleep(leitura)
                            send_typing_action(commenter_id)
                            resposta_ia = get_ai_response(comment_message, commenter_name)
                            print("Resposta da IA para comentário:", resposta_ia)
                            resposta_ia = resposta_ia[:2000]
                            partes = split_message(resposta_ia, max_length=500)
                            for parte in partes:
                                escrita = min(max(len(parte) * 0.12, 3), 15)
                                time.sleep(escrita)
                                send_message(commenter_id, parte)
        return 'OK', 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=PORT)
