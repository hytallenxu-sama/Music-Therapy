import flet as ft
from modules.AudioDirectory import AudioDirectory
from modules.Song import Song
from modules.Sidebar import Sidebar  # Import the Sidebar class


class PlayList(ft.View):
    def __init__(self, page: ft.Page):
        super(PlayList, self).__init__(
            route='/discover',
            horizontal_alignment='center'
        )

        self.page = page
        self.playlist: list[Song] = AudioDirectory.playlist

        # Initialize the sidebar
        self.sidebar = Sidebar(page)

        # Main content container
        self.main_content = ft.Container(
            width=self.page.window_width,
            height=self.page.window_height,
            bgcolor="#FFFED8",
            gradient=ft.LinearGradient(
                begin=ft.alignment.Alignment(-1, -1),  # Top-left
                end=ft.alignment.Alignment(1, 1),  # Bottom-right
                colors=["#FFFED8", "#D6DCFF"],  # Your gradient colors
            ),
            border_radius=ft.border_radius.only(
                top_left=35, top_right=35, bottom_left=35, bottom_right=35
            ),
            animate=ft.animation.Animation(600, ft.AnimationCurve.DECELERATE),
            animate_scale=ft.animation.Animation(400, curve="decelerate"),
            padding=ft.padding.all(20),
            content=self.create_playlist_column(),
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

    def create_playlist_column(self):
        column = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[]
        )

        # Header with menu toggle
        column.controls.append(
            ft.Row(
                alignment="spaceBetween",
                controls=[
                    ft.IconButton(
                        icon=ft.icons.MENU,
                        on_click=self.sidebar.shrink_sidebar,  # Use sidebar's shrink method
                        icon_color="black",
                    ),
                    ft.Text("PLAYLIST", size=21, weight='bold', font_family="Fira"),
                ]
            )
        )
        # Generate playlist UI
        self.song_list_column = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )
        self.gen_playlist_ui()
        column.controls.append(self.song_list_column)

        return column

    def gen_playlist_ui(self):
        """Generate the playlist UI."""
        for song in self.playlist:
            self.song_list_column.controls.append(
                self.create_song_row(
                    song_name=song.song_name,
                    artist=song.artist,
                    song=song,
                )
            )

    def create_song_row(self, song_name, artist, song: Song):
        """Create a row for a song."""
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(f"Title: {song_name}", font_family="Fira"),
                    ft.Text(artist, font_family="Fira"),
                ],
                alignment="spaceBetween",
            ),
            data=song,
            padding=10,
            on_click=self.toggle_song,
        )

    def toggle_song(self, e):
        """Handle song toggle."""
        self.page.session.set("song", e.control.data)
        self.page.go('/song')
