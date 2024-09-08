import os

import httpx
import dotenv
from authmiddleware.app import AuthMiddleware, Config
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_settings import BaseSettings


dotenv.load_dotenv()


class Settings(BaseSettings):
    JWT_AUDIENCE: str = ""
    JWT_ISSUER: str = ""
    HOST: str = "0.0.0.0"
    PORT: int = 8090
    RELOAD: bool = True
    AUTH_URL: str = "http://localhost:8089"
    TOKEN_URL: str = f"{AUTH_URL}/token"
    AUTHORIZE_URL: str = "http://localhost:8089/authorize"
    UNAUTHORIZED_URL: str = "http://localhost:8089/unauthorized"
    CLIENT_ID: str = "raushan"
    CLIENT_SECRET: str = "client_secret"
    SECRET_KEY: str = "secret_key"
    REDIRECT_URI: str = "http://localhost:8090/auth/callback"
    RESPONSE_TYPE: str = "code"


settings = Settings()

print(f"settings: {settings}")


config = Config(
    secret_key=settings.SECRET_KEY,
    client_id=settings.CLIENT_ID,
    client_secret=settings.CLIENT_SECRET,
    redirect_uri=settings.REDIRECT_URI,
    response_type=settings.RESPONSE_TYPE,
    authorize_url=settings.AUTHORIZE_URL,
    unauthorized_url=settings.UNAUTHORIZED_URL,
    algorithms=["HS256"],
    audience=settings.JWT_AUDIENCE,
    issuer=settings.JWT_ISSUER,
)


class TokenRequest(BaseModel):
    client_id: str
    code: str
    grant_type: str = "authorization_code"


async def get_token(code: str, client_id: str):
    payload = TokenRequest(
        code=code, client_id=client_id, grant_type="authorization_code"
    ).model_dump()

    print(f"payload: {payload}")
    async with httpx.AsyncClient() as client:
        response = await client.post(settings.TOKEN_URL, json=payload)
        return response.json()["access_token"] or None


app = FastAPI()
app.add_middleware(AuthMiddleware, get_token=get_token, config=config)


@app.get("/")
async def root():
    return {"message": "Hello World", "method": "GET"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host=settings.HOST, port=int(settings.PORT), reload=settings.RELOAD
    )
