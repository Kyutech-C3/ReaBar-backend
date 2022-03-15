from flask import Flask, request, abort
from dotenv import load_dotenv
from pathlib import Path
import os
from db.main import get_db
from sqlalchemy.orm import Session
from schemas.bot import User
from cruds.bot import save_img, book_register, create_user
from exception import GetIsbnException, GetBookInfoException, RegisterBookException, SaveImageException

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextSendMessage, ImageMessage
)

load_dotenv()
YOUR_CHANNEL_ACCESS_TOKEN=os.environ.get('YOUR_CHANNEL_ACCESS_TOKEN')
YOUR_CHANNEL_SECRET=os.environ.get('YOUR_CHANNEL_SECRET')

db: Session = next(get_db())

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

# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(text=event.message.text)) #ここでオウム返しのメッセージを返します。

# 画像を受け取った際の処理
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    user = create_user(db, profile.user_id, profile.display_name)
    message_id = event.message.id
    src_img_path = SRC_IMG_PATH.format(message_id)   # 保存する画像のパス
    
    try:
        save_img(message_id, src_img_path)   # 画像を一時保存する
        book_info = book_register(db, src_img_path, user)
        print(book_info)
    except GetIsbnException as e:
        resText = "バーコードの読み込みに失敗しました。もう一度、全体がきれいに写るように写真を撮影してください。"
        print(e)
    except GetBookInfoException as e:
        resText = "書籍情報の取得が取得できませんでした。"
        print(e)
    except RegisterBookException as e:
        resText = "すでに同じ書籍が登録されています。"
        print(e)
    except SaveImageException as e:
        resText = "エラーが発生しました"
        print(e)
    else:
        resText = f"タイトル：{book_info.title}\n著者：{book_info.author}サムネ：{book_info.thumbnail_url}"
    finally:
        # 一時保存していた画像を削除
        Path(SRC_IMG_PATH.format(message_id)).absolute().unlink()

    # 書籍情報を返す
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=resText)
    )

if __name__ == "__main__":
    app.run(debug=True)
