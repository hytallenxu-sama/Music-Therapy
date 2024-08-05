import flet as ft


# define a song class
class Song(object):
    def __init__(self, song_name: str, artist: str, audio_path: str):
        super(Song, self).__init__()
        self.song_name = song_name
        self.artist_name = artist
        self.audio_path = audio_path

    @property
    def name(self):
        return self.song_name

    @property
    def artist(self):
        return self.artist_name

    @property
    def path(self):
        return self.audio_path


class AudioDirectory(object):
    playlist: list = [
        Song(
            song_name='xxxxx',
            artist='Hello',
            audio_path='xxxxx'
        )
    ]
    #print(playlist[0].artist, "***")


class PlayList(ft.View):
    def __init__(self, page: ft.Page):
        super(PlayList, self).__init__(
            route='/playlist',
            horizontal_alignment='center'
        )

        self.page = page
        self.playlist: list[Song] = AudioDirectory.playlist

        self.controls = [
            ft.Row(
                [
                    ft.Text("PLAYLIST", size=21, weight='bold')
                ],
                alignment='center'
            )
        ]
        self.gen_playlist_ui()

    def gen_playlist_ui(self):
        for song in self.playlist:
            self.controls.append(
                self.create_song_row(
                    song_name=song.song_name,
                    artist=song.artist,
                    song=song,
                )
            )

    def create_song_row(self, song_name, artist, song: Song):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(f"Title: {song.name}"),
                    ft.Text(artist),
                ],
                alignment="spaceBetween"
            ),
            data=song,
            padding=10,
            on_click=self.toggle_song
        )

    def toggle_song(self, e):
        self.page.session.set("song",e.control.data)
        self.page.go('/song')

class CurrentSong(ft.View):
    def __init__(self,page:ft.Page):
        super(CurrentSong,self).__init__(
            route='/song',
            padding=20,
            horizontal_alignment='center',
            vertical_alignment='center'
        )
        self.page=page
        self.song=self.page.session.get('song')
        #print(self.song.song_name, self.song.artist_name)

        #define vars for current song
        self.duration=0
        self.start=0
        self.end=0
        self.is_playing=False

        #define UI for current song
        self.txt_start=ft.Text(self.format_time(self.start))
        self.txt_end = ft.Text(f"-{self.format_time(self.start)}")
        self.slider=ft.Slider(min=0,thumb_color='transparent',on_change_end=None)

        self.back_btn=ft.TextButton(
            content=ft.Text(
                "Playlist",
                color='white'
            ),
            on_click=self.toggle_playlist,
        )

        self.play_btn=self.create_toggle_button(
            ft.icons.PLAY_ARROW_ROUNDED,2,self.play
        )


        # main controls
        self.controls=[
            ft.Row(
                [self.back_btn],
                alignment='start'
            ),
            # for image, can be canceled
            ft.Container(
                height=60,
                expand=True,
                border_radius=8,
                shadow=ft.BoxShadow(
                    spread_radius=6,
                    blur_radius=10,
                    color=ft.colors.with_opacity(0.35,'black'),
                ),
            ),
            ft.Divider(height=10,color='transparent'),
            ft.Column(
                [
                    ft.Row(controls=[ft.Text(self.song.song_name,size=18,weight='bold')]),
                    ft.Row(
                        controls=[ft.Text(self.song.artist,size=15,opacity=0.81)],
                    ),

                ],
                spacing=1
            ),
            ft.Divider(height=10,color="transparent"),

            #timestamp UI
            ft.Column(),
            ft.Divider(height=10, color="transparent"),
            ft.Row(
                [
                    self.create_toggle_button(
                        ft.icons.REPLAY_10_SHARP,
                        0.9,
                        lambda e:self.__update_position(-5000),
                    ),
                    self.play_btn,
                    self.create_toggle_button(
                        ft.icons.FORWARD_10_SHARP,
                        0.9,
                        lambda e: self.__update_position(-5000),
                    ),
                ],
                alignment='spaceEvenly'
            ),
            ft.Divider(height=10,color="transparent"),
        ]

    def play(self,e):
        pass


    def __update_position(self,e):
        pass

    def __update_slider(self,delta):
        self.slider.value=delta
        self.slider.update()

    def __update_time_stamps(self,start:int,end:int):
        self.txt_start=None
    def __update(self,delta:int):
        # once a song played, position updates by 1 sec
        self.start+=1000
        self.end-=1000

        #update position of slider
        self.__update_slider(delta)
        self.__update_slider(delta)
        self.__update_time_stamps()

    def format_time(self, value:int):
        milliseconds:int = value
        minutes,seconds = divmod(milliseconds / 1000,60)
        formatted_time: str = "{:02}:{:02}".format(int(minutes), int(seconds))
        return formatted_time

    def create_audio_track(self,e):
        self.audio=ft.Audio(
            src=self.song.path,
            on_position_changed=lambda e: self.__update(
                int(e.data)
            )
        )

        self.page.overlay.append(self.audio)

    #generate buttons
    def create_toggle_button(self,icon,scale,function):
        return ft.IconButton(icon=icon,scale=scale,on_click=function)

    def toggle_playlist(self,e):
        pass

def main(page: ft.Page):
    # navigation bar
    def on_nav_change(e: ft.ControlEvent):
        selected_index = e.control.selected_index
        selected_item = nav_bar.destinations[selected_index].label
        print(f"Selected item: {selected_item}")
        # Add your logic here to handle the navigation change

    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(label="Home", icon=ft.icons.HOME),
            ft.NavigationBarDestination(label="Profile", icon=ft.icons.PERSON),
            ft.NavigationBarDestination(label="Settings", icon=ft.icons.SETTINGS)
        ],
        selected_index=0,  # Default selected item
        on_change=on_nav_change  # Event handler for changes
    )
    # page.add(nav_bar)

    # page start
    page.theme_mode = ft.ThemeMode.LIGHT

    def router(route):
        page.views.clear()
        if (page.route == '/playlist'):
            playlist = PlayList(page)
            page.views.append(playlist)
        if page.route=='/song':
            song=CurrentSong(page)
            page.views.append(song)

        page.update()

    page.on_route_change = router
    page.go('/playlist')


ft.app(target=main)
