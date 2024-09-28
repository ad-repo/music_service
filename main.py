import os.path

from flask import Blueprint, request
import subprocess
from flasgger import swag_from

main = Blueprint('main', __name__)

@main.route('/split_flac', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Script output',
            'schema': {
                'type': 'string'
            }
        }
    }
})
def run_split_script():
    try:
        result = subprocess.run(['python', "-u", 'app/split_flac.py'], capture_output=True, text=True)
        return f"Script output:\n{result.stdout}\n\n{result.stderr}"
    except Exception as e:
        return str(e), 500


@main.route('/lossless2mp3', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Script output',
            'schema': {
                'type': 'string'
            }
        }
    }
})
def run_mp3_script():
    print("foo", os.path.abspath(os.path.curdir))
    try:
        result = subprocess.run(['python', "-u", 'app/lossless2mp3.py'], capture_output=True, text=True)
        return f"Script output:\n{result.stdout}\n\n{result.stderr}"
    except Exception as e:
        return str(e), 500


@main.route('/video_metadata_to_location', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Script output',
            'schema': {
                'type': 'string',
            }
        },
        400: {
            'description': 'Bad Request',
        },
        500: {
            'description': 'Internal Server Error',
        }
    }
})
def run_video_metadata_to_location():
    # Get the 'input_string' query parameter
    input_string = request.args.get('input_string')

    # Get the 'include_metadata' boolean parameter (default to False if not provided)
    remove_subs = request.args.get('remove_subs', 'true').lower() in ['true', '1', 'yes']
    only_englsh_subs = request.args.get('only_englsh_subs', 'true').lower() in ['true', '1', 'yes']

    if not input_string:
        return "Missing 'input_string' parameter.", 400

    try:
        # Prepare the command for subprocess with optional include_metadata flag
        command = ['python', '-u', 'app/video_metadata_to_location.py', input_string, remove_subs, only_englsh_subs]

        # Run the script with the input string and optional flag
        result = subprocess.run(command, capture_output=True, text=True)

        return f"Script output:\n{result.stdout}\n\n{result.stderr}"
    except Exception as e:
        return str(e), 500
