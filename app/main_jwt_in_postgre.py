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


@app.post('/login' ,response_model=TokenSchema)
def login(request: requestdetails, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email")
    hashed_pass = user.password
    if not verify_password(request.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )

    # if both pass and email are correct
    access=create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    token_db = TokenTable(user_id=user.id,
                        access_toke=access,  
                        refresh_toke=refresh, 
                        status=True  # user logged in 
                    )
    db.add(token_db)
    db.commit()
    db.refresh(token_db)
    return {
        "access_token": access,
        "refresh_token": refresh,
    }


@app.get('/getusers') # get all users from the db # used by admin
def getusers(dependencies=Depends(JWTBearer()),session: Session = Depends(get_session)):
    user = session.query(User).all()
    return user


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

@app.post('/logout')
def logout(dependencies=Depends(JWTBearer()), db: Session = Depends(get_session)): 
    #dependencies returned from class JWTBearer()
    token=dependencies  # takes token as a parameter token accessed by the user( eg jwt -> ugfhdsbfjbfjbb74323hjbjfbjdsbaf)
    payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
    user_id = payload['sub']
    token_record = db.query(TokenTable).all()
    info=[]
    # Deleting expired tokens (older than 1 day) from the database 
    for record in token_record :
        print("record",record)
        if (datetime.utcnow() - record.created_date).days >1:
            info.append(record.user_id)
    if info:
        existing_token = db.query(TokenTable).where(TokenTable.user_id.in_(info)).delete()
        db.commit()
        
    # if less then one day make it invalid
    existing_token = db.query(TokenTable).filter(TokenTable.user_id == user_id, TokenTable.access_toke==token).first()
    if existing_token:
        existing_token.status=False
        db.add(existing_token)
        db.commit()
        db.refresh(existing_token)
    return {"message":"Logout Successfully"} 


if __name__ == "__main__":
    uvicorn.run("app.main_jwt_in_postgre:app", port=5000, log_level="info", reload=True)
