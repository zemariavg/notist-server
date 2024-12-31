from flask import abort, app

def validate_fields(data, fields, data_type):
    return all(isinstance(data[field], data_type) for field in fields)

def validate_note(note, headers):
    if not (isinstance(note, dict) or isinstance(headers, dict)):
        print("Failed to validate note/headers type")
        print(f"type note: {type(note)}, type headers: {type(headers)}")
        abort(400, description="Invalid JSON")

    required_note_str_fields = ['title', 'iv', 'encrypted_note', 'note_tag', 'ciphered_note_key']
    required_headers_str_fields = ['req_from', 'version']

    if not (validate_fields(note, required_note_str_fields, str) or validate_fields(headers, required_headers_str_fields, str)):
        print("Failed to validate note/headers field types")
        abort(400, description="Invalid JSON")

def check_version(headers):
    if headers['version'] != '1':
        print("Create version must be 1")
        abort(400, description="Invalid JSON")


def validate_add_collaborator_req(req_data):
    if req_data is None:
        abort(400, description="Invalid JSON")

    if not isinstance(req_data, dict):
        abort(400, description="Invalid JSON")

    required_str_fields = ['collaborator', 'permission']
    required_dict_fields = ['note']

    if not validate_fields(req_data, required_str_fields, str) or not validate_fields(req_data, required_dict_fields, dict):
        abort(400, description="Invalid JSON")