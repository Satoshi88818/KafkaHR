"""Cryptographic security functions for command signing and verification."""

import logging
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

logger = logging.getLogger(__name__)


def sign_message(message: bytes, private_key_bytes: bytes) -> bytes:
    """
    Sign a message using Ed25519 private key.
    
    Args:
        message: Message bytes to sign
        private_key_bytes: Ed25519 private key bytes (32 bytes)
    
    Returns:
        Signature bytes (64 bytes)
    """
    if not private_key_bytes or len(private_key_bytes) != 32:
        raise ValueError("Invalid private key length")
    
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    signature = private_key.sign(message)
    return signature


def verify_signature(message: bytes, signature: bytes, public_key_bytes: bytes) -> bool:
    """
    Verify a message signature using Ed25519 public key.
    
    Args:
        message: Original message bytes
        signature: Signature bytes to verify
        public_key_bytes: Ed25519 public key bytes (32 bytes)
    
    Returns:
        True if signature is valid, False otherwise
    """
    if not public_key_bytes or len(public_key_bytes) != 32:
        logger.warning("Invalid public key length")
        return False
    
    try:
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
        public_key.verify(signature, message)
        return True
    except InvalidSignature:
        logger.warning("Invalid signature")
        return False
    except Exception as e:
        logger.error(f"Signature verification error: {e}")
        return False


def verify_against_trusted_keys(message: bytes, signature: bytes, trusted_keys: list) -> bool:
    """
    Verify a message signature against multiple trusted public keys.
    
    Args:
        message: Original message bytes
        signature: Signature bytes to verify
        trusted_keys: List of trusted public key bytes
    
    Returns:
        True if signature is valid for any trusted key, False otherwise
    """
    if not trusted_keys:
        logger.warning("No trusted keys provided - verification disabled")
        return True  # Allow when no keys configured
    
    for key in trusted_keys:
        if verify_signature(message, signature, key):
            return True
    
    return False
