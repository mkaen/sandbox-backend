import uuid


def generate_uuid() -> uuid.UUID:
    """Generate a unique reference"""
    return uuid.uuid4()
