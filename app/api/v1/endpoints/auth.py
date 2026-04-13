from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.core.security import create_access_token
from app.crud.user import crud_user
from app.schemas.user import LoginRequest, Token, UserCreate, UserRead

router = APIRouter()


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = crud_user.authenticate(db, email=payload.email, password=payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return Token(access_token=create_access_token(subject=user.id))


@router.post("/register", response_model=UserRead, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if crud_user.get_by_email(db, email=payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_user.create(db, obj_in=payload)


@router.get("/me", response_model=UserRead)
def get_me(current_user=Depends(get_current_active_user)):
    return current_user
