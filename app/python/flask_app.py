from flask import Flask, request, jsonify
import os
from queue import Queue
from bot import BotFactory
from bot_utils import get_secret_value
from process_results import ProcessResults
from process_messages import ProcessMessages

app = Flask(__name__, static_url_path='')
app.config['UPLOAD_FOLDER'] = 'static/uploads'

REGION_NAME       = os.environ['AWS_DEFAULT_REGION']
TELEGRAM_APP_URL  = os.environ['TELEGRAM_APP_URL']
TELEGRAM_SECRET   = os.environ['TELEGRAM_SECRET']
SUB_DOMAIN_SECRET = os.environ['SUB_DOMAIN_SECRET']

response = get_secret_value(REGION_NAME, TELEGRAM_SECRET, 'TELEGRAM_TOKEN')
if int(response[1]) != 200:
    raise ValueError(response[0])

TELEGRAM_TOKEN = response[0]

response = get_secret_value(REGION_NAME, SUB_DOMAIN_SECRET)
if int(response[1]) != 200:
    raise ValueError(response[0])

DOMAIN_CERTIFICATE = response[0]

@app.route('/', methods=['GET'])
def index():
    return 'Ok', 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "message": "Service is up and running!"}), 200

@app.route('/ready', methods=['GET'])
def ready():
    return jsonify({"status": "ready", "message": "Service is ready!"}), 200

@app.route(f'/{TELEGRAM_TOKEN}/', methods=['POST'])
def webhook():
    req = request.get_json()
    if "message" in req:
        msg = req['message']
    elif "edited_message" in req:
        msg = req['edited_message']
    else:
        return 'No message', 400

    message_queue.put(msg)

    return 'Ok', 200

@app.route(f'/loadTest/', methods=['POST'])
def load_test():
    req = request.get_json()
    if "message" in req:
        msg = req['message']
    elif "edited_message" in req:
        msg = req['edited_message']
    else:
        return 'No message', 400

    message_queue.put(msg)

    return 'Ok', 200

if __name__ == "__main__":
    bot_factory = BotFactory(TELEGRAM_TOKEN, TELEGRAM_APP_URL, DOMAIN_CERTIFICATE)

    # Create a message queue
    message_queue = Queue()

    # Start the results and messages threads when the application starts
    results_queue_thread = ProcessResults(app, bot_factory)
    results_queue_thread.daemon = True
    results_queue_thread.start()

    messages_queue_thread = ProcessMessages(app, bot_factory, message_queue)
    messages_queue_thread.daemon = True
    messages_queue_thread.start()

    app.run(host='0.0.0.0', port=8443)
