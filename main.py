import flet as ft
from navbar import navbar
from hashlib import sha256 # for admin purposes
from tools import *
import matplotlib.pyplot as plt
import io
import base64
from time import localtime

t=localtime()
time_now=str(t.tm_year)+str(t.tm_mon)+str(t.tm_mday)

# define a song class
class Song(object):
    def __init__(self, song_name: str, artist: str, audio_path: str, img_src:str, song_id:int):
        super(Song, self).__init__()
        self.song_name = song_name
        self.artist_name = artist
        self.audio_path = audio_path
        self.img_src=img_src
        self.song_id=song_id

    @property
    def src(self):
        return self.img_src

    @property
    def id(self):
        return self.song_id

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
    # read lines
    cursor=connectDatabase().cursor()
    cursor.execute("SELECT * FROM songs")
    lines=cursor.fetchall()
    playlist:list=[]
    for i in lines:
        playlist.append(Song(song_id=i[0],song_name=i[1],artist=i[2],audio_path=i[3],img_src=i[4]))
    #print(playlist[0].artist, "***")
    cursor.close()


class PlayList(ft.View):
    def __init__(self, page: ft.Page):
        super(PlayList, self).__init__(
            route='/discover',
            horizontal_alignment='center'
        )

        self.page = page
        self.playlist: list[Song] = AudioDirectory.playlist

        self.controls = [
            ft.Row(
                [
                    ft.Text("PLAYLIST", size=21, weight='bold',font_family="Fira")
                ],
                alignment='center'
            )
        ]
        self.controls.append(navbar(self.page,1))
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
                    ft.Text(f"Title: {song.name}",font_family="Fira"),
                    ft.Text(artist,font_family="Fira"),
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
        self.audio = None
        self.page=page
        self.song=self.page.session.get('song')
        self.add_num()

        #print(self.song.song_name, self.song.artist_name)

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
        conn=connectDatabase()
        cursor=conn.cursor()
        # add counts
        cursor.execute(f"SELECT counts FROM songs WHERE song_id={self.song.song_id}")
        count = cursor.fetchone()
        if count:
            cursor.execute(f"UPDATE songs SET counts={count[0]+1} WHERE song_id={self.song.song_id}")
        else:
            cursor.execute(f"INSERT INTO songs (song_id,counts) VALUES ({self.song.song_id},1)")
        # write to daily statistics
        cursor.execute(f"SELECT * FROM daily_stats WHERE date='{time_now}'")
        count = cursor.fetchone()
        if count:
            cursor.execute(f"UPDATE daily_stats SET counts={count[1]+1} WHERE date='{time_now}'")
        else:
            cursor.execute(f"INSERT INTO daily_stats (date,counts) VALUES ('{time_now}',1)")
        conn.commit()
        conn.close()


    def play(self, e):
        try:
            # Ensure that the audio control is properly initialized and added to the page
            if not self.audio:
                self.create_audio_track()
            from time import sleep
            sleep(0.5)  # sleep 0.5 seconds to ensure nothing is None
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
        except Exception as ex:
            print(f"An error occurred: {ex}")

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


