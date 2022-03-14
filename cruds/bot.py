from dotenv import load_dotenv
import os
from pathlib import Path
from pyzbar.pyzbar import decode
from PIL import Image
import requests

from linebot import (
    LineBotApi
)

load_dotenv()
YOUR_CHANNEL_ACCESS_TOKEN=os.environ.get('YOUR_CHANNEL_ACCESS_TOKEN')

GOOGLE_API=os.environ.get('GOOGLE_API')

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)

# 写真の保存
def save_img(message_id, src_img_path):
    # message_idから画像のバイナリデータを取得
    message_content = line_bot_api.get_message_content(message_id)
    with open(src_img_path, "wb") as f:
        # バイナリを1024バイトずつ書き込む
        for chunk in message_content.iter_content():
            f.write(chunk)

# 画像内のバーコードからISBNの抽出
def get_isbn_by_bar_code(src_img_path):
    # 画像ファイルの指定
    img_path = Path(rf"{src_img_path}")
    # バーコードの読取
    data = decode(Image.open(img_path))
    print(data)
    return data[1][0].decode('utf-8', 'ignore')

# ISBNから書籍情報を検索・取得
def get_book_info_by_isbn(isbn):
    # 検索リクエストURL
    req_url = GOOGLE_API + isbn
    # リクエスト
    response = requests.get(req_url)
    return response.json()