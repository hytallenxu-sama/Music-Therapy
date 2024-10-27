import flet as ft
from hashlib import sha256
from modules import *


class Admin(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route='/settings',
            horizontal_alignment='center',
            scroll='ALWAYS'
        )
        self.page = page
        self.page.fonts = {"Fira": "content/FiraCode.ttf"}
        self.playlist: list[Song] = AudioDirectory.playlist
        self.user = None
        self.password = None
        self.submitButton = None
        self.addSongName = None
        self.addArtist = None
        self.addAudio = None
        self.addSrc = None
        self.init()

    def init(self):
        # Initialize login fields
        self.user = ft.TextField(label="Username", width=500)
        self.password = ft.TextField(label="Password", password=True, can_reveal_password=True, width=500)
        self.submitButton = ft.ElevatedButton("Submit", on_click=self.submitInfo)

        # Populate initial controls
        self.controls = [
            navbar(self.page, 2),
            ft.Container(
                content=ft.Column(
                    controls=[
                        self.user,
                        self.password,
                        self.submitButton
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                ),
                alignment=ft.alignment.center
            )
        ]

        # Check for an existing session
        if self.page.session.contains_key("pw") and "ADMIN" in self.page.session.get("role"):
            self.goAdminPage()

    def userList(self):
        try:
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
        except Exception as e:
            print(f"Database connection error: {e}")
            return {}

    def submitInfo(self, e):
        # Hash the password input
        pw = sha256(self.password.value.encode('utf-8')).hexdigest()
        users = self.userList()
        if self.user.value in users and pw == users[self.user.value][0]:
            # Store session information
            self.page.session.set("pw", pw)
            self.page.session.set("user", self.user.value)
            self.page.session.set("role", users[self.user.value][1])
            if users[self.user.value][1] == "ADMIN":
                self.goAdminPage()
        else:
            # Show an error message if authentication fails
            self.controls.append(ft.Text("Invalid Username or Password", color=ft.colors.RED))
            self.page.update()

    def logout(self, e):
        # Clear session and reinitialize login page
        self.page.session.remove("pw")
        self.page.session.remove("user")
        self.init()
        self.page.update()

    def addToDatabase(self, e):
        try:
            conn = connectDatabase()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO songs (song_name, artist, audio_path, img_src, counts) VALUES (?,?,?,?,?)",
                           (self.addSongName.value, self.addArtist.value, self.addAudio.value, self.addSrc.value, 0))
            conn.commit()
            conn.close()
            # Show a success message to the user
            self.controls.append(ft.Text("Song added successfully!", color=ft.colors.GREEN))
            self.page.update()
        except Exception as e:
            print(f"Error adding song: {e}")
            self.controls.append(ft.Text("Failed to add song. Please try again.", color=ft.colors.RED))
            self.page.update()

    def addSongsForm(self) -> ft.Column:
        # Song addition form encapsulated in a Column for neat organization
        self.addSongName = ft.TextField(label="Song Name", width=300)
        self.addArtist = ft.TextField(label="Artist", width=300)
        self.addAudio = ft.TextField(label="Audio Path", width=300)
        self.addSrc = ft.TextField(label="Image Path", width=300)

        addSongButton = ft.ElevatedButton(
            "Add Song", on_click=self.addToDatabase
        )

        song_form = ft.Column(
            controls=[
                self.addSongName,
                self.addArtist,
                self.addAudio,
                self.addSrc,
                addSongButton
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10
        )

        return song_form

    def goAdminPage(self):
        # Clear all controls and add admin-specific controls
        self.controls.clear()
        self.controls.append(navbar(self.page, 2))
        self.controls.append(
            ft.Text(f"Welcome, {self.page.session.get('user')}!", font_family="Fira", size=24)
        )
        self.controls.append(ft.TextButton(
            content=ft.Text("Log Out", font_family="Fira"),
            on_click=self.logout
        ))

        # Add datatables for song stats
        stats = getSongStats(self)
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Title", font_family='Fira')),
                ft.DataColumn(ft.Text("Artist", font_family='Fira')),
                ft.DataColumn(ft.Text("Times Played", font_family='Fira')),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(song.song_name, font_family='Fira')),
                        ft.DataCell(ft.Text(song.artist, font_family='Fira')),
                        ft.DataCell(ft.Text(str(getCounts(self, song.song_id)), font_family='Fira')),
                    ]
                ) for song in stats
            ]
        )

        # Add the data table and chart
        self.controls.append(table)
        self.controls.append(
            ft.Image(src_base64=returnBase64(self=self, data=getDailyData(self)))
        )

        # Add song addition form
        self.controls.append(self.addSongsForm())

        # Refresh the page to reflect changes
        self.page.update()

