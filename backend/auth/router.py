from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from .. import crud, schemas
from ..database import get_supabase
from .utils import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter()

@router.post("/register")
def register_user(user: schemas.UserCreate, supabase: Client = Depends(get_supabase)):
    db_user = crud.get_user_by_email(supabase, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    new_user = crud.create_user(supabase=supabase, user=user, hashed_password=hashed_password)
    return new_user

@router.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: schemas.UserLogin, supabase: Client = Depends(get_supabase)):
    user = crud.get_user_by_email(supabase, email=form_data.email)
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": str(user["id"])}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def read_users_me(current_user: dict = Depends(get_current_user), supabase: Client = Depends(get_supabase)):
    user = crud.get_user(supabase, user_id=current_user["user_id"])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
