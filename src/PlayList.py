import flet as ft
from modules.AudioDirectory import AudioDirectory
from modules.navbar import navbar
from modules.tools import *
from modules.Song import Song

class PlayList(ft.View):
    def __init__(self, page: ft.Page):
        super(PlayList, self).__init__(
            route='/discover',
            horizontal_alignment='center'
        )

        self.page = page
        self.playlist: list[Song] = AudioDirectory.playlist

        self.controls = [
            ft.Row(
                [
                    ft.Text("PLAYLIST", size=21, weight='bold',font_family="Fira")
                ],
                alignment='center'
            )
        ]
        self.controls.append(navbar(self.page,1))
        self.gen_playlist_ui()

    def gen_playlist_ui(self):
        for song in self.playlist:
            self.controls.append(
                self.create_song_row(
                    song_name=song.song_name,
                    artist=song.artist,
                    song=song,
                )
            )

    def create_song_row(self, song_name, artist, song: Song):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(f"Title: {song.name}",font_family="Fira"),
                    ft.Text(artist,font_family="Fira"),
                ],
                alignment="spaceBetween"
            ),
            data=song,
            padding=10,
            on_click=self.toggle_song
        )

    def toggle_song(self, e):
        self.page.session.set("song",e.control.data)
        self.page.go('/song')
