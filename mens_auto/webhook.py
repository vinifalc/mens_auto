from flask import Flask, request

app = Flask(__name__)
VERIFY_TOKEN = "meu-token-super-secreto"

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
        print(data)  # Aqui você pode tratar o evento recebido
        return 'OK', 200

if __name__ == '__main__':
    app.run(port=5000)
