from flask import Flask, render_template, jsonify, request
from threading import Timer
import subprocess
from script import run_nginx_container
from script_odoo import run_odoo_container

app = Flask(__name__)

def stop_container_after_period(container_name, period_seconds):
    def stop_container():
        subprocess.run(["docker", "stop", container_name])
        subprocess.run(["docker", "rm", container_name])
        print(f"Container {container_name} stopped and removed after {period_seconds} seconds.")
    
    Timer(period_seconds, stop_container).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-containers', methods=['POST'])
def run_containers():
    container_type = request.args.get('type')
    period = request.args.get('period')
    
    if container_type == "nginx":
        container_name, result = run_nginx_container()
    elif container_type == "odoo":
        container_name, result = run_odoo_container()
    else:
        return jsonify(message="Invalid container type"), 400

    if container_name is None:
        return jsonify(message=result), 400  # Envoie un message d'erreur si pas de ports disponibles

    periods_in_seconds = {
        "1d": 86400,
        "1w": 604800,
        "1m": 2592000
    }
    stop_time = periods_in_seconds.get(period, 86400)
    stop_container_after_period(container_name, stop_time)

    return jsonify(message=f"Started {container_type} container on port {result} for {period}.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
