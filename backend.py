from flask import Flask, request, jsonify
import os
import re
from datetime import datetime

app = Flask(__name__)

# Enable CORS manually
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Path to your HR automation script
HR_SCRIPT_PATH = "hr_automation.py"  # ← Change this to your file name!

def update_script_with_skills(skills, threshold):
    """Update REQUIRED_SKILLS and SKILL_MATCH_THRESHOLD in your script"""
    try:
        # Check if script exists
        if not os.path.exists(HR_SCRIPT_PATH):
            return False, f"Script not found: {HR_SCRIPT_PATH}"

        # Read original script
        with open(HR_SCRIPT_PATH, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update REQUIRED_SKILLS
        skills_list = '["' + '", "'.join([s.lower() for s in skills]) + '"]'
        content = re.sub(
            r'REQUIRED_SKILLS = \[.*?\]',
            f'REQUIRED_SKILLS = {skills_list}',
            content,
            flags=re.DOTALL
        )

        # Update SKILL_MATCH_THRESHOLD
        content = re.sub(
            r'SKILL_MATCH_THRESHOLD = \d+',
            f'SKILL_MATCH_THRESHOLD = {threshold}',
            content
        )

        # Write back to script
        with open(HR_SCRIPT_PATH, 'w', encoding='utf-8') as f:
            f.write(content)

        return True, f"✓ Script updated with skills: {skills} (Threshold: {threshold}%)"

    except Exception as e:
        return False, f"Error updating script: {str(e)}"


@app.route('/api/process-emails', methods=['POST', 'OPTIONS'])
def process_emails():
    """Endpoint to update skills and prepare for email processing"""
    
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()

        # Validate input
        if not data.get('skills') or len(data['skills']) == 0:
            return jsonify({
                'message': 'At least one skill is required',
                'output': ''
            }), 400

        threshold = int(data.get('threshold', 60))
        skills = [skill.strip() for skill in data['skills']]

        print(f"\n[{datetime.now()}] Processing request...")
        print(f"Skills: {skills}")
        print(f"Threshold: {threshold}%")

        # Update script with new skills
        success, message = update_script_with_skills(skills, threshold)

        if not success:
            return jsonify({
                'message': message,
                'output': message
            }), 500

        print(message)

        output = f"""
╔════════════════════════════════════════╗
║     HR AUTOMATION - EMAIL PROCESSOR    ║
╚════════════════════════════════════════╝

✓ Configuration Updated
{'=' * 40}
Required Skills: {', '.join(skills)}
Match Threshold: {threshold}%
Script Updated: {HR_SCRIPT_PATH}

{'=' * 40}
📋 Next Steps:
  1. Your {HR_SCRIPT_PATH} has been updated
  2. Skills will be used in email processing
  3. Run your script to process emails:
     
     python {HR_SCRIPT_PATH}

{'=' * 40}
 Configuration Complete!
"""

        return jsonify({
            'message': 'Configuration updated successfully',
            'skills': skills,
            'threshold': threshold,
            'output': output
        }), 200

    except Exception as e:
        error_msg = f"Server error: {str(e)}"
        print(f"[{datetime.now()}] Error: {error_msg}")
        return jsonify({
            'message': error_msg,
            'output': error_msg
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'Server is running ✓',
        'script_path': HR_SCRIPT_PATH,
        'script_exists': os.path.exists(HR_SCRIPT_PATH),
        'timestamp': datetime.now().isoformat()
    }), 200


if __name__ == '__main__':
    print("=" * 50)
    print(" HR AUTOMATION BACKEND")
    print("=" * 50)
    print(f"Script Path: {HR_SCRIPT_PATH}")
    print(f"Script Exists: {os.path.exists(HR_SCRIPT_PATH)}")
    print(f"Server: http://localhost:5000")
    print("=" * 50)
    print("Starting Flask server...")
    print("=" * 50)
    
    app.run(debug=True, host='localhost', port=5000, use_reloader=False)



# This is a demo for git hub