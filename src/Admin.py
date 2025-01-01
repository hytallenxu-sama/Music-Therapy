import flet as ft
from modules.tools import *
from modules.AudioDirectory import AudioDirectory
from modules.Tables import *
from modules.navbar import *

import time
import threading
from concurrent.futures import ThreadPoolExecutor

class Admin(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route='/settings',
            horizontal_alignment='center',
            scroll='ADAPTIVE'
        )
        self.page = page
        self.page.fonts = {"Fira": "content/FiraCode.ttf"}
        self.db_handler = self.page.session.get('database')
        self.Directory = AudioDirectory()
        self.playlist = self.Directory.playlist
        self.executor = ThreadPoolExecutor(max_workers=10)
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
                alignment=ft.alignment.center,
                padding=ft.padding.all(20),
                border=ft.border.all(1, ft.colors.BLACK12),
                border_radius=10,
                bgcolor=ft.colors.WHITE,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.Alignment(-1, -1),  # Top-left
                    end=ft.alignment.Alignment(1, 1),  # Bottom-right
                    colors=["#FFFED8", "#D6DCFF"],  # Your gradient colors
                ),
            )
        ]

        # Check for an existing session
        if self.page.session.contains_key("pw") and "ADMIN" in self.page.session.get("role"):
            #self.addTimeStamp()
            self.goAdminPage()

    def execute_in_thread(self, func, *args, **kwargs):
        """Helper to execute tasks in a separate thread."""
        self.executor.submit(func, *args, **kwargs)

    def addTimeStamp(self):
        """Update the timestamp in the database."""
        def update_timestamp():
            self.db_handler.update_data(UserData, filters={'username': self.page.session.get("user")}, updates={'LoginTime': int(time.time())})

        # Execute in a thread
        self.execute_in_thread(update_timestamp)

    def userList(self):
        users = {}
        for user in self.db_handler.query_data(UserData):
            users[user.username] = [user.password, user.role, user.LoginTime]
        return users

    def submitInfo(self, e):
        # Hash the password input
        pw = hash(self.password.value)
        users = self.userList()
        if self.user.value in users and pw == users[self.user.value][0]:
            # Store session information
            self.page.session.set("pw", pw)
            self.page.session.set("user", self.user.value)
            self.page.session.set("role", users[self.user.value][1])
            if users[self.user.value][1] == "ADMIN":
                self.addTimeStamp()
                logger("INFO", f"{self.user.value} logged in")
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

    def removeUserFromDatabase(self, e):
        try:
            self.db_handler.delete_data(UserData, username=self.removeUser.value)
            # Show a success message in a banner
            self.page.banner = ft.Banner(
                content=ft.Text("User removed successfully!", color=ft.colors.GREEN),
                bgcolor=ft.colors.WHITE,
                actions=[
                    ft.TextButton("Close", on_click=lambda _: self.close_banner())
                ]
            )
            self.page.banner.open = True
            self.page.update()

        except Exception as e:
            logger("ERROR", f"Failed to remove user: {e}")

            # Show an error message in a banner
            self.page.banner = ft.Banner(
                content=ft.Text("Failed to remove user. Please try again.", color=ft.colors.RED),
                bgcolor=ft.colors.WHITE,
                actions=[
                    ft.TextButton("Close", on_click=lambda _: self.close_banner())
                ]
            )
            self.page.banner.open = True
            self.page.update()

    def removeSongFromDatabase(self, e):
        try:
            self.db_handler.delete_data(Songs, song_name=self.removeSong.value)

            # Show a success message in a banner
            self.page.banner = ft.Banner(
                content=ft.Text("Song removed successfully!", color=ft.colors.GREEN),
                bgcolor=ft.colors.WHITE,
                actions=[
                    ft.TextButton("Close", on_click=lambda _: self.close_banner())
                ]
            )
            self.page.banner.open = True
            self.page.update()

        except Exception as e:
            logger("ERROR", f"Failed to remove song: {e}")

            # Show an error message in a banner
            self.page.banner = ft.Banner(
                content=ft.Text("Failed to remove song. Please try again.", color=ft.colors.RED),
                bgcolor=ft.colors.WHITE,
                actions=[
                    ft.TextButton("Close", on_click=lambda _: self.close_banner())
                ]
            )
            self.page.banner.open = True
            self.page.update()

    def removeItemsForm(self) -> ft.Card:
        self.removeUser = ft.TextField(label="Username to Remove", width=250)
        self.removeSong = ft.TextField(label="Song Name to Remove", width=250)

        removeUserButton = ft.ElevatedButton("Remove User", on_click=self.removeUserFromDatabase)
        removeSongButton = ft.ElevatedButton("Remove Song", on_click=self.removeSongFromDatabase)

        remove_form = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Remove User or Song", size=18, weight="bold", font_family="Fira"),
                        self.removeUser,
                        removeUserButton,
                        self.removeSong,
                        removeSongButton
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10
                ),
                padding=ft.padding.all(15),
                gradient=ft.LinearGradient(
                    begin=ft.alignment.Alignment(-1, -1),  # Top-left
                    end=ft.alignment.Alignment(1, 1),  # Bottom-right
                    colors=["#FFFED8", "#D6DCFF"],  # Your gradient colors
                ),
            ),
            elevation=5
        )
        return remove_form

    def addSongToDatabase(self, e):
        try:
            self.db_handler.insert_data(Songs, song_name=self.addSongName.value, artist=self.addArtist.value, audio_path = self.addAudio.value, img_src = self.addSrc.value, counts=0)
            # Show a success message to the user
            self.controls.append(ft.Text("Song added successfully!", color=ft.colors.GREEN))
            self.page.update()
        except Exception as e:
            logger("ERROR", f"Failed to add song: {e}")
            self.controls.append(ft.Text("Failed to add song. Please try again.", color=ft.colors.RED))
            self.page.update()

    def addUserToDatabase(self, e):
        try:
            self.db_handler.insert_data(UserData, username=self.addUser.value, password=hash(self.addPassword.value), role=self.addRole.value, LoginTime=0)
            # Show a success message in a banner
            self.page.banner = ft.Banner(
                content=ft.Text("User added successfully!", color=ft.colors.GREEN),
                bgcolor=ft.colors.WHITE,
                actions=[
                    ft.TextButton("Close", on_click=lambda _: self.close_banner())
                ]
            )
            self.page.banner.open = True
            self.page.update()

        except Exception as e:
            logger("ERROR", f"Failed to add user: {e}")

            # Show an error message in a banner
            self.page.banner = ft.Banner(
                content=ft.Text("Failed to add user. Please try again.", color=ft.colors.RED),
                bgcolor=ft.colors.WHITE,
                actions=[
                    ft.TextButton("Close", on_click=lambda _: self.close_banner())
                ]
            )
            self.page.banner.open = True
            self.page.update()

    def close_banner(self):
        """Closes the banner."""
        pass

    def addUsersForm(self) -> ft.Card:
        self.addUser = ft.TextField(label="User", width=250)
        self.addPassword = ft.TextField(label="Password", width=250, password=True, can_reveal_password=True)
        self.addRole = ft.Dropdown(
            label="Role",
            width=100,
            options=[
                ft.dropdown.Option("ADMIN"),
                ft.dropdown.Option("USER")
            ]
        )

        addUserButton = ft.ElevatedButton("Add User", on_click=self.addUserToDatabase)

        user_form = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Add New User", size=18, weight="bold", font_family="Fira"),
                        self.addUser,
                        self.addPassword,
                        self.addRole,
                        addUserButton
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10
                ),
                padding=ft.padding.all(15),
                gradient=ft.LinearGradient(
                    begin=ft.alignment.Alignment(-1, -1),  # Top-left
                    end=ft.alignment.Alignment(1, 1),  # Bottom-right
                    colors=["#FFFED8", "#D6DCFF"],  # Your gradient colors
                ),
            ),
            elevation=5
        )
        return user_form

    def addSongsForm(self) -> ft.Card:
        self.addSongName = ft.TextField(label="Song Name", width=250)
        self.addArtist = ft.TextField(label="Artist", width=250)
        self.addAudio = ft.TextField(label="Audio Path", width=250)
        self.addSrc = ft.TextField(label="Image Path", width=250)

        addSongButton = ft.ElevatedButton("Add Song", on_click=self.addSongToDatabase)

        song_form = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Add New Song", size=18, weight="bold", font_family="Fira"),
                        self.addSongName,
                        self.addArtist,
                        self.addAudio,
                        self.addSrc,
                        addSongButton
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10
                ),
                padding=ft.padding.all(15),
                gradient=ft.LinearGradient(
                    begin=ft.alignment.Alignment(-1, -1),  # Top-left
                    end=ft.alignment.Alignment(1, 1),  # Bottom-right
                    colors=["#FFFED8", "#D6DCFF"],  # Your gradient colors
                ),
            ),
            elevation=5
        )
        return song_form

    def goAdminPage(self):
        # Clear all controls and add admin-specific controls
        self.controls.clear()
        self.Directory.refresh()
        def load_admin_page():
            self.controls.append(navbar(self.page, 2))
            self.controls.extend([
                ft.Text(f"Welcome, {self.page.session.get('user')}!", font_family="Fira", size=24, weight="bold"),
                ft.TextButton(
                    content=ft.Text("Log Out", font_family="Fira"),
                    on_click=self.logout
                )]
            )
            # Add a section for song statistics with a table
            stats = getSongStats(self)
            userlist = dict(sorted(self.userList().items(), key=lambda item: item[1][-1], reverse=True))
            user_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("User", font_family='Fira')),
                    ft.DataColumn(ft.Text("Last Login Time", font_family='Fira')),
                ],
                rows=[
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(user, font_family='Fira')),
                            ft.DataCell(ft.Text(unix_to_human(userlist[user][-1]), font_family='Fira'))
                        ]
                    ) for user in userlist
                ]
            )

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

            # Wrap the data table and chart in a card
            stats_card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            user_table,
                            ft.Text("Song Statistics", size=18, weight="bold", font_family="Fira"),
                            table,
                            ft.Image(src_base64=returnBase64(self=self, data=getDailyData(self)))
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=10
                    ),
                    padding=ft.padding.all(15),
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.Alignment(-1, -1),  # Top-left
                        end=ft.alignment.Alignment(1, 1),  # Bottom-right
                        colors=["#FFFED8", "#D6DCFF"],  # Your gradient colors
                    ),
                ),
                elevation=5
            )

            # Add the user and song forms in a row for better layout
            forms_row = ft.Row(
                controls=[
                    self.addSongsForm(),
                    self.addUsersForm()
                ],
                spacing=20,
                wrap=True,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )

            # Wrap forms in a column for further layout organization
            forms_section = ft.Column(
                controls=[
                    ft.Text("Administration Tools", size=24, weight="bold", font_family="Fira"),
                    forms_row
                ],
                spacing=20
            )
            self.controls.extend([stats_card, forms_section, self.removeItemsForm()])
            self.page.update()
        self.execute_in_thread(load_admin_page)