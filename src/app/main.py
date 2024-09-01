from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session
from app.db.session import get_db
from typing import List
from app.models import User, Magazine, Plan, Subscription
from app.views import (
    create_user,
    authenticate_user,
    UserCreate,
    UserLogin,
    UserResponse,
    MagazineResponse,
    SubscriptionResponse,
    SubscriptionCreate,
    get_magazines,
    get_plans,
    cancel_subscription,
    get_active_subscriptions_for_user,
    create_subscription,
)

app = FastAPI()


# User endpoints
@app.post("/users/register", response_model=UserCreate)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if the username or email already exists
        existing_user = (
            db.query(User)
            .filter((User.username == user.username) | (User.email == user.email))
            .first()
        )
        if existing_user:
            raise HTTPException(
                status_code=400, detail="Username or email already registered"
            )

        db_user = create_user(db, user)
        return JSONResponse(
            content={
                "message": "User created successfully",
                "user_id": db_user.id,
                "user_name": db_user.username,
            },
            status_code=201,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/users/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.email, user.password)
    if db_user:
        return {
            "message": "Login successful",
            "user_id": db_user.id,
            "user_name": db_user.name,
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")


#  api to reset password
def reset_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user:
        # Send password reset email
        return {"message": "Password reset email sent"}
    raise HTTPException(status_code=404, detail="User not found")


# Magazine and plan endpoints
@app.get("/magazines/")
def list_magazines(db: Session = Depends(get_db)):
    magazines = get_magazines(db)
    plans = get_plans(db)
    return JSONResponse(
        content={"magazines": magazines, "plans": plans},
        status_code=200,
    )


@app.post("/subscriptions/", response_model=SubscriptionResponse)
def add_subscription(subscription: SubscriptionCreate, db: Session = Depends(get_db)):
    try:
        # Create a new subscription
        return create_subscription(db=db, subscription=subscription)
    except ValueError as e:
        # Handle errors such as duplicate subscriptions or invalid references
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/subscriptions/{user_id}/", response_model=List[SubscriptionResponse])
def get_subscriptions(user_id: int, db: Session = Depends(get_db)):
    try:
        # Retrieve active subscriptions for the user
        subscriptions = get_active_subscriptions_for_user(db, user_id)
        return subscriptions
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))


@app.post("/subscriptions/{subscription_id}/cancel/")
def cancel_subscription_endpoint(subscription_id: int, db: Session = Depends(get_db)):
    try:
        # Cancel the specified subscription
        subscription = cancel_subscription(db, subscription_id)
        if subscription is None:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return JSONResponse(
            content={"message": "Subscription cancelled"}, status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
