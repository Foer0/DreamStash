from pwdlib import PasswordHash


passwd_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return passwd_hasher.hash(password)


def verify_password(password, hashed_password) -> bool:
    return passwd_hasher.verify(password, hashed_password)


