from flask import abort, app

def validate_note(note):
    def validate_fields(data, fields, data_type):
        return all(isinstance(data[field], data_type) for field in fields)
    
    if not isinstance(note, dict):
        print("Failed to validate note JSON")
        print(type(note))
        abort(400, description="Invalid JSON")
    
    required_note_str_fields = ['title', 'iv', 'encrypted_note', 'note_tag', 'note_key', 'req_from']
    required_note_int_fields = ['version']
    
    if not validate_fields(note, required_note_str_fields, str) or not validate_fields(note, required_note_int_fields, int):
        print("Failed to validate note JSON")
        abort(400, description="Invalid JSON")
