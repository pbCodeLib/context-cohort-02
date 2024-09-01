# crud.py
from sqlalchemy.orm import Session
from app.models import User, Magazine, Plan, Subscription
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from typing import List
from datetime import date

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# User models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr


# Magazine models


class MagazineResponse(BaseModel):
    id: int
    name: str
    description: str
    base_price: int


class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    magazine_id: int
    plan_id: int
    price: float
    renewal_date: str
    is_active: bool


class SubscriptionCreate(BaseModel):
    user_id: int
    magazine_id: int
    plan_id: int
    price: float
    renewal_date: date
    is_active: bool


# create user in the database with hashed password


def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(name=user.name, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if user and pwd_context.verify(password, user.hashed_password):
        return user
    return None


def get_magazines(db: Session):
    return db.query(Magazine).all()


# Plan models
def get_plans(db: Session):
    return db.query(Plan).all()


def create_subscription(db: Session, subscription: SubscriptionCreate):
    # Check if the user already has an active subscription for the given magazine and plan
    existing_subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == subscription.user_id,
            Subscription.magazine_id == subscription.magazine_id,
            Subscription.plan_id == subscription.plan_id,
            Subscription.is_active == True,
        )
        .first()
    )

    if existing_subscription:
        raise ValueError(
            "User already has an active subscription for this magazine and plan."
        )

    # Retrieve magazine and plan
    magazine = (
        db.query(Magazine).filter(Magazine.id == subscription.magazine_id).first()
    )
    plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()

    if not magazine or not plan:
        raise ValueError("Magazine or Plan not found.")

    # Calculate the price at renewal
    price = magazine.base_price * (1 - plan.discount)

    # Create a new subscription
    db_subscription = Subscription(
        user_id=subscription.user_id,
        magazine_id=subscription.magazine_id,
        plan_id=subscription.plan_id,
        price=price,
        renewal_date=subscription.renewal_date,
        is_active=True,
    )
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription


def get_active_subscriptions_for_user(db: Session, user_id: int):
    return (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id, Subscription.is_active == True)
        .all()
    )


def cancel_subscription(db: Session, subscription_id: int):
    subscription = (
        db.query(Subscription).filter(Subscription.id == subscription_id).first()
    )
    if subscription:
        subscription.is_active = False
        db.commit()
        db.refresh(subscription)
    return subscription



