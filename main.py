import subprocess

from flasgger import swag_from
from flask import Blueprint, request

main = Blueprint('main', __name__)


@main.route('/split_image', methods=['GET'])
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
        result = subprocess.run(['python', "-u", 'app/split_image.py'], capture_output=True, text=True)
        return f"Script output:\n{result.stdout}\n\n{result.stderr}"
    except Exception as e:
        return str(e), 500


@main.route('/split_this_image', methods=['GET'])
@swag_from({
    'parameters': [
        {
            'name': 'cue_dir',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': ''
        }
    ],
    'responses': {
        200: {
            'description': 'Script output',
            'schema': {
                'type': 'string'
            }
        }
    }
})
def run_split_this_script():
    cue_dir = request.args.get('cue_dir')

    try:
        result = subprocess.run(['python', "-u", 'app/split_image.py', '--cue_dir', cue_dir], capture_output=True, text=True)
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
    try:
        result = subprocess.run(['python', "-u", 'app/lossless2mp3.py'], capture_output=True, text=True)
        return f"Script output:\n{result.stdout}\n\n{result.stderr}"
    except Exception as e:
        return str(e), 500


@main.route('/set_video_lang', methods=['GET'])
@swag_from({
    'parameters': [
        {
            'name': 'video_filename',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': ''
        },
        {
            'name': 'remove_subs',
            'in': 'query',
            'type': 'string',
            'required': True,
            'default': 'true',
            'description': ''
        },
        {
            'name': 'only_english_subs',
            'in': 'query',
            'type': 'string',
            'required': True,
            'default': 'true',
            'description': ''
        }

    ],
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
def set_video_lang():
    video_filename = request.args.get('video_filename')

    remove_subs = request.args.get('remove_subs', 'true')
    only_english_subs = request.args.get('only_english_subs', 'true')

    if video_filename is None or not video_filename:
        return "Missing 'input_string' parameter.", 400

    try:
        command = ['python', '-u', 'app/set_video_lang.py', video_filename, remove_subs, only_english_subs]
        result = subprocess.run(command, capture_output=True, text=True)
        return f"Script output:\n{result.stdout}\n\n{result.stderr}"
    except Exception as e:
        return str(e), 500
