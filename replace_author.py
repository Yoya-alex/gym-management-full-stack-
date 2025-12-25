def email_callback(email: bytes) -> bytes:
    if email == b"merouanezouaid@example.com":  # old email
        return b"yonatanalam75@gmail.com"       # your correct email
    return email

def name_callback(name: bytes) -> bytes:
    if name == b"merouanezouaid":            # old name
        return b"Yonatan"                     # your correct name
    return name
