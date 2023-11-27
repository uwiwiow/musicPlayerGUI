import PIL.Image
import pygame as pg
from music import Music
import ttkbootstrap as ttk
from PIL import Image, ImageTk
from doubleLinkedList import DLL
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame

# window
window = ttk.Window(themename='darkly')
window.title("Kilq Music Player")
window.geometry('1600x900')
window.iconbitmap('assets/icon.ico')
window.state('zoomed')

# pg
pg.mixer.init()
music = Music().list_songs()


def on_enter(event):
    event.widget.configure(bootstyle="secondary")
    for child in event.widget.winfo_children():
        if child.winfo_name() == 'play_button':
            child.config(image=play_image, bootstyle='secondary')
        elif child.winfo_name() == 'queue_button':
            child.config(bootstyle='secondary')
        else:
            if isinstance(child, ttk.Frame):
                child.winfo_children()[0].configure(bootstyle="inverse-secondary")
                child.winfo_children()[1].configure(bootstyle="inverse-secondary")
            else:
                child.configure(bootstyle="inverse-secondary")


def on_leave(event):
    event.widget.configure(bootstyle='default')
    for child in event.widget.winfo_children():
        if child.winfo_name() == 'play_button':
            child.config(image='', bootstyle='default-link')
        elif child.winfo_name() == 'queue_button':
            child.config(bootstyle='default-link')
        else:
            if isinstance(child, ttk.Frame):
                child.winfo_children()[0].configure(bootstyle="default")
                child.winfo_children()[1].configure(bootstyle="light")
            else:
                child.configure(bootstyle="default")


def open_img(file_path):
    img = Image.open(file_path)
    photo = ImageTk.PhotoImage(img)
    return photo


def load_song(song_data: tuple[str, dict, PIL.Image.Image]):
    if pause_var.get():
        pause_song()
        dll.pop()
    if pg.mixer_music.get_busy():
        dll.pop()
    progress_var.set(0)
    dll.push(song_data)
    play()


def is_playing():
    if not pg.mixer_music.get_busy() and not pause_var.get():
        print(pause_var.get())
        progress_var.set(progress_var.get() + ((0.1 * 100) / dll.get()[1]['duration']))
        dll.pop()
        if dll.get() is not None:
            time_var.set(time_var.get() - dll.get()[1]['duration'])
            progress_var.set(0)
            play()
        progress_var.set(0)
        update_queue()
    else:
        if not pause_var.get():
            pg.mixer_music.unpause()
            progress_var.set(progress_var.get() + ((0.1 * 100) / dll.get()[1]['duration']))
            window.after(100, is_playing)
        if pause_var.get():
            pg.mixer_music.pause()
            window.after(100, is_playing)


def play():
    song: tuple[str, dict, PIL.Image.Image] = dll.get()
    window.nametowidget('bottom_frame.song_data_frame.title').configure(text=song[1]['title'], bootstyle='default')
    window.nametowidget('bottom_frame.song_data_frame.author').configure(text=song[1]['artist'], bootstyle='light')
    window.nametowidget('bottom_frame.cover_image')['image'] = song[2]
    pg.mixer_music.load(song[0])
    pg.mixer_music.play(1)
    is_playing()
    update_queue()


def add_to_queue(song_data: tuple[str, dict, PIL.Image.Image]):
    # check if total time in queue is less than 15-min or queue max time is disabled
    if (time_var.get() + song_data[1]['duration']) <= 900 or disable_time.get():
        time_var.set(time_var.get() + song_data[1]['duration'])  # add song duration for queue list
        dll.append(song_data)  # add song to node
        update_queue()  # updates queue frame
        if not pg.mixer_music.get_busy():  # plays music if there's no music already playing
            time_var.set(time_var.get() - song_data[1][
                'duration'])  # reduces the time duration of the variable for the queue list
            play()
    else:
        time_limit()


# cant be pickled
play_image = open_img('assets/play.png')
add_queue_image = open_img('assets/add_queue.png')
queue_image = open_img('assets/queue.png')
unpaused_image = open_img('assets/pause.png')
paused_image = open_img('assets/unpause.png')

