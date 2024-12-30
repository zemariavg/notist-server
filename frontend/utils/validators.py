from flask import abort, app

def validate_note(note, headers):
    def validate_fields(data, fields, data_type):
        return all(isinstance(data[field], data_type) for field in fields)
    def validate_headers(data, fields, data_type):
        return all(isinstance(data[field], data_type) for field in fields)


    if not (isinstance(note, dict) or isinstance(headers, dict)):
        print("Failed to validate note/headers type")
        print(f"type note: {type(note)}, type headers: {type(headers)}")
        abort(400, description="Invalid JSON")

    required_note_str_fields = ['title', 'iv', 'encrypted_note', 'note_tag', 'ciphered_note_key']
    required_headers_str_fields = ['req_from', 'version']

    if not (validate_fields(note, required_note_str_fields, str) or validate_headers(headers, required_headers_str_fields, str)):
        print("Failed to validate note/headers field types")
        abort(400, description="Invalid JSON")

def check_version(headers):
    if headers['version'] != '1':
        print("Create version must be 1")
        abort(400, description="Invalid JSON")
