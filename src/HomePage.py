import flet as ft
from modules.tools import *
from modules.AudioDirectory import AudioDirectory
from modules.Song import Song
from modules.Sidebar import Sidebar  # Import the Sidebar class

class HomePage(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/home",
            horizontal_alignment="center",
            vertical_alignment="start",
        )
        self.page = page
        self.Directory = AudioDirectory()
        self.playlist = self.Directory.playlist
        self.page.fonts = {"Fira": "FiraCode.ttf"}

        # Initialize the sidebar
        self.sidebar = Sidebar(page)

        # Main content container with bottom-rounded end
        self.main_content = ft.Container(
            width=self.page.window_width,
            height=self.page.window_height,  # Main content spans the full view height
            bgcolor="#FFFED8",
            gradient=ft.LinearGradient(
                begin=ft.alignment.Alignment(-1, -1),  # Top-left
                end=ft.alignment.Alignment(1, 1),  # Bottom-right
                colors=["#FFFED8", "#D6DCFF"],  # Your gradient colors
            ),
            border_radius=ft.border_radius.only(
                top_left=35, top_right=35, bottom_left=35, bottom_right=35
            ),  # Add a rounded bottom
            animate=ft.animation.Animation(600, ft.AnimationCurve.DECELERATE),
            animate_scale=ft.animation.Animation(400, curve="decelerate"),
            padding=ft.padding.only(top=30, left=20, right=20),
            content=self.create_main_column(),
        )

        # Link the sidebar's main content to this page's main content
        self.sidebar.main_content = self.main_content

        # Stack to hold both the sidebar and the main content
        self.controls.append(
            ft.Stack(
                controls=[
                    self.main_content,  # Main content at the bottom layer
                    self.sidebar.sidebar,  # Sidebar on top layer
                ]
            )
        )

        # Add songs to the homepage
        self.add_fav_to_home()

    def create_main_column(self):
        PINK = "#eb06ff"

        main_column = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[]
        )

        # Header with menu toggle and notifications
        main_column.controls.append(
            ft.Row(
                alignment="spaceBetween",
                controls=[
                    ft.IconButton(
                        icon=ft.icons.MENU,
                        on_click=self.sidebar.shrink_sidebar,  # Use sidebar's shrink method
                        icon_color="black",
                    ),
                    ft.Row(
                        controls=[
                            ft.Icon(ft.icons.SEARCH, color="black"),
                            ft.Icon(ft.icons.NOTIFICATIONS_OUTLINED, color="black"),
                        ]
                    ),
                ]
            )
        )

        # Add logo to the main column
        main_column.controls.append(
            ft.Container(
                image_src="content/logo.png",
                width=250,
                height=250,
                alignment=ft.alignment.center
            )
        )

        # Add most played songs header
        main_column.controls.append(
            ft.Container(
                content=ft.Text(
                    "Most Played Songs",
                    size=20,
                    font_family="Fira",
                    text_align="center",
                    color="black",
                ),
                padding=ft.padding.symmetric(vertical=10)
            )
        )

        # Song list
        self.song_list_column = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        )

        # Add song list to main column
        main_column.controls.append(self.song_list_column)

        return main_column

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
        cont1 = self.create_song_container(song1)
        cont2 = self.create_song_container(song2)

        song_row = ft.Row(
            controls=[cont1, cont2],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            spacing=20,
            wrap=True
        )
        return song_row

    def create_single_song_container(self, song: Song):
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
                        width=150,
                        height=150,
                        fit=ft.ImageFit.CONTAIN
                    ),
                    ft.Text(
                        f'{song.name}\n{song.artist}',
                        font_family="Fira",
                        text_align="center",
                        size=14,
                        color="black",
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            padding=10,
            border=ft.border.all(2, ft.colors.PINK_ACCENT),
            border_radius=ft.border_radius.all(10),
            width=200,
            height=220,
            bgcolor=ft.colors.BLACK12,
            on_click=self.toggle_song,
            data=song
        )
