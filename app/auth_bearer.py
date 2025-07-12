import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import FastAPI, Depends, HTTPException,status
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .models import TokenTable
from .utils import ALGORITHM, JWT_SECRET_KEY


def decodeJWT(jwtoken: str): # convert jwt to payload # we encryted the user.id in the jwttoken while creating it in function  create_access_token
    try:
        # Decode and verify the token
        payload = jwt.decode(jwtoken, JWT_SECRET_KEY, ALGORITHM)
        return payload
    except InvalidTokenError:
        return None


# decide if token is valid or not
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        #  this line means token is extracted from the HTTP request:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request) 
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decodeJWT(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid

jwt_bearer = JWTBearer()