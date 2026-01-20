from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)

API_TOKEN = '7407~YHY2DTA7GtKKZBeBE3UB9UM8Y6rtMeCARvhQ4CzeuAwm9u4wW6ARJREWQNFmVBHy'
BASE_URL = 'https://byu.instructure.com/api/v1'

@app.before_request
def log_request():
    app.logger.info(f"Request: {request.method} {request.path}")

@app.route('/api/courses', methods=['GET', 'OPTIONS'])
def get_courses():
    app.logger.info("get_courses endpoint called")
    if request.method == 'OPTIONS':
        return '', 200
    try:
        app.logger.info("Fetching courses from Canvas API")
        response = requests.get(
            f'{BASE_URL}/courses?enrollment_state=active',
            headers={'Authorization': f'Bearer {API_TOKEN}'}
        )
        app.logger.info(f"Canvas API response status: {response.status_code}")
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        app.logger.error(f"Error fetching courses: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/courses/<int:course_id>/assignments', methods=['GET', 'OPTIONS'])
def get_assignments(course_id):
    app.logger.info(f"get_assignments endpoint called for course {course_id}")
    if request.method == 'OPTIONS':
        return '', 200
    try:
        app.logger.info(f"Fetching assignments from Canvas API for course {course_id}")
        # Fetch all assignments (not just upcoming) to include past due
        response = requests.get(
            f'{BASE_URL}/courses/{course_id}/assignments?per_page=100',
            headers={'Authorization': f'Bearer {API_TOKEN}'}
        )
        app.logger.info(f"Canvas API response status: {response.status_code}")
        response.raise_for_status()
        assignments = response.json()
        
        # Fetch all submissions at once (more efficient)
        try:
            sub_response = requests.get(
                f'{BASE_URL}/courses/{course_id}/students/submissions?per_page=100',
                headers={'Authorization': f'Bearer {API_TOKEN}'}
            )
            if sub_response.status_code == 200:
                submissions = sub_response.json()
                # Create a map of assignment_id -> submission for quick lookup
                submission_map = {sub.get('assignment_id'): sub for sub in submissions}
                
                # Add submission info to assignments
                for assignment in assignments:
                    submission = submission_map.get(assignment['id'])
                    if submission:
                        assignment['submission'] = submission
                        assignment['submitted'] = submission.get('workflow_state') in ['submitted', 'graded']
                    else:
                        assignment['submitted'] = False
            else:
                for assignment in assignments:
                    assignment['submitted'] = False
        except Exception as e:
            app.logger.warning(f"Could not fetch bulk submissions: {e}")
            for assignment in assignments:
                assignment['submitted'] = False
        
        return jsonify(assignments)
    except Exception as e:
        app.logger.error(f"Error fetching assignments for course {course_id}: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=8001, debug=True)
