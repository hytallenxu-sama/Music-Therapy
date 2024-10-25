import flet as ft
from hashlib import sha256
from modules import *

class Admin(ft.View):
    def __init__(self, page: ft.Page):
        super(Admin, self).__init__(
            route='/settings',
            horizontal_alignment='center',
            scroll='ALWAYS'
        )
        self.page = page
        self.page.fonts = {"Fira": "content/FiraCode.ttf"}
        self.playlist: list[Song] = AudioDirectory.playlist
        self.init()

    def init(self):
        self.user = ft.TextField()
        self.password = ft.TextField(password=True, can_reveal_password=True)
        self.submitButton = ft.ElevatedButton(
            "Submit",
            on_click=self.submitInfo
        )
        self.controls = [
            navbar(self.page, 2),
            self.user,
            self.password,
            self.submitButton
        ]
        if self.page.session.contains_key("pw") and "ADMIN" in self.page.session.get("role"):
            self.goAdminPage()

    def userList(self):
        users = {}
        conn = connectDatabase()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        lines = cursor.fetchall()
        for line in lines:
            if len(line) == 3:
                users[line[0]] = [line[1], line[2]]
        conn.close()
        return users

    def submitInfo(self,e):
        print(e.control.data)
        pw=sha256(self.password.value.encode('utf-8')).hexdigest()
        users=self.userList()
        if(self.user.value in users and pw==users[self.user.value][0]):
            self.page.session.set("pw",pw)
            self.page.session.set("user",self.user.value)
            self.page.session.set("role",users[self.user.value][1])
            if(users[self.user.value][1]=="ADMIN"):
                self.goAdminPage()


    def logout(self,e):
        self.page.session.remove("pw")
        self.page.session.remove("user")
        self.init()
        self.page.update()

    def addToDatabase(self,e):
        print(e.control.data)
        return 0
        conn = connectDatabase()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO songs (song_name, artist) VALUES (?, ?)", (self.controls[0].value, self.controls[1].value))
        conn.commit()
        conn.close()
        self.goAdminPage()

    def addSongs(self)->ft.Row:
        res = ft.Row()
        res.controls=[
            ft.TextField(),
            ft.TextField(),
            ft.ElevatedButton(
                data=res,
                on_click=self.addToDatabase
            )
        ]
        return res


    def goAdminPage(self):
        # Clear all controls in the current view
        self.controls.clear()
        # Add new controls
        self.controls.append(navbar(self.page, 2))
        self.controls.append(ft.Text(f"{self.page.session.get('user')}, Welcome!", font_family="Fira", size=24))
        self.controls.append(ft.TextButton(
            content=ft.Text(
                "Log Out"
                ,font_family="Fira"
            ),
            on_click=self.logout
        ))

        #add datatables
        stats=getSongStats(self)
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Title",font_family='Fira')),
                ft.DataColumn(ft.Text("Artist",font_family='Fira')),
                ft.DataColumn(ft.Text("Times",font_family='Fira')),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(song.song_name,font_family='Fira')),
                        ft.DataCell(ft.Text(song.artist,font_family='Fira')),
                        ft.DataCell(ft.Text(str(getCounts(self,song.song_id)),font_family='Fira')),
                    ]
                ) for song in stats
            ]
        )
        self.controls.extend([table,
                              ft.Image(
                                  src_base64=returnBase64(self=self, data=getDailyData(self))
                              )
                              ])
        self.controls.append(self.addSongs())

        # Refresh the page to reflect the changes
        self.page.update()
