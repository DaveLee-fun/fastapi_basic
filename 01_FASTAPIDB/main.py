from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import Optional

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DATABASE_URL = "mysql+pymysql://funcoding:funcoding@localhost/my_memo_app"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Memo(Base):
    __tablename__ = 'memo'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    content = Column(String(1000))

class MemoCreate(BaseModel):
    title: str
    content: str
    
class MemoUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None    
    
def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()
        
Base.metadata.create_all(bind=engine)


# 메모 생성
@app.post("/memos/")
async def create_user(memo: MemoCreate, db: Session = Depends(get_db)):
    new_memo = Memo(title= memo.title, content= memo.content)
    db.add(new_memo)
    db.commit()
    db.refresh(new_memo) 
    # 새로 생성된 사용자의 정보를 반환합니다.
    return {"id": new_memo.id, "title": new_memo.title, "content": new_memo. content}


# 메모 조회
@app.get("/memos/")
async def list_memos(db: Session = Depends(get_db)):
    memos = db.query(Memo).all()
    return [{'id': memo.id, 'title': memo.title, 'content': memo.content} for memo in memos]

# 메모 수정
@app.put("/memos/{memo_id}")
async def update_user(memo_id: int, memo: MemoUpdate, db: Session = Depends(get_db)):
    db_memo = db.query(Memo).filter(Memo.id == memo_id).first()
    if db_memo is None:
        return {"error": "User not found"}
    
    if memo.title is not None:
        db_memo.title = memo.title
    if memo.content is not None:
        db_memo.content = memo.content

    db.commit()
    db.refresh(db_memo)
    return {"id": db_memo.id, "title": db_memo.title, "content": db_memo.content}


# 메모 삭제
@app.delete("/memos/{memo_id}")
async def delete_user(memo_id: int, db: Session = Depends(get_db)):
    db_memo = db.query(Memo).filter(Memo.id == memo_id).first()
    if db_memo is None:
        return {"error": "Memo not found"}
    db.delete(db_memo)
    db.commit()
    return {"message": "Memo deleted"}


# 기존 라우트
@app.get('/')
async def read_root(request: Request):
    return templates.TemplateResponse('home.html', {"request": request})

@app.get('/about')
async def about():
    return {"message": "이것은 마이 메모 앱의 소개 페이지입니다."}
