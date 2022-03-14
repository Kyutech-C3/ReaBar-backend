from flask import Flask, request, abort
from dotenv import load_dotenv
from pathlib import Path
import os
from cruds.bot import save_img, get_isbn_by_bar_code, get_book_info_by_isbn

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage
)

load_dotenv()
YOUR_CHANNEL_ACCESS_TOKEN=os.environ.get('YOUR_CHANNEL_ACCESS_TOKEN')
YOUR_CHANNEL_SECRET=os.environ.get('YOUR_CHANNEL_SECRET')

SAVE_DIR=os.environ.get('SAVE_DIR')
SRC_IMG_PATH = SAVE_DIR + "/{}.jpg"

if not os.path.isdir(SAVE_DIR):
    os.mkdir(SAVE_DIR)

app = Flask(__name__, static_folder="static", static_url_path="")

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

# 画像を受け取った際の処理
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    message_id = event.message.id
    src_img_path = SRC_IMG_PATH.format(message_id)   # 保存する画像のパス

    save_img(message_id, src_img_path)   # 画像を一時保存する
    isbn = get_isbn_by_bar_code(src_img_path)   # ISBNの取得
    book_info = get_book_info_by_isbn(isbn)
    print(book_info)

    # 書籍情報を返す
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"タイトル：{book_info['items'][0]['volumeInfo']['title']}\n著者：{book_info['items'][0]['volumeInfo']['authors'][0]}")
    )
    # 一時保存していた画像を削除
    Path(SRC_IMG_PATH.format(message_id)).absolute().unlink()

if __name__ == "__main__":
    app.run()
