import flet as ft
from modules.tools import *
from modules.AudioDirectory import AudioDirectory
from modules.Tables import *
from modules.Sidebar import Sidebar  # Import the Sidebar class

import time
from concurrent.futures import ThreadPoolExecutor


class Admin(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route='/settings',
            horizontal_alignment='center',
            vertical_alignment='start',
            scroll='ALWAYS'
        )
        self.page = page
        self.page.fonts = {"Fira": "content/FiraCode.ttf"}
        self.db_handler = self.page.session.get('database')
        self.Directory = AudioDirectory()
        self.playlist = self.Directory.playlist
        self.executor = ThreadPoolExecutor(max_workers=10)

        # Initialize Sidebar
        self.sidebar = Sidebar(self.page)

        # Create a container for the main content without fixed height
        self.main_content = ft.Container(
            width=self.page.window_width,
            height=self.page.window_height,
            bgcolor="#FFFED8",
            gradient=ft.LinearGradient(
                begin=ft.alignment.Alignment(-1, -1),  # Top-left
                end=ft.alignment.Alignment(1, 1),      # Bottom-right
                colors=["#FFFED8", "#D6DCFF"],          # Gradient colors
            ),
            border_radius=ft.border_radius.only(
                top_left=35, top_right=35, bottom_left=35, bottom_right=35
            ),
            animate=ft.animation.Animation(600, ft.AnimationCurve.DECELERATE),
            animate_scale=ft.animation.Animation(400, curve="decelerate"),
            padding=ft.padding.only(left=20, right=20),
            content=ft.ListView(
                controls=[],  # Will be populated by self.init() or goAdminPage()
                spacing=10,
                padding=ft.padding.only(top=30)
            )
        )

        # Assign the main_content to the sidebar for layout adjustments
        self.sidebar.main_content = self.main_content

        # Stack to hold both the main content and the sidebar
        self.controls = [
            ft.Stack(
                controls=[
                    self.main_content,      # Main content at the bottom layer
                    self.sidebar.sidebar,  # Sidebar on top layer
                ]
            )
        ]
        # Initialize the login or admin page based on session
        self.init()

    def init(self):
        """Initialize the login form or navigate to admin page if already logged in."""
        # Clear any existing controls in main_content
        self.main_content.content.controls.clear()

        # Check for an existing session
        if self.page.session.contains_key("pw") and "ADMIN" in self.page.session.get("role"):
            # Automatically navigate to admin page if already logged in
            self.goAdminPage()
        else:
            # Initialize login fields
            self.user = ft.TextField(label="Username", width=500, autofocus=True)
            self.password = ft.TextField(label="Password", password=True, can_reveal_password=True, width=500)
            self.submitButton = ft.ElevatedButton("Submit", on_click=self.submitInfo)

            # Header with menu button (enabled but functionality may be limited before login)
            header = ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
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

            # Populate main_content with login controls
            self.main_content.content.controls.extend([
                header,
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
                        end=ft.alignment.Alignment(1, 1),      # Bottom-right
                        colors=["#FFFED8", "#D6DCFF"],          # Gradient colors
                    ),
                )
            ])
            self.page.update()

    def execute_in_thread(self, func, *args, **kwargs):
        """Helper to execute tasks in a separate thread."""
        self.executor.submit(func, *args, **kwargs)

    def addTimeStamp(self):
        """Update the timestamp in the database."""
        def update_timestamp():
            self.db_handler.update_data(
                UserData,
                filters={'username': self.page.session.get("user")},
                updates={'LoginTime': int(time.time())}
            )
        # Execute in a thread
        self.execute_in_thread(update_timestamp)

    def userList(self):
        """Retrieve the list of users from the database."""
        users = {}
        for user in self.db_handler.query_data(UserData):
            users[user.username] = [user.password, user.role, user.LoginTime]
        return users

    def submitInfo(self, e):
        """Handle the login submission."""
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
            error_message = ft.Text("Invalid Username or Password", color=ft.colors.RED)
            # Remove existing error messages to avoid duplicates
            self.main_content.content.controls = [
                ctrl for ctrl in self.main_content.content.controls
                if not (isinstance(ctrl, ft.Text) and ctrl.color == ft.colors.RED)
            ]
            self.main_content.content.controls.append(error_message)
            self.page.update()

    def logout(self, e):
        """Handle the logout action."""
        # Clear session and reinitialize login page
        self.page.session.remove("pw")
        self.page.session.remove("user")
        self.init()
        self.page.update()

    def removeUserFromDatabase(self, e):
        """Remove a user from the database."""
        try:
            self.db_handler.delete_data(UserData, username=self.removeUser.value)
        except Exception as e:
            logger("ERROR", f"Failed to remove user: {e}")

    def removeSongFromDatabase(self, e):
        """Remove a song from the database."""
        try:
            self.db_handler.delete_data(Songs, song_name=self.removeSong.value)
            self.page.update()

        except Exception as e:
            logger("ERROR", f"Failed to remove song: {e}")
            self.page.update()

    def removeItemsForm(self) -> ft.Card:
        """Create the form for removing users or songs."""
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
                    end=ft.alignment.Alignment(1, 1),      # Bottom-right
                    colors=["#FFFED8", "#D6DCFF"],          # Gradient colors
                ),
            ),
            elevation=5
        )
        return remove_form

    def addSongToDatabase(self, e):
        """Add a new song to the database."""
        try:
            self.db_handler.insert_data(
                Songs,
                song_name=self.addSongName.value,
                artist=self.addArtist.value,
                audio_path=self.addAudio.value,
                img_src=self.addSrc.value,
                counts=0
            )
            self.page.update()
        except Exception as e:
            logger("ERROR", f"Failed to add song: {e}")
            self.page.update()

    def addUserToDatabase(self, e):
        """Add a new user to the database."""
        try:
            self.db_handler.insert_data(
                UserData,
                username=self.addUser.value,
                password=hash(self.addPassword.value),
                role=self.addRole.value,
                LoginTime=0
            )
            self.page.update()
        except Exception as e:
            logger("ERROR", f"Failed to add user: {e}")
            self.page.update()

    def close_banner(self):
        """Closes the banner."""
        self.page.banner.open = False
        self.page.update()

    def addUsersForm(self) -> ft.Card:
        """Create the form for adding new users."""
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
                    end=ft.alignment.Alignment(1, 1),      # Bottom-right
                    colors=["#FFFED8", "#D6DCFF"],          # Gradient colors
                ),
            ),
            elevation=5
        )
        return user_form

    def addSongsForm(self) -> ft.Card:
        """Create the form for adding new songs."""
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
                    end=ft.alignment.Alignment(1, 1),      # Bottom-right
                    colors=["#FFFED8", "#D6DCFF"],          # Gradient colors
                ),
            ),
            elevation=5
        )
        return song_form

    def goAdminPage(self):
        """Navigate to the admin page with administration tools and statistics."""
        def load_admin_page():
            # Clear existing controls in main_content
            self.main_content.content.controls.clear()

            # Refresh directory and fetch statistics
            self.Directory.refresh()

            # Welcome message and logout button
            welcome_row = ft.Row(
                controls=[
                    ft.Text(
                        f"Welcome, {self.page.session.get('user')}!",
                        font_family="Fira",
                        size=24,
                        weight="bold",
                        color="black"
                    ),
                    ft.TextButton(
                        content=ft.Text("Log Out", font_family="Fira"),
                        on_click=self.logout
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )

            # User statistics table
            userlist = dict(sorted(
                self.userList().items(),
                key=lambda item: item[1][-1],
                reverse=True
            ))
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

            # Song statistics table
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

            # Song statistics card with user table and song table
            stats_card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            user_table,
                            ft.Text("Song Statistics", size=18, weight="bold", font_family="Fira", color="black"),
                            table,
                            ft.Image(src_base64=returnBase64(self=self, data=getDailyData(self)))
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=10
                    ),
                    padding=ft.padding.all(15),
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.Alignment(-1, -1),  # Top-left
                        end=ft.alignment.Alignment(1, 1),      # Bottom-right
                        colors=["#FFFED8", "#D6DCFF"],          # Gradient colors
                    ),
                ),
                elevation=5
            )

            # Forms for adding users and songs
            forms_row = ft.Row(
                controls=[
                    self.addSongsForm(),
                    self.addUsersForm()
                ],
                spacing=20,
                wrap=True,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )

            # Administration tools section
            forms_section = ft.Column(
                controls=[
                    ft.Text("Administration Tools", size=24, weight="bold", font_family="Fira", color="black"),
                    forms_row
                ],
                spacing=20
            )

            # Remove items form
            remove_items_form = self.removeItemsForm()

            # Header with menu button and notifications
            header = ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
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

            # Add all admin controls to main_content
            self.main_content.content.controls.extend([
                header,
                welcome_row,
                stats_card,
                forms_section,
                remove_items_form,
            ])
            self.page.update()

        # Execute the admin page setup in a separate thread
        self.execute_in_thread(load_admin_page)
