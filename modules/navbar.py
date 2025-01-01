import flet as ft

navi_dic={
    'Home':'/home',
    'Discover':'/discover',
    'Settings':'/settings'
}

def navbar(page, s:int):
    def on_nav_change(e: ft.ControlEvent):
        selected_index = e.control.selected_index
        selected_item = nav_bar.destinations[selected_index].label
        page.go(navi_dic[selected_item])

    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(label="Home", icon=ft.icons.HOME),
            ft.NavigationBarDestination(label="Discover", icon=ft.icons.PERSON),
            ft.NavigationBarDestination(label="Settings", icon=ft.icons.SETTINGS)
        ],
        selected_index=s,  # Default selected item
        on_change=on_nav_change  # Event handler for changes
    )

    def shrink(e):
        page2.controls[0].width=150
        page2.controls[0].scale=ft.transform.Scale(0.8, alignment=ft.alignment.center_right)
        page2.controls[0].border_radius=ft.border_radius.only(top_left=35, top_right=0, bottom_left=35, bottom_right=0)
        page2.update()

    nav = ft.Container(
        content = ft.Column(
            controls = [
                ft.Row(
                    alignment="spaceBetween",
                    controls=[
                        ft.Container(
                            on_click=lambda e: shrink(e), content=ft.Icon(ft.icons.MENU)
                        ),
                        ft.Row(
                            controls=[
                                ft.Icon(ft.icons.SEARCH),
                                ft.Icon(ft.icons.NOTIFICATIONS_OUTLINED),
                            ],
                        )
                    ]
                )
            ]
        )
    )

    page2 = ft.Row(
        alignment="end",
        controls=[
            ft.Container(
                width=400,
                height=850,
                bgcolor='#3450a1',
                border_radius=35,
                animate=ft.animation.Animation(600, ft.AnimationCurve.DECELERATE),
                animate_scale=ft.animation.Animation(400, curve="decelerate"),
                padding=ft.padding.only(top=50, left=20, right=20, bottom=5),
                content=ft.Column(controls=[nav]),
            )
        ]
    )

    return nav_bar