# add 0 to one-digit numbers as str
add = lambda x: '0' + str(x) if len(str(x)) == 1 else x

# set app sizes for low res
fhd = [60, 45, 25, 25, 600]
hd = [40, 30, 10, 15, 450]
res: list[int] = hd if window.winfo_width() < 1880 else fhd

# main frame with scroller
sf = ScrolledFrame(window, name='main_sf')
sf.pack(fill=BOTH, expand=YES)

# double linked list st
dll = DLL()

# vars
time_var = ttk.IntVar()
disable_time = ttk.BooleanVar()
progress_var = ttk.DoubleVar()

for i, v in enumerate(music):
    frame = ttk.Frame(sf, name=f'song{i}')  # individual frame for each song

    number = ttk.Button(frame, text=f'{i + 1}', width=3, image=None, bootstyle='default-link', name='play_button',
                        command=lambda song_data=v: load_song(song_data))
    number.pack(side='left', padx=(20, 10))

    image_label = ttk.Label(frame, image=v[2])
    image_label.pack(side='left', padx=10)

    data_frame = ttk.Frame(frame, width=res[0])
    title = ttk.Label(data_frame, text=f'{v[1]["title"]}', width=res[0], font='14')
    title.pack()
    autor = ttk.Label(data_frame, text=f'{v[1]["artist"]}', width=res[0], font='12', bootstyle='light')
    autor.pack()
    data_frame.pack(side='left', padx=15)

    album = ttk.Label(frame, text=f'{v[1]["album"]}', width=res[1], font='14')
    album.pack(side='left', padx=15)

    fecha = ttk.Label(frame, text=f'{v[1]["year"]}', width=res[2], font='14')
    fecha.pack(side='left', padx=15)

    genero = ttk.Label(frame, text=f'{v[1]["genre"]}', width=res[3], font='14')
    genero.pack(side='left', padx=15)

    duration = ttk.Label(frame, text=f'{add(int(v[1]["duration"]) // 60)}:{add(int(v[1]["duration"]) % 60)}',
                         width=10,
                         font='14')
    duration.pack(side='left', padx=15)

    queue = ttk.Button(frame, width=3, image=add_queue_image, bootstyle='default-link', name='queue_button',
                       command=lambda song_data=v: add_to_queue(song_data))
    queue.pack(side='left', padx=15)

    frame.pack(ipady=10, anchor='w', fill='x')
    frame.bind("<Enter>", on_enter)
    frame.bind("<Leave>", on_leave)


def disable_time_limit():
    if not disable_time.get():
        disable_time.set(ttk.TRUE)
    else:
        disable_time.set(ttk.FALSE)


def mostrar_lista_canciones():
    if button_var.get():
        button_var.set(ttk.FALSE)
        window.nametowidget('float_frame').destroy()
    else:
        button_var.set(ttk.TRUE)
        # Crea un nuevo Frame para mostrar la lista de canciones
        frame_canciones = ttk.Frame(window, padding=1, width=420, height=res[4], borderwidth=1, relief='solid',
                                    bootstyle='dark', name='float_frame')
        frame_canciones.propagate(0)
        frame_canciones.place(relx=1.0, rely=1.0, x=-20, y=-100, anchor="se")

        ttk.Label(frame_canciones, text="Lista de Reproducción", font='arial 16 bold', bootstyle='inverse-dark',
                  name='label_lista_canciones').pack()
        ttk.Label(frame_canciones, text=f'{add(time_var.get() // 60)}:{add(time_var.get() % 60)}', font='arial 16 bold',
                  bootstyle='inverse-dark', name='tiempo').pack()

        sf_canciones = ScrolledFrame(frame_canciones, name='frame_scroll')
        sf_canciones.pack(fill=BOTH, expand=YES)

        update_queue()


