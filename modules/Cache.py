import flet as ft

class Cache:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db_handler = self.page.session.get('database')

    def storeData(self, key: str, data: object):
        self.page.session.set(key=key, value=data)

    def getData(self, key:str):
        return self.page.session.get(key)

    def isData(self, key:str):
        return self.page.session.get(key) is not None

    def clearData(self, key:str):
        if self.isData(key):
            self.page.session.remove(key)