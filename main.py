import flet as ft
from time import *

from modules.navbar import navbar
from modules.tools import *
from modules.Song import Song
from modules.AudioDirectory import AudioDirectory

from src.Admin import Admin
from src.Comments import Comments
from src.HomePage import HomePage
from src.PlayList import PlayList
from src.HomePage import HomePage
from src.CurrentSong import CurrentSong


def main(page: ft.Page):
    # page start
    page.theme_mode = ft.ThemeMode.LIGHT
    def router(route):
        page.views.clear()
        if(page.route=='/home'):
            homepage=HomePage(page)
            page.views.append(homepage)
        if (page.route == '/discover'):
            playlist = PlayList(page)
            page.views.append(playlist)
        if page.route=='/song':
            song=CurrentSong(page)
            page.views.append(song)
        if page.route=='/settings':
            page.views.append(Admin(page))
        if page.route=='/comments':
            page.views.append(Comments(page))

        page.update()

    page.on_route_change = router
    page.go('/home')


ft.app(target=main)
