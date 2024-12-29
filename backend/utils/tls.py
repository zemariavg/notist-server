import tempfile
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import pkcs12

def get_p12_data(p12_path: str, p12_pwd: str) -> tuple[str, str, str]:
    private_key, certificate, other_certs = pkcs12.load_key_and_certificates(
        open(p12_path, 'rb').read(), 
        p12_pwd.encode(), 
        default_backend()
    )

    with tempfile.NamedTemporaryFile(delete=False) as key_file, \
         tempfile.NamedTemporaryFile(delete=False) as cert_file:

        key_file.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ))
        key_file.flush()

        cert_file.write(certificate.public_bytes(serialization.Encoding.PEM))
        cert_file.flush()
        
    with tempfile.NamedTemporaryFile(delete=False) as other_certs_file:
        other_certs_file.write(other_certs[0].public_bytes(serialization.Encoding.PEM))

    return (cert_file.name, key_file.name, other_certs_file.name)
    
def delete_temp_files(temp_files: list):
    """Delete temporary files."""
    for temp_file in temp_files:
        try:
            os.unlink(temp_file)
            print(f"Deleted temp file: {temp_file}")
        except FileNotFoundError:
            print(f"Temp file not found (already deleted): {temp_file}")
        except Exception as e:
            print(f"Error deleting temp file {temp_file}: {e}")