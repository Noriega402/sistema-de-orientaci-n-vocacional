from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):

    nombre: str = Field(
        min_length=2,
        max_length=100
    )

    correo: EmailStr

    password: str = Field(
        min_length=6,
        max_length=72
    )


class LoginRequest(BaseModel):

    correo: EmailStr

    password: str = Field(
        min_length=6,
        max_length=72
    )