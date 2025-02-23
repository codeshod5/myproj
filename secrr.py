from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

import jwt
from fastapi import Depends, FastAPI, HTTPException, status, Response, Request, Form
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import Field,SQLModel,create_engine,Session,select
from fastapi.middleware.cors import CORSMiddleware
import  os
from dotenv import load_dotenv

load_dotenv()
# Generate a secure secret key
# # Run: openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30




# Pydantic models
# class Token(BaseModel):
#     access_token: str
#     token_type: str

# class TokenData(BaseModel):
#     username: Optional[str] = None

class User(SQLModel):
    
    email:str=Field(index=True)
    area:str=Field(index=True)
    password:str=Field(index=True)
  
# class UserInDB(,table=True):
#     id:int|None = Field(default=None,primary_key=True)
#     hashed_password: str
class Userinfo(SQLModel,table=True):
    id:int|None = Field(default=None,primary_key=True)
    area:str
    email:str
    hashed_pass:str





DATABASE_URL1 = os.getenv("DATABASE_URL1")
engine = create_engine(DATABASE_URL1)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

origins =[
    "http://localhost:8080",
    "http://127.0.0.1:5500",
    "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development only)
    allow_methods=["*"],
    allow_credentials=True,
    allow_headers=["*"],
)


# def create_table():
#     SQLModel.metadata.create_all(engine)
# create_table()
async def get_session():
    with Session(engine) as session:
        yield session

sess = Annotated[Session,Depends(get_session)]

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_pass(plain_text:str,hashed_password:str):
    return pwd_context.verify(plain_text,hashed_password)

def create_access_token(data:dict,expires_delta:timedelta):
    to_encode = data.copy()
    expire =  datetime.now(timezone.utc)+expires_delta
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)







        
@app.post('/createe')
async def store_hashpass(form_data:User,session:sess):
    hashed_password = get_password_hash(form_data.password)
    user_info = Userinfo(
        email = form_data.email,
        area=form_data.area,
        hashed_pass=hashed_password

    )
    session.add(user_info)
    session.commit()
    session.refresh(user_info)
    access_token = create_access_token(
        data={"sub":form_data.email},
        expires_delta=timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    )
    print(access_token)
    return {"acess_token":access_token,"msg": "authenticated"}
    
  


    # return ({"hashed":hashed_password})


@app.post('/authenti')
async def authenticate_user(form_data: User, session: sess):
    user = session.exec(select(Userinfo).where(Userinfo.email == form_data.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_pass(form_data.password, user.hashed_pass):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    access_token = create_access_token(
        data={"sub":user.email},
        expires_delta=timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    )
    
    return {"acess_token":access_token,"msg": "authenticated"}


@app.get("/me")
async def get_current_user(token:str):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401,detail="invalid token")
        return {"email":email,"msg":"authicated"}
    except Exception as e:

        raise HTTPException(status_code=401,detail="EXPIRED TOKEN")





       
    
    



    

    
# Set-ExecutionPolicy Unrestricted -Scope Process




