from statistics import mode
from tkinter.messagebox import NO
from dotenv import load_dotenv
import os
from pathlib import Path
from pyzbar.pyzbar import decode
from PIL import Image
import requests
from db import models
from sqlalchemy.orm.session import Session
from datetime import datetime
import math

from schemas.api import Book
from schemas.bot import User, TotalInfo

from exception import GetIsbnException, GetBookInfoException, SaveImageException, RegisterBookException, LeadAlreadyExistsException

from linebot import (
    LineBotApi
)

YOUR_CHANNEL_ACCESS_TOKEN=os.environ.get('YOUR_CHANNEL_ACCESS_TOKEN')

GOOGLE_API=os.environ.get('GOOGLE_API')

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)

# 写真の保存
def save_img(message_id: str, src_img_path: str):
    # message_idから画像のバイナリデータを取得
    message_content = line_bot_api.get_message_content(message_id)
    try:
        with open(src_img_path, "wb") as f:
            # バイナリを1024バイトずつ書き込む
            for chunk in message_content.iter_content():
                f.write(chunk)
    except Exception as e:
        raise SaveImageException("画像の保存に失敗しました", e)
# 画像内のバーコードからISBNの抽出
def get_isbn_by_bar_code(db: Session, src_img_path: str) -> str:
    # 画像ファイルの指定
    img_path = Path(rf"{src_img_path}")
    # バーコードの読取
    data = decode(Image.open(img_path))
    print(data)
    return data[1][0].decode('utf-8', 'ignore')

# ISBNから書籍情報を検索・取得
def get_book_info_by_isbn(isbn: str) -> object:
    # 検索リクエストURL
    req_url = GOOGLE_API + isbn
    # リクエスト
    response = requests.get(req_url)
    return response.json()

# ユーザー情報の登録
def create_user(db: Session, user_id: str, user_name: str) -> User:
    user_orm = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user_orm is None:
        user_orm = models.User(
            user_id = user_id,
            name = user_name
        )

        db.add(user_orm)
        db.commit()
        db.refresh(user_orm)

    user = User.from_orm(user_orm)
    return user

# 書籍情報の登録
def book_register(db: Session, src_img_path: str, user: User) -> Book:
    isbn = get_isbn_by_bar_code(db, src_img_path)   # ISBNの取得
    if isbn is None:
        raise GetIsbnException('ISBNの取得に失敗しました', 404)

    book_orm = db.query(models.Book).filter(models.Book.isbn == isbn).first()

    if book_orm is None:
        book_info = get_book_info_by_isbn(isbn)
        print(book_info)
        if book_info is None:
            raise GetBookInfoException('書籍の情報取得に失敗しました', 404)

        book_orm = models.Book(
            isbn = isbn,
            title = book_info['items'][0]['volumeInfo']['title'],
            author = book_info['items'][0]['volumeInfo']['authors'][0],
            thumbnail_url = book_info['items'][0]['volumeInfo']['imageLinks']['smallThumbnail'],
            published_date = book_info['items'][0]['volumeInfo']['publishedDate'],
            page = book_info['items'][0]['volumeInfo']['pageCount']
        )
        
        db.add(book_orm)
        db.commit()
        db.refresh(book_orm)
    book = Book.from_orm(book_orm)


    try:
        book_user_intermediate_table_register(db, user.user_id, isbn)
    except LeadAlreadyExistsException as e:
        raise RegisterBookException('書籍の登録に失敗しました', e)
    else:
        updateReadPage(db, user.user_id, book_info['items'][0]['volumeInfo']['pageCount'])
        return book

# ユーザーと書籍の中間テーブル情報の登録
def book_user_intermediate_table_register(db: Session, user_id: str, isbn: str):
    read_orm = db.query(models.Read).filter(models.Read.user_id == user_id, models.Read.isbn == isbn).first()

    if read_orm is not None:
        raise LeadAlreadyExistsException('Readにデータがすでに存在しています', 400)
    else:
        read_orm = models.Read(
            user_id = user_id,
            isbn = isbn
        )

        db.add(read_orm)
        db.commit()
        db.refresh(read_orm)

# 統計情報の更新
def updateReadPage(db: Session, user_id: str, page: int) -> TotalInfo:
    datetime_now = datetime.now()
    read_page_orm = db.query(models.ReadPage).filter(models.ReadPage.user_id == user_id, models.ReadPage.year == datetime_now.year, models.ReadPage.month == datetime_now.month, models.ReadPage.week == datetime_now.month).first()

    if read_page_orm is not None:
        read_page_orm.pages += page
        read_page_orm.quantity += 1
    else:
        new_year_day = datetime(year=datetime_now.year, month=1, day=1)
        offset_day = new_year_day.weekday()
        read_page_orm = models.ReadPage(
            user_id = user_id,
            year = datetime_now.year,
            month = datetime_now.month,
            week = math.ceil((int(datetime_now.strftime('%j')) + offset_day) / 7),
            pages = page,
            quantity = 1
        )
        db.add(read_page_orm)
    db.commit()
    db.refresh(read_page_orm)
    read_page = TotalInfo.from_orm(read_page_orm)

    return read_page
