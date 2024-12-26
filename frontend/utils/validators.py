from flask import abort, app

def validate_fields(data, fields, data_type):
    return all(isinstance(data[field], data_type) for field in fields)
    
def validate_note_backup_req(req_data):
    if req_data is None:
        abort(400, description="Invalid JSON")
    
    if not isinstance(req_data, dict):
        abort(400, description="Invalid JSON")
    
    required_note_str_fields = ['title', 'iv', 'encrypted_note', 'note_tag', 'ciphered_note_key', 'req_from']
    required_note_int_fields = ['version']
    
    if not validate_fields(req_data, required_note_str_fields, str) or not validate_fields(req_data, required_note_int_fields, int):
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
