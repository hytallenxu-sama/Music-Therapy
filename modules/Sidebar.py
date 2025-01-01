import flet as ft


class Sidebar:
    def __init__(self, page: ft.Page):
        self.page = page
        self.sidebar = ft.Container(
            width=page.window_width / 3,  # Sidebar width
            height=page.window_height,  # Sidebar extends full height of the view
            bgcolor="#FFD8E8",
            gradient=ft.LinearGradient(
                begin=ft.alignment.Alignment(-1, -1),  # Top-left
                end=ft.alignment.Alignment(1, 1),  # Bottom-right
                colors=["#FFD8E8", "#D8FFE0"],  # Gradient colors
            ),
            border_radius=ft.border_radius.only(top_left=35, bottom_left=35),
            animate=ft.animation.Animation(600, ft.AnimationCurve.DECELERATE),
            padding=ft.padding.all(20),
            visible=False,  # Sidebar starts hidden
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.icons.CLOSE,
                                on_click=self.restore_sidebar,
                                icon_color="black",
                            )
                        ],
                        alignment="end",
                    ),
                    ft.Text("Menu", size=24, color="black", weight="bold"),
                    ft.Divider(color="white12"),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.icons.HOME, color="black60"),
                                ft.Text("Home", color="black"),
                            ],
                        ),
                        on_click=lambda e: page.go("/home"),
                        padding=ft.padding.symmetric(vertical=10),
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.icons.SEARCH, color="black60"),
                                ft.Text("Discover", color="black"),
                            ],
                        ),
                        on_click=lambda e: page.go("/discover"),
                        padding=ft.padding.symmetric(vertical=10),
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.icons.SETTINGS, color="black60"),
                                ft.Text("Settings", color="black"),
                            ],
                        ),
                        on_click=lambda e: page.go("/settings"),
                        padding=ft.padding.symmetric(vertical=10),
                    ),
                ],
                spacing=20,
            ),
        )

        self.main_content = None  # This will be set by the page

    def shrink_sidebar(self, e):
        """Shrink the main content and show the sidebar."""
        self.sidebar.visible = True  # Make the sidebar visible
        if self.main_content:
            self.main_content.width = self.page.window_width / 4 * 3  # Shrink main content
            self.main_content.scale = ft.transform.Scale(0.8, alignment=ft.alignment.center_right)
            self.main_content.border_radius = ft.border_radius.only(
                top_left=35, top_right=0, bottom_left=35, bottom_right=35
            )
        self.page.update()

    def restore_sidebar(self, e):
        """Restore the main content and hide the sidebar."""
        self.sidebar.visible = False  # Hide the sidebar
        if self.main_content:
            self.main_content.width = self.page.window_width  # Restore main content size
            self.main_content.scale = ft.transform.Scale(1, alignment=ft.alignment.center_right)
            self.main_content.border_radius = ft.border_radius.all(35)  # Rounded end restored
        self.page.update()
