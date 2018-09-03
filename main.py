from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def connect():
    print ('Client Connected')

@socketio.on('update')
def update_client(times):
    

if __name__ == '__main__':
    def run_app():
        socketio.run(app, host='0.0.0.0', port=8080)
    app_thread = threading.Thread(target=run_app)
    app_thread.start()