def update_queue():
    if button_var.get():
        sf_widget = window.nametowidget('.float_frame.!frame.frame_scroll')
        window.nametowidget('.float_frame.tiempo')['text'] = f'{add(time_var.get() // 60)}:{add(time_var.get() % 60)}'
        for child in sf_widget.winfo_children():
            child.destroy()

        songs_data = dll.display()
        for it, song_data in enumerate(songs_data):
            if it == 0:
                song_frame = ttk.Frame(sf_widget, name=f'song{it}')
                num = ttk.Label(song_frame, text=f'{it + 1}', width=3, image=None, name=str(it), font='14',
                                   bootstyle='success')
                num.pack(side='left', padx=(20, 10))

                lbl_title = ttk.Label(song_frame, text=f'{song_data[1]["title"]}', width=45, font='14', bootstyle='success')
                lbl_title.pack(side='left', padx=15)
                song_frame.pack(ipady=20, anchor='w', fill='x')

                ttk.Separator(sf_widget).pack(anchor='w', fill='x')
            else:
                song_frame = ttk.Frame(sf_widget, name=f'song{it}')
                num = ttk.Label(song_frame, text=f'{it + 1}', width=3, image=None, name=str(it), font='14')
                num.pack(side='left', padx=(20, 10))

                lbl_title = ttk.Label(song_frame, text=f'{song_data[1]["title"]}', width=45, font='14')
                lbl_title.pack(side='left', padx=15)
                song_frame.pack(ipady=20, anchor='w', fill='x')


def time_limit():
    if button_var.get():
        sf_widget = window.nametowidget('.float_frame.!frame.frame_scroll')

        error_frame = ttk.Frame(sf_widget, name='error_frame')
        lbl_title = ttk.Label(error_frame, text='Tiempo limite alcanzado: maximo 15 minutos', width=45, font='20', bootstyle='danger')
        lbl_title.pack(side='left', padx=15)
        error_frame.pack(ipady=20, anchor='w', fill='x')


def pause_song():
    if not pause_var.get():
        pause_var.set(ttk.TRUE)
        btn = window.nametowidget('.bottom_frame.controls.pause_button')
        btn['image'] = unpaused_image
    else:
        pause_var.set(ttk.FALSE)
        btn = window.nametowidget('.bottom_frame.controls.pause_button')
        btn['image'] = paused_image


def set_volume(value):
    pg.mixer_music.set_volume(float(value))


bottom_frame = ttk.Frame(window, name='bottom_frame', borderwidth=1, relief='solid')
bottom_frame.pack(side='bottom', fill='x')
bottom_frame.config(height=90)
bottom_frame.propagate(0)

# right buttons, controls
button_var = ttk.BooleanVar()
boton_mostrar_canciones = ttk.Button(bottom_frame, image=queue_image, command=mostrar_lista_canciones,
                                     textvariable=button_var, bootstyle='secondary')
boton_mostrar_canciones.pack(side='right', padx=30)

ttk.Checkbutton(bottom_frame, bootstyle="dark-toolbutton", text='Desactivar limite de tiempo',
                command=disable_time_limit).pack(side='right')

volume_slider = ttk.Scale(bottom_frame, to=1, orient="horizontal", name='volume', command=set_volume, bootstyle='dark')
volume_slider.set(1)
volume_slider.pack(side='right', padx=25)

# left buttons, data
cover_image = ttk.Label(bottom_frame, image=None, name='cover_image')
cover_image.pack(side='left', padx=(45, 15))

song_data_frame = ttk.Frame(bottom_frame, name='song_data_frame')

title = ttk.Label(song_data_frame, font='14', name='title')
title.pack()

author = ttk.Label(song_data_frame, font='10', name='author')
author.pack()

song_data_frame.pack(side='left', padx=25)

# mid controls
controls_frame = ttk.Frame(bottom_frame, height=80, width=600, name='controls')

pause_var = ttk.BooleanVar()
# pause = ttk.Button(controls_frame, image=paused_image, command=pause_song, textvariable=pause_var, name='pause_button', bootstyle='dark-link')
# pause.pack()  TODO arreglar esto

progress_bar = ttk.Progressbar(controls_frame, variable=progress_var, orient='horizontal', length=600, mode='determinate')
progress_bar.pack(pady=10)

controls_frame.pack(pady=5)
controls_frame.propagate(0)

# run
window.mainloop()
