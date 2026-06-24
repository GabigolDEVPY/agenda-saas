from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

# Initialize Fernet key
try:
    key = settings.FIELD_ENCRYPTION_KEY.encode()
    cipher_suite = Fernet(key)
except Exception as e:
    # Fallback key for testing / configuration phase
    logger.warning("FIELD_ENCRYPTION_KEY invalid or missing. Using fallback key.")
    fallback_key = Fernet.generate_key()
    cipher_suite = Fernet(fallback_key)

def encrypt_value(plain_text):
    if not plain_text:
        return plain_text
    if not isinstance(plain_text, str):
        plain_text = str(plain_text)
    encrypted_bytes = cipher_suite.encrypt(plain_text.encode('utf-8'))
    return encrypted_bytes.decode('utf-8')

def decrypt_value(cipher_text):
    if not cipher_text:
        return cipher_text
    if not isinstance(cipher_text, str):
        cipher_text = str(cipher_text)
    try:
        decrypted_bytes = cipher_suite.decrypt(cipher_text.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to decrypt value: {e}")
        return cipher_text

class EncryptedCharField(models.CharField):
    """
    A Django model field that transparently encrypts character data when writing to
    the database and decrypts it when reading.
    """
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return decrypt_value(value)

    def to_python(self, value):
        if value is None or not isinstance(value, str):
            return value
        if value.startswith('gAAAA'):
            try:
                return decrypt_value(value)
            except Exception:
                pass
        return value

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None or value == '':
            return value
        # Don't double encrypt
        if isinstance(value, str) and value.startswith('gAAAA'):
            try:
                decrypt_value(value)
                return value
            except Exception:
                pass
        return encrypt_value(value)

class EncryptedEmailField(models.EmailField):
    """
    A Django model field that transparently encrypts email data when writing to
    the database and decrypts it when reading.
    """
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return decrypt_value(value)

    def to_python(self, value):
        if value is None or not isinstance(value, str):
            return value
        if value.startswith('gAAAA'):
            try:
                return decrypt_value(value)
            except Exception:
                pass
        return value

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None or value == '':
            return value
        # Don't double encrypt
        if isinstance(value, str) and value.startswith('gAAAA'):
            try:
                decrypt_value(value)
                return value
            except Exception:
                pass
        return encrypt_value(value)