class HomePage(ft.View):
    def __init__(self, page: ft.Page):
        super(HomePage, self).__init__(
            route='/home',
            horizontal_alignment='center'
        )
        self.page=page
        self.controls.append(navbar(self.page,0))
        self.playlist: list[Song] = AudioDirectory.playlist
        self.page.fonts={
            "Fira":"FiraCode.ttf"
        }

        #add home logo to page
        self.controls.append(
            ft.Container(
                image_src=f"logo.png",
                width=250,
                height=250
            )
        )
        self.controls.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(
                            "播放最多的歌曲",
                            size=15,
                            font_family="Fira",
                        )
                    ],
                    alignment="center"
                ),
                padding=10
            )
        )
        self.add_fav_to_home()

    def add_fav_to_home(self):
        song=getSongStats(self)
        for i in range(0,len(song),2):
            try:
                first = song[i]
                second = song[i + 1]
                res = self.create_song_row(first, second)
                self.controls.append(res)
            except Exception as e:
                print(f"Error: {e}")

    def toggle_song(self, e):
        self.page.session.set("song",e.control.data)
        self.page.go('/song')


    def create_song_row(self, song: Song, song2: Song)->ft.Row:
        # Create the first container with image and text for the first song
        cont1 = ft.Container(
            content=ft.Column(
                [
                    ft.Image(src=song.img_src, expand=True),  # Adjust width/height for initial size
                    ft.Text(
                        f'{song.name}\n{song.artist}',
                        font_family="Fira",
                        text_align="center",
                        size=14  # Font size that adjusts
                    )
                ],
                alignment="center",
                horizontal_alignment="center",

            ),
            padding=10,
            border=ft.border.all(10, ft.colors.GREEN_ACCENT),
            expand=True,  # Allow the container to expand
            data=song,
            on_click=self.toggle_song
        )

        # Create the second container with image and text for the second song
        cont2 = ft.Container(
            content=ft.Column(
                [
                    ft.Image(src=song2.img_src, expand=True),  # Adjust width/height for initial size
                    ft.Text(
                        f'{song2.name}\n{song2.artist}',
                        font_family="Fira",
                        text_align="center",
                        size=14  # Font size that adjusts
                    )
                ],
                #alignment="center",
                horizontal_alignment="center"
            ),
            padding=10,
            border=ft.border.all(10, ft.colors.GREEN_ACCENT),
            expand=True,  # Allow the container to expand
            data=song2,
            on_click=self.toggle_song
        )

        # Create the row containing both containers
        content = ft.Row(
            controls=[cont1, cont2],
            alignment="SPACE_EVENLY",
            expand=True  # Allow the row to expand
        )

        # Return the containers and content row
        return content

class Admin(ft.View):
    def __init__(self, page: ft.Page):
        super(Admin, self).__init__(
            route='/settings',
            horizontal_alignment='center',
            scroll='ALWAYS'
        )
        self.page = page
        self.page.fonts = {"Fira": "FiraCode.ttf"}
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

    def submitInfo(self, e):
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

    def returnBase64(self,data:dict):
        plt.switch_backend('Agg')
        sorted_data = sorted(data.items())
        dates = [item[0] for item in sorted_data]
        times = [int(item[1]) for item in sorted_data]

        # Create the plot
        fig, ax = plt.subplots()
        ax.plot(dates, times, marker='o')

        # Set labels
        ax.set_xlabel("Date")
        ax.set_ylabel("Times")
        ax.set_title("Times vs. Date")

        # Save the plot to a BytesIO object
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)

        # Convert the plot to a base64 string for Flet Image
        img_data = buffer.getvalue()
        plt.close(fig)  # Close the figure after saving to free resources

        # Convert BytesIO object to a base64-encoded image
        img_data = base64.b64encode(img_data).decode("utf-8")
        return img_data

    def getDailyData(self):
        cursor=connectDatabase().cursor()
        cursor.execute("SELECT * FROM daily_stats")
        lines = cursor.fetchall()
        res = {}
        for line in lines:
            if len(line) == 2:
                res[str(line[0])] = line[1]
        cursor.close()
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
        self.controls.append(table)
        self.controls.append(
            ft.Image(
                src_base64=self.returnBase64(self.getDailyData())
            )
        )

        # Refresh the page to reflect the changes
        self.page.update()


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
        self.playlist: list[Song] = AudioDirectory.playlist
        self.init()

    def getComments(self, song_id:int):
        directory='Comments/'+str(song_id)+'.txt'
        file=open(directory,'r').readlines()
        return file

    def sendComment(self,e):
        val=e.control.value
        directory = 'Comments/' + str(self.song_id) + '.txt'
        file = open(directory, 'a')
        file.writelines(f'{val}\n')
        file.close()
        print('Send Comment OK')
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
            self.controls.append(
                ft.Row(
                    controls=[ft.Text(value=f'Commented：{each}', font_family='Fira')]
                )
            )

        self.controls.append(
            ft.TextField(
                label='Comment Here',
                on_submit=self.sendComment
            )
        )





def main(page: ft.Page):
    # page start
    page.theme_mode = ft.ThemeMode.LIGHT
    def router(route):
        page.views.clear()
        if(page.route=='/home'):
            homepage=HomePage(page)
            page.views.append(homepage)
        if (page.route == '/discover'):
            playlist = PlayList(page)
            page.views.append(playlist)
        if page.route=='/song':
            song=CurrentSong(page)
            page.views.append(song)
        if page.route=='/settings':
            page.views.append(Admin(page))
        if page.route=='/comments':
            page.views.append(Comments(page))

        page.update()

    page.on_route_change = router
    page.go('/home')


ft.app(target=main)
