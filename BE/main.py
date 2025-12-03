from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
import models, schemas
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Quản lý chi tiêu API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email đã tồn tại")
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Đăng ký thành công", "user_id": new_user.id}

@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    user_db = db.query(models.User).filter(models.User.email == user.email).first()
    if not user_db or user_db.password != user.password:
        raise HTTPException(status_code=401, detail="Sai email hoặc mật khẩu")
    return {"message": "Đăng nhập thành công", "user_id": user_db.id, "income": user_db.income}

@app.post("/expenses")
def add_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    if expense.date > date.today():
        raise HTTPException(status_code=400, detail="Ngày chi tiêu không được lớn hơn hôm nay!")

    user = db.query(models.User).filter(models.User.id == expense.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    total_month_expense = db.query(func.sum(models.Expense.amount)).filter(
        models.Expense.user_id == expense.user_id,
        func.date_format(models.Expense.date, "%Y-%m") == expense.date.strftime("%Y-%m")
    ).scalar() or 0

    if total_month_expense + expense.amount > user.income:
        raise HTTPException(status_code=400, detail="Tổng chi tháng vượt quá thu nhập!")

    new_exp = models.Expense(**expense.dict())
    db.add(new_exp)
    db.commit()
    db.refresh(new_exp)
    return {"message": "Đã thêm chi tiêu", "id": new_exp.id}

@app.get("/expenses/{user_id}")
def get_expenses(user_id: int, db: Session = Depends(get_db)):
    data = db.query(models.Expense).filter(models.Expense.user_id == user_id).all()
    return data

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    exp = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Không tìm thấy chi tiêu")
    db.delete(exp)
    db.commit()
    return {"message": "Đã xóa thành công"}

@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, expense: schemas.ExpenseBase, db: Session = Depends(get_db)):
    db_expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Không tìm thấy chi tiêu")

    if expense.date > date.today():
        raise HTTPException(status_code=400, detail="Ngày chi tiêu không được lớn hơn hôm nay!")

    user = db.query(models.User).filter(models.User.id == db_expense.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    total_month_expense = db.query(func.sum(models.Expense.amount)).filter(
        models.Expense.user_id == db_expense.user_id,
        func.date_format(models.Expense.date, "%Y-%m") == expense.date.strftime("%Y-%m"),
        models.Expense.id != expense_id
    ).scalar() or 0

    if total_month_expense + expense.amount > user.income:
        raise HTTPException(status_code=400, detail="Tổng chi tháng vượt quá thu nhập!")

    for key, value in expense.dict().items():
        setattr(db_expense, key, value)

    db.commit()
    db.refresh(db_expense)
    return {"message": "Cập nhật thành công"}

@app.get("/expenses/{user_id}/detail")
def get_expenses_by_month(user_id: int, db: Session = Depends(get_db), year: int = None, month: int = None):
    if not year or not month or month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Thông tin tháng hoặc năm không hợp lệ.")
    
    expenses = db.query(models.Expense).filter(
        models.Expense.user_id == user_id,
        func.year(models.Expense.date) == year,
        func.month(models.Expense.date) == month
    ).all()

    if not expenses:
        raise HTTPException(status_code=404, detail="Không có chi tiêu cho tháng này.")
    
    return expenses
