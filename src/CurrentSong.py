import flet as ft
from modules import Database, GPT, Song
from modules.Tables import *
from modules.tools import *

from time import *
t=localtime()
time_now=str(t.tm_year)+str(t.tm_mon)+str(t.tm_mday)


class CurrentSong(ft.View):
    def __init__(self,page:ft.Page):
        super(CurrentSong,self).__init__(
            route='/song',
            padding=20,
            horizontal_alignment='center',
            vertical_alignment='center'
        )
        self.audio = None
        self.page = page
        self.song = self.page.session.get('song')
        self.db_handler = self.page.session.get('database')

        self.add_num()
        #define vars for current song
        self.duration=0
        self.start=0
        self.end=0
        self.is_playing=False
        #define UI for current song
        self.txt_start=ft.Text(self.format_time(self.start),font_family="Fira")
        self.txt_end = ft.Text(f"-{self.format_time(self.start)}",font_family="Fira")
        self.slider=ft.Slider(min=0,thumb_color='transparent',on_change_end=
                              lambda e: self.toggle_seek(round(float(e.data))))

        self.back_btn=ft.TextButton(
            content=ft.Text(
                "Playlist",
                color='black'
                , font_family="Fira"
            ),
            on_click=self.toggle_playlist,
        )

        self.comment_btn = ft.TextButton(
            content=ft.Text(
                "Comment",
                color='black'
                , font_family="Fira"
            ),
            on_click=lambda e:self.page.go('/comments'),
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
                image_src=self.song.src # image
            ),
            ft.Divider(height=10,color='transparent'),
            ft.Column(
                [
                    ft.Row(controls=[ft.Text(self.song.song_name,size=18,weight='bold',font_family="Fira")]),
                    ft.Row(
                        controls=[ft.Text(self.song.artist,size=15,opacity=0.81,font_family="Fira")],
                    ),

                ],
                spacing=1
            ),
            ft.Divider(height=10,color="transparent"),

            #timestamp UI
            ft.Column(
                [
                    ft.Row([self.txt_start,self.txt_end],alignment='spaceBetween'),
                    self.slider,
                ],
                spacing=0
            ),
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
                        lambda e: self.__update_position(5000),
                    ),
                ],
                alignment='spaceEvenly'
            ),
            ft.Divider(height=10,color="transparent"),
            ft.Row(
                [self.comment_btn],
                alignment='end'
            ),
        ]

        self.create_audio_track()

    def add_num(self):
        res = self.db_handler.query_data(Songs, song_id=self.song.song_id)
        if res:
            self.db_handler.update_data(Songs, filters={'song_id':self.song.song_id}, updates={'counts':res[0].counts+1})
        else:
            self.db_handler.insert_data(Songs, song_id=self.song.song_id, song_name=self.song.song_name, artist=self.song.artist, audio_path=self.song.path, img_src=self.song.src, counts=0)

        res = self.db_handler.query_data(Daily,date=time_now)
        if res:
            self.db_handler.update_data(Daily, filters={'date':time_now}, updates={'counts':res[0].counts+1})
        else:
            self.db_handler.insert_data(Daily, date=time_now, counts=1)

    def play(self, e):
        try:
            # Ensure that the audio control is properly initialized and added to the page
            if not self.audio:
                self.create_audio_track()
            from time import sleep
            while not self.audio.get_duration:
                sleep(0.03)
            # Toggle play/pause and retrieve the duration
            self.toggle_play_pause()
            self.duration = self.audio.get_duration()

            # Handle case where duration retrieval fails
            if self.duration is None:
                print("Error: Unable to retrieve audio duration.")
                return

            # Update the slider's maximum value
            self.end = self.duration
            self.slider.max = self.duration
        except TimeoutError as ex:
            print(f"TimeoutError: {ex}")
            logger("ERROR", f"TimeoutError: {ex}")
        except Exception as ex:
            print(f"An error occurred: {ex}")
            logger("ERROR", f"Error: {ex}")

    #    def play(self,e):
 #       self.toggle_play_pause()
  #      self.duration = self.audio.get_duration()
   #     self.end = self.duration
    #    self.slider.max=self.duration

    def toggle_seek(self, delta:float):
        self.start=delta
        self.end=self.duration-delta
        self.audio.seek(self.start)
        self.__update_slider(delta)

    def toggle_play_pause(self,event=None):
        if self.is_playing:
            self.play_btn.icon=ft.icons.PLAY_ARROW_ROUNDED
            self.audio.pause()
        else:
            self.play_btn.icon=ft.icons.PAUSE_ROUNDED
            try:
                self.audio.resume()
            except Exception:
                self.audio.play()
        self.is_playing=False if self.is_playing else True
        #self.play_btn.on_click=self.toggle_play_pause()
        self.play_btn.update()


    def __update_start_end(self):
        if self.start<0:
            self.start=0
        if self.end>self.duration:
            self.end=self.duration

    def __update_position(self,e):
        self.__update_start_end()
        if(self.start>0):
            pos_change=e
            pos=self.start+pos_change
            self.audio.seek(pos)
            self.start+=pos_change
            self.end-=pos_change

    def __update_slider(self,delta):
        self.slider.value=delta
        self.slider.update()

    def __update_time_stamps(self,start:int,end:int):
        self.txt_start.value=self.format_time(start)
        self.txt_end.value=f"-{self.format_time(min(end,self.audio.get_duration()))}"
        self.txt_start.update()
        self.txt_end.update()


    def __update(self,delta:int):
        # once a song played, position updates by 1 sec
        self.start+=1000
        self.end-=1000

        #update position of slider
        try:
            self.__update_slider(delta)
            self.__update_time_stamps(self.start, self.end)
        except Exception as e:
            pass


    def format_time(self, value:int):
        milliseconds:int = value
        minutes,seconds = divmod(milliseconds / 1000,60)
        formatted_time: str = "{:02}:{:02}".format(int(minutes), int(seconds))
        return formatted_time

    def create_audio_track(self):
        #print(self.song.path)
        self.audio=ft.Audio(
            src=self.song.path,
            on_position_changed=lambda e: self.__update(
                int(e.data)
            )
        )
        self.page.overlay.append(self.audio)
        self.page.update()


    #generate buttons
    def create_toggle_button(self,icon,scale,function):
        return ft.IconButton(icon=icon,scale=scale,on_click=function)

    def toggle_playlist(self,e):
        self.audio.pause()
        self.page.session.remove('song')
        self.page.go('/discover')

