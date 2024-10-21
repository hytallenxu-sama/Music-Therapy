import flet as ft
from modules import *

class HomePage(ft.View):
    def __init__(self, page: ft.Page):
        super(HomePage, self).__init__(
            route='/home',
            horizontal_alignment='center'
        )
        self.page=page
        self.controls.append(navbar(self.page,0))
        self.playlist: list[Song] = AudioDirectory.playlist
        self.page.fonts={
            "Fira":"FiraCode.ttf"
        }

        #add home logo to page
        self.controls.append(
            ft.Container(
                image_src=f"content/logo.png",
                width=250,
                height=250
            )
        )
        self.controls.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(
                            "播放最多的歌曲",
                            size=15,
                            font_family="Fira",
                        )
                    ],
                    alignment="center"
                ),
                padding=10
            )
        )
        self.add_fav_to_home()

    def add_fav_to_home(self):
        song=getSongStats(self)
        for i in range(0,len(song),2):
            try:
                first = song[i]
                second = song[i + 1]
                res = self.create_song_row(first, second)
                self.controls.append(res)
            except Exception as e:
                print(f"Error: {e}")

    def toggle_song(self, e):
        self.page.session.set("song",e.control.data)
        self.page.go('/song')


    def create_song_row(self, song: Song, song2: Song)->ft.Row:
        # Create the first container with image and text for the first song
        cont1 = ft.Container(
            content=ft.Column(
                [
                    ft.Image(src=song.img_src, expand=True),  # Adjust width/height for initial size
                    ft.Text(
                        f'{song.name}\n{song.artist}',
                        font_family="Fira",
                        text_align="center",
                        size=14  # Font size that adjusts
                    )
                ],
                alignment="center",
                horizontal_alignment="center",

            ),
            padding=10,
            border=ft.border.all(10, ft.colors.GREEN_ACCENT),
            expand=True,  # Allow the container to expand
            data=song,
            on_click=self.toggle_song
        )

        # Create the second container with image and text for the second song
        cont2 = ft.Container(
            content=ft.Column(
                [
                    ft.Image(src=song2.img_src, expand=True),  # Adjust width/height for initial size
                    ft.Text(
                        f'{song2.name}\n{song2.artist}',
                        font_family="Fira",
                        text_align="center",
                        size=14  # Font size that adjusts
                    )
                ],
                #alignment="center",
                horizontal_alignment="center"
            ),
            padding=10,
            border=ft.border.all(10, ft.colors.GREEN_ACCENT),
            expand=True,  # Allow the container to expand
            data=song2,
            on_click=self.toggle_song
        )

        # Create the row containing both containers
        content = ft.Row(
            controls=[cont1, cont2],
            alignment="SPACE_EVENLY",
            expand=True  # Allow the row to expand
        )

        # Return the containers and content row
        return content

