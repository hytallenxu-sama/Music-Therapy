import flet as ft
from modules.AudioDirectory import AudioDirectory
from modules.navbar import navbar
from modules.tools import *
from modules.Song import Song
from time import *
t=localtime()
time_now=str(t.tm_year)+str(t.tm_mon)+str(t.tm_mday)

class Comments(ft.View):
    def __init__(self, page: ft.Page):
        super(Comments, self).__init__(
            route='/comments',
            horizontal_alignment='center',
            scroll='ALWAYS'
        )
        self.song_id = None
        self.page = page
        self.page.fonts = {"Fira": "FiraCode.ttf"}
        self.playlist: list[Song] = AudioDirectory.playlist
        self.init()

    def getComments(self, song_id:int):
        cursor = connectDatabase().cursor()
        cursor.execute(f"SELECT * FROM comments WHERE song_id={song_id}")
        lines = cursor.fetchall()
        file = []
        for line in lines:
            if len(line) == 3:
                file.append(line[2])
        cursor.close()
        return file

    def sendComment(self,e):
        conn=connectDatabase()
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO comments (song_id,date,content) VALUES ({self.song_id},{time_now},'{e.control.value}')")
        conn.commit()
        cursor.close()
        self.init()
        self.page.update()


    def init(self):
        self.song_id=self.page.session.get('song').song_id
        self.back_btn = ft.TextButton(
            content=ft.Text(
                "Return",
                color='black'
                , font_family="Fira"
            ),
            on_click=lambda e:self.page.go('/song'),
        )
        self.controls=[
            ft.Row(
                [self.back_btn],
                alignment='start'
            ),
            ft.Text(value=f'Welcome to No.{self.song_id}',font_family='Fira')
        ]
        comments=self.getComments(self.song_id)
        for each in comments:
            self.controls.append(
                ft.Row(
                    controls=[ft.Text(value=f'Commented：{each}', font_family='Fira')]
                )
            )

        self.controls.append(
            ft.TextField(
                label='Comment Here',
                on_submit=self.sendComment
            )
        )
