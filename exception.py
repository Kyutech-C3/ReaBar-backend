class GetIsbnException(Exception):
    """ISBNの取得中にエラーが発生したことを知らせる例外クラス"""
    pass

class GetBookInfoException(Exception):
    """書籍の情報取得中にエラーが発生したことを知らせる例外クラス"""
    pass

class LeadAlreadyExistsException(Exception):
    """Readにすでにデータが存在していることを知らせる例外クラス"""
    pass

class RegisterBookException(Exception):
    """書籍の登録中にエラーが発生したことを知らせる例外クラス"""
    pass

class SaveImageException(Exception):
    """画像の保存中にエラーが発生したことを知らせる例外クラス"""
    pass
