import flet as ft
from modules.AudioDirectory import AudioDirectory
from modules.Song import Song
from modules.navbar import *
from modules.GPT import GPT
from modules.Tables import *
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
        self.db_handler = self.page.session.get('database')
        self.playlist: list[Song] = AudioDirectory.playlist
        self.init()
        self.GPT = GPT()

    def getComments(self, song_id: int):
        comments = self.db_handler.query_data(Comment, song_id=song_id)
        return [[comment.comment_id,comment.username,comment.content] for comment in comments]

    def sendComment(self,e):
        self.db_handler.insert_data(
            Comment,
            song_id=self.song_id,
            timestamp=int(time()),
            content=e.control.value,
            username=self.page.session.get("user")
        )
        self.init()
        self.page.update()
        self.db_handler.insert_data(
            Comment,
            song_id=self.song_id,
            timestamp=int(time()),
            content=self.GPT.autoReply(e.control.value),
            username="yxnulleath"
        )
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
            textVal = f'{each[1]} commented：{each[2]}'
            if self.page.session.get('role')=='ADMIN':
                textVal = f'[{each[0]}] {textVal}'
            self.controls.append(
                ft.ResponsiveRow(
                    controls=[ft.Text(value=textVal, font_family='Fira')]
                )
            )

        self.controls.append(
            ft.TextField(
                label='Comment Here',
                on_submit=self.sendComment
            )
        )
