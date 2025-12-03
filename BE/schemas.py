from pydantic import BaseModel
from datetime import date
from typing import Optional

class UserCreate(BaseModel):
    fullname: str
    email: str
    password: str
    income: float

class UserLogin(BaseModel):
    email: str
    password: str

class ExpenseBase(BaseModel):
    date: date
    category: str
    amount: float
    note: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    user_id: int

class ExpenseResponse(ExpenseBase):
    id: int

    class Config:
        from_attributes  = True
