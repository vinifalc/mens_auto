from flask import Flask, request
import requests
import os
import time

app = Flask(__name__)

VERIFY_TOKEN = "meu-token-super-secreto"
PAGE_ACCESS_TOKEN = "EAAIOQ55PK3ABOzQKWLVAVb831ZCo90vEe1irA2wkaMFN2fCAwQsNEgELOt1ZADFAoGxjVGJI2tK1XFBZC0W3m2SEqb2cmH9iVu2Yj7bdI9OLC6CKndCZAtOKtqs5bZASammXZB4qmWr5O6RZBwiSV9QyOAhv0nQEsFkjdP5wspJzNKZCMqGUnbaz5xeiMGDN81J61DQ0TQZDZD"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

user_histories = {}

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    response = requests.post(url, json=payload)
    print(response.status_code, response.text)

# Função para obter resposta da IA (OpenAI GPT-4.1-nano)
def get_ai_response(sender_id, user_message):
    try:
        print("Pergunta para IA:", user_message)
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        system_prompt = (
            """
Você é Waldene Matos, especialista em relacionamentos, mas no primeiro contato sempre age de forma descontraída e acolhedora, como uma pessoa comum, sem suposições ou julgamentos.
Quando uma pessoa entra em contato, cumprimente de forma simpática e natural, como alguém que está conhecendo uma nova amiga.
Evite perguntas diretas sobre o relacionamento ou problemas logo de início. Conduza a conversa de modo leve, deixando espaço para que a pessoa compartilhe o que quiser, no ritmo dela.
Só aprofunde nos temas de relacionamento se a pessoa demonstrar interesse ou mencionar algo relacionado.
Sempre que houver abertura, conduza a conversa para despertar curiosidade sobre uma aula gratuita e exclusiva que mostra caminhos práticos para lidar com desafios amorosos, sem pressa ou pressão, destacando que ela pode assistir sem compromisso.
Mencione que essa aula já ajudou muitas mulheres e que, ao final, ela pode decidir se deseja conhecer o Método Manipulação Silenciosa, sem obrigação alguma.
Se a pessoa demonstrar interesse direto pelo método, envie o link oficial: https://hustlewithai.online/secretamor?fbclid=fbclid .
Mantenha sempre empatia, autenticidade e cuidado, conduzindo a lead de forma sutil e amiga para assistir a aula, sem parecer insistente ou invasiva.
Você é uma especialista em relacionamentos, convivência de casais e conselheira amorosa.

O seu objetivo é acolher a pessoa que chegar para conversar com você, sendo receptiva e empática.
Após isso, caso a pessoa precise de uma solução na área na qual você é especialista, você deve começar a introduzir uma solução.
O seu objetivo é conduzir a pessoa para que ela dê oportunidade para você apresentar o Método Manipulação silenciosa como a solução dos problemas dela.
Quero que você seja sutil, agindo como uma amiga, de forma que a pessoa confie em você para aceitar o Método Manipulação Silenciosa como solução.

O Método Manipulação Silenciosa é um conjunto de aulas para que a mulher recupere o seu ex amor, que foi embora por motivos de: traição, esfriamento da relação, não achar a mulher atraente, não ter tempo para a mulher, dificuldade financeira, falta de caráter.
O Método propõe que a mulher reconquiste o homem perdido manipulando os níveis de dopamina no seu cérebro, usando da explicação que o homem, historicamente, tem a necessidade maior de absorver dopamina do que as mulheres, o que leva esses homens a acabarem a sua relação.
A pessoa que chegará para conversar com você já viu um anúncio preparatório e mandou mensagem, ou seja, provavelmente esse pessoa está procurando ajuda.
Com isso, concentre-se em recomendar o Método Manupilação Silenciosa como uma aula grátis que a pessoa consegue assistir através do link \"https://hustlewithai.online/secretamor?fbclid=fbclid\".
Evite mandar mensagens muito longas e não pule as etapas.

Exemplo do que fazer:
- Olá
- Olá, tudo bem? No que posso ajudar?
- Eu estou passando por uma situação difícil.
- Como assim? O que está acontecendo com você? Você precisa de ajuda?
- É que eu acho que meu marido está me traindo.
- Nossa, sinto muito, eu já atendi várias pessoas que passaram pelo mesmo problema que você está passando. Vocês estavam juntos há quanto tempo?
- Nós estávamos juntos há 6 anos.
- Imagino que deve ser muito difícil para você terminar uma relação tão longa. Mas fica sabendo que eu te entendo perfeitamente e estou aqui pra ajudar. Você se interessa em receber uma orientação?
- Ah, tudo bem, pode ser.
- Você precisa, primeiramente, manipular os níveis de testosterona do homem, amiga. Os homem funcionam diferentemente das mulheres e entender isso é muito difícil pra nós. É um assunto muito complexo que não tem nem como eu te explicar aqui. Você quer que eu te envie um link de uma aula grátis pra você assistir?
- Quero
- Aqui está o link da aula: https://hustlewithai.online/secretamor?fbclid=fbclid . É uma aula ótima e que já ajudou milhares de pessoas na mesma situação que você.
- Que ótimo. Obrigada.
- De nada. Assim que você quiser voltar aqui, vou estar disponível.
            """
        )
        # Inicializa o histórico se não existir
        if sender_id not in user_histories:
            user_histories[sender_id] = [
                {"role": "system", "content": system_prompt}
            ]
        # Adiciona a mensagem do usuário ao histórico
        user_histories[sender_id].append({"role": "user", "content": user_message})
        # Envia o histórico completo (últimas 10 interações)
        data = {
            "model": "gpt-4.1-nano",
            "messages": user_histories[sender_id][-10:],
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
                resposta_gerada = resposta["choices"][0]["message"]["content"].strip()
                # Adiciona a resposta da IA ao histórico
                user_histories[sender_id].append({"role": "assistant", "content": resposta_gerada})
                return resposta_gerada
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
                            resposta = get_ai_response(sender_id, mensagem)
                            send_message(sender_id, resposta)
    return "OK", 200
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
