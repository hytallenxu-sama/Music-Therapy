import flet as ft
from modules.tools import *
from modules.AudioDirectory import AudioDirectory
from modules.navbar import *
from modules.Song import Song

class HomePage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route='/home',
            horizontal_alignment='center',
            vertical_alignment='start',  # Align content to the top
            scroll='ADAPTIVE'  # Enable scrolling for the view
        )
        self.page = page
        self.Directory = AudioDirectory()
        self.playlist = self.Directory.playlist
        self.page.fonts = {
            "Fira": "FiraCode.ttf"
        }

        # Create a main Column to hold all content
        main_column = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,  # Space between controls
            controls=[]
        )

        # Add navbar to the main column
        self.controls.append(navbar(self.page, 0))

        # Add home logo to the main column
        main_column.controls.append(
            ft.Container(
                image_src="content/logo.png",
                width=250,
                height=250,
                alignment=ft.alignment.center
            )
        )

        # Add the "Most Played Songs" header
        main_column.controls.append(
            ft.Container(
                content=ft.Text(
                    "播放最多的歌曲",
                    size=20,
                    font_family="Fira",
                    text_align="center"
                ),
                padding=ft.padding.symmetric(vertical=10)
            )
        )

        # Create a Column for the list of songs
        self.song_list_column = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15  # Space between song rows
        )

        # Remove the fixed height and just wrap the song list column directly
        scrollable_song_list = ft.Container(
            content=self.song_list_column,
            expand=False,  # Remove expand to let the container adjust to the content height
            padding=ft.padding.symmetric(horizontal=20),
        )

        # Add the scrollable song list to the main column
        main_column.controls.append(scrollable_song_list)

        # Set the main column as the content of the view
        self.controls.append(main_column)

        # Populate the song list
        self.add_fav_to_home()

    def add_fav_to_home(self):
        self.Directory.refresh()
        songs = getSongStats(self)
        for i in range(0, len(songs), 2):
            try:
                first = songs[i]
                second = songs[i + 1] if (i + 1) < len(songs) else None
                if second:
                    song_row = self.create_song_row(first, second)
                else:
                    song_row = self.create_single_song_container(first)
                self.song_list_column.controls.append(song_row)
            except Exception as e:
                logger("ERROR", f"Error adding songs: {e}")

    def toggle_song(self, e):
        self.page.session.set("song", e.control.data)
        self.page.go('/song')

    def create_song_row(self, song1: Song, song2: Song):
        # Create containers for each song
        cont1 = self.create_song_container(song1)
        cont2 = self.create_song_container(song2)

        # Create a row containing both song containers
        song_row = ft.Row(
            controls=[cont1, cont2],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            spacing=80,
            wrap=True  # Allow wrapping if screen is narrow
        )
        return song_row

    def create_single_song_container(self, song: Song):
        # Create a single song container occupying full width
        cont = self.create_song_container(song)
        single_row = ft.Row(
            controls=[cont],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        )
        return single_row

    def create_song_container(self, song: Song):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Image(
                        src=song.img_src,
                        width=300,
                        height=300,
                        fit=ft.ImageFit.CONTAIN
                    ),
                    ft.Text(
                        f'{song.name}\n{song.artist}',
                        font_family="Fira",
                        text_align="center",
                        size=14
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            padding=10,
            border=ft.border.all(2, ft.colors.GREEN_ACCENT),
            border_radius=ft.border_radius.all(10),
            width=420,  # Fixed width to ensure consistency
            height=420,  # Fixed height to prevent stretching
            bgcolor=ft.colors.WHITE,
            on_click=self.toggle_song,
            data=song  # Store the song data for the toggle function
        )
