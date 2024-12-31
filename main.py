import flet as ft
from src import *
from modules.Database import Database

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = "smooth"
    page.session.set("user", "Anonymous")
    database = Database('sqlite:///SQLite/database.db')
    page.session.set("database", database)

    def router(route):
        page.views.clear()
        if(page.route=='/home'):
            page.views.append(HomePage(page))
        if (page.route == '/discover'):
            page.views.append(PlayList(page))
        if page.route=='/song':
            page.views.append(CurrentSong(page))
        if page.route=='/settings':
            page.views.append(Admin(page))
        if page.route=='/comments':
            page.views.append(Comments(page))
        page.update()
    page.on_route_change = router
    page.go('/home')

ft.app(target=main)