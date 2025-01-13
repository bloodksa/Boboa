
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, send_file
import os
import json
import zipfile
import subprocess
import psutil

app = Flask(__name__)
app.secret_key = "supersecretkey"

CONFIG_FILE = "bots_config.json"
BACKUP_FOLDER = "backups"
ERROR_LOGS_FOLDER = "error_logs"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"bots": []}
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file)

def save_config(data):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def create_backup():
    os.makedirs(BACKUP_FOLDER, exist_ok=True)
    backup_file = os.path.join(BACKUP_FOLDER, "backup.zip")
    with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if os.path.exists(CONFIG_FILE):
            zipf.write(CONFIG_FILE, arcname=os.path.basename(CONFIG_FILE))
        for folder in ["uploaded_bots", ERROR_LOGS_FOLDER]:
            if os.path.exists(folder):
                for root, _, files in os.walk(folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, start=".")
                        zipf.write(file_path, arcname)
    return backup_file

@app.route('/')
def home():
    bots = load_config().get('bots', [])
    return render_template('index.html', bots=bots, system_stats=get_system_stats())

@app.route('/update-bot/<bot_name>', methods=['POST'])
def update_bot(bot_name):
    if 'file' not in request.files:
        flash("No file uploaded.", "danger")
        return redirect(url_for('home'))
    
    file = request.files['file']
    if not file.filename.endswith('.zip'):
        flash("Only ZIP files are allowed.", "danger")
        return redirect(url_for('home'))
    
    upload_folder = "uploaded_bots"
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)

    # Extract and replace bot files
    extract_folder = os.path.join(upload_folder, file.filename[:-4])
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_folder)

    # Update bot configuration
    bots = load_config().get('bots', [])
    for bot in bots:
        if bot['name'] == bot_name:
            bot['status'] = "stopped"  # Stop bot during update
            bot['entry_point'] = os.path.join(extract_folder, bot.get('entry_point', ''))
    save_config({"bots": bots})

    flash(f"Bot '{bot_name}' updated successfully!", "success")
    return redirect(url_for('home'))

@app.route('/view-errors/<bot_name>', methods=['GET'])
def view_errors(bot_name):
    error_file = os.path.join(ERROR_LOGS_FOLDER, f"{bot_name}.log")
    if os.path.exists(error_file):
        with open(error_file, 'r') as file:
            errors = file.read()
        return jsonify({"bot_name": bot_name, "errors": errors})
    else:
        return jsonify({"bot_name": bot_name, "errors": "No errors logged for this bot."})

@app.route('/backup', methods=['GET'])
def backup():
    backup_file = create_backup()
    return send_file(backup_file, as_attachment=True)

def get_system_stats():
    return {
        "cpu_usage": psutil.cpu_percent(interval=1),
        "memory_usage": psutil.virtual_memory().percent
    }

if __name__ == '__main__':
    # Create templates for rendering
    os.makedirs('templates', exist_ok=True)
    os.makedirs(ERROR_LOGS_FOLDER, exist_ok=True)
    with open('templates/index.html', 'w') as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bot Dashboard</title>
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        </head>
        <body class="container mt-5">
            <h1 class="mb-4">Bot Management Dashboard</h1>
            <div class="mb-3">
                <strong>System CPU Usage:</strong> {{ system_stats.cpu_usage }}%<br>
                <strong>System Memory Usage:</strong> {{ system_stats.memory_usage }}%
            </div>
            <a href="/backup" class="btn btn-info mb-3">Download Backup</a>
            <h2>Bot List</h2>
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Description</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for bot in bots %}
                    <tr>
                        <td>{{ bot.name }}</td>
                        <td>{{ bot.description }}</td>
                        <td>{{ bot.status }}</td>
                        <td>
                            <form action="/update-bot/{{ bot.name }}" method="post" enctype="multipart/form-data" style="display: inline-block;">
                                <input type="file" name="file" required>
                                <button type="submit" class="btn btn-primary btn-sm">Update</button>
                            </form>
                            <a href="/view-errors/{{ bot.name }}" class="btn btn-warning btn-sm">View Errors</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </body>
        </html>
        """)
    app.run(host='0.0.0.0', port=5000)
