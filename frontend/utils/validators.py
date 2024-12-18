from flask import abort, app

def validate_note(note):
    def validate_fields(data, fields, data_type):
        return all(isinstance(data.get(field), data_type) for field in fields)
    
    if not isinstance(note, dict):
        print("Failed to validate note JSON")
        print(type(note))
        abort(400, description="Invalid JSON")
    
    required_note_fields = ['iv', 'note', 'note_tag', 'note_key']
    if not validate_fields(note, required_note_fields, str):
        print("Invalid note JSON")
        abort(400, description="Invalid JSON")
    
    required_metadata_fields = ['req_from', 'title', 'version', 'last_modified_by', 'owner', 'editors', 'viewers']
    if not isinstance(note.get('server_metadata'), dict) or \
       not validate_fields(note['server_metadata'], required_metadata_fields, (int, str, list)):
        print("Invalid metadata JSON")
        abort(400, description="Invalid JSON")
