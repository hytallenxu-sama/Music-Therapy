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
    return nav_bar
