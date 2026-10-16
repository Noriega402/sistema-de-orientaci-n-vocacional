from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """
    Genera el hash seguro de una contraseña.
    """

    return pwd_context.hash(password)


def verify_password(
    password: str,
    hashed_password: str
) -> bool:
    """
    Compara una contraseña ingresada
    contra el hash almacenado en PostgreSQL.
    """

    return pwd_context.verify(
        password,
        hashed_password
    )