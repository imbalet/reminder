from pydantic import UUID4, BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class AccessTokenData(BaseModel):
    user_id: UUID4


class RefreshTokenData(BaseModel):
    user_id: UUID4
    jti: UUID4
