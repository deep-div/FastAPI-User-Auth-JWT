import jwt
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .schemas import *
from .models import User, TokenTable
from .database import Base, engine, SessionLocal
from datetime import datetime 
from .auth_bearer import JWTBearer
from functools import wraps
from .utils import create_access_token,create_refresh_token,verify_password, get_hashed_password
from .utils import ALGORITHM, JWT_SECRET_KEY, JWT_REFRESH_SECRET_KEY
from fastapi.responses import JSONResponse
import uvicorn
from fastapi import Request

app = FastAPI()

# Create tables from the models if not exists
Base.metadata.create_all(bind=engine)

# Whenever the api is hit sqlalchemy orm session starts with postgre as db and after the api return something connection close
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def register_user(user: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.query(User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_hashed_password(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )

    session.add(new_user)
    session.commit() # It saves all the changes you've made in the current database session (transaction) to the actual database permanently.
    session.refresh(new_user)

    return {"message": "User created successfully"}

@app.get("/getusers")
def get_profile(request: Request, db: Session = Depends(get_session)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Access token missing")

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    return {"id": user.id, "email": user.email, "username": user.username}


@app.post('/login')
def login_with_cookie(request: requestdetails, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.email == request.email).first()
    if user is None or not verify_password(request.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    response = JSONResponse(content={"access_token": access_token, "refresh_token": refresh_token})
    
    # Set access token in HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,       # Prevent JS access
        secure=True,         # Only send over HTTPS in production
        samesite="Lax",      # Protect against CSRF (adjust as needed)
        max_age=1800         # Optional: expires in 30 minutes
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=60 * 60 * 24 * 30  # 30 days
    )

    # You could store refresh_token too if needed
    return response


@app.post('/change-password')
def change_password(request: changepassword, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    
    if not verify_password(request.old_password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password")
    
    encrypted_password = get_hashed_password(request.new_password)
    user.password = encrypted_password
    db.commit()
    
    return {"message": "Password changed successfully"}


@app.post("/logout")
def logout():
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


if __name__ == "__main__":
    uvicorn.run("app.main_jwt_in_cookies:app", port=5000, log_level="info", reload=True)
