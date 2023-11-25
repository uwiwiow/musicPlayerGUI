import os
import io
import pickle
import hashlib
import PIL.Image
import pygame as pg
import tkinter as tk
import ttkbootstrap as ttk
from tinytag import TinyTag
from PIL import Image, ImageTk
from doubleLinkedList import DLL
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame


def hash_files(dir_):
    return hashlib.sha256("".join(
        [f for f in os.listdir(dir_) if os.path.isfile(os.path.join(dir_, f))]).encode()).hexdigest()


def list_songs(music_directory="music\\") -> list[tuple[str, dict, PIL.Image.Image]]:
    """
    Load song from the given folder

    :return:
        A list of tuples where each tuple consists of a string representing the full path of the song,
        a dictionary containing the song tags, and an image representing the album cover
    """
    directory = music_directory
    hash_ = hash_files(directory)

    try:
        with open('assets/music.pkl', 'rb') as f:
            loaded_data: dict = pickle.load(f)
            loaded_hash = loaded_data.get('hash_')
            loaded_music_list = loaded_data.get('music_list')
    except (FileNotFoundError, pickle.UnpicklingError):
        loaded_hash = None
        loaded_music_list = None

    if hash_ == loaded_hash:
        return loaded_music_list
    else:
        music_list = []
        for song in os.listdir(directory):
            full_dir = directory + song
            music_list.append((full_dir, TinyTag.get(full_dir).as_dict(),
                               Image.open(io.BytesIO(TinyTag.get(full_dir, image=True).get_image()))))

        data = {'hash_': hash_, 'music_list': music_list}

        with open('assets/music.pkl', 'wb') as f:
            pickle.dump(data, f)

        return music_list


# pg
pg.mixer.init()
music = list_songs()


def on_enter(event):
    event.widget.configure(bootstyle="secondary")
    for child in event.widget.winfo_children():
        if child.winfo_name() == 'play_button':
            child.config(image=play_image)
        elif child.winfo_name() == 'queue_button':
            continue
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
            child.config(image='')
        elif child.winfo_name() == 'queue_button':
            continue
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


def load_img(img: PIL.Image.Image, width: int = 45, height: int = 45):
    res_img = img.resize((width, height), Image.LANCZOS)
    return ImageTk.PhotoImage(res_img)


def load_song(song_data: tuple[str, dict, PIL.Image.Image]):
    dll.push(song_data)
    play()


def play():
    song: tuple[str, dict, PIL.Image.Image] = dll.get()
    pg.mixer_music.load(song[0])
    pg.mixer_music.play(1)
    dll.pop()  # TODO revisar que si hace pop actualice en queue


def add_to_queue(song_data: tuple[str, dict, PIL.Image.Image]):
    dll.append(song_data)
    pg.mixer_music.queue(song_data[0])
    # TODO anadir el tiempo total para no pasar los 15 minutos
    if not pg.mixer_music.get_busy():
        play()


# window
window = ttk.Window(themename='darkly')
window.title("Kilq Music Player")
window.geometry('1600x900')
window.iconbitmap('assets/icon.ico')
window.state('zoomed')  # TODO uncomment this line

# cant be pickled
play_image = open_img('assets/play.png')
queue_image = open_img('assets/queue.png')
images = []
for i, val in enumerate(music):
    images.append(load_img(val[2]))

# add 0 to one-digit numbers as str
add = lambda x: '0' + str(x) if len(str(x)) == 1 else x

# set app sizes for low res
fhd = [60, 45, 25, 25]
hd = [40, 30, 10, 15]
res: list[int] = hd if window.winfo_width() < 1880 else fhd

# main frame with scroller
sf = ScrolledFrame(window)
sf.hide_scrollbars()
sf.pack(fill=BOTH, expand=YES)

# double linked list st
dll = DLL()

for i, v in enumerate(music):
    frame = ttk.Frame(sf)  # individual frame for each song

    play_button_var = ttk.BooleanVar()
    number = ttk.Button(frame, text=f'{i + 1}', width=3, image=None, bootstyle='dark', name='play_button',
                        command=lambda song_data=v: load_song(song_data))
    number.pack(side='left', padx=(20, 10))

    image_label = ttk.Label(frame, image=images[i])
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

    duration = ttk.Label(frame, text=f'{add(int(v[1]["duration"]) // 60)}:{add(int(v[1]["duration"]) % 60)}', width=10,
                         font='14')
    duration.pack(side='left', padx=15)

    queue = ttk.Button(frame, width=3, image=queue_image, bootstyle='dark', name='queue_button',
                        command=lambda song_data=v: add_to_queue(song_data))
    queue.pack(side='left', padx=15)

    frame.pack(ipady=20, anchor='w', fill='x')
    frame.bind("<Enter>", on_enter)
    frame.bind("<Leave>", on_leave)
    frame.configure()


def mostrar_lista_canciones():
    if button_var.get():
        for child in window.winfo_children():
            if child.winfo_name() == 'float_frame':
                button_var.set(ttk.FALSE)
                child.destroy()
    else:
        button_var.set(ttk.TRUE)
        # Crea un nuevo Frame para mostrar la lista de canciones
        frame_canciones = ttk.Frame(window, padding=10, width=420, height=60, borderwidth=1, name='float_frame',
                                    bootstyle='dark')
        frame_canciones.propagate(0)
        frame_canciones.place(relx=1.0, rely=1.0, x=-20, y=-70, anchor="se")

        sf_canciones = ScrolledFrame(frame_canciones, bootstyle='dark')
        # sf_canciones.hide_scrollbars()
        sf_canciones.pack(fill=BOTH, expand=YES)

        # TODO Agregar scroll por si hay muchas canciones en el queue
        # TODO Agrega contenido a frame_canciones
        ttk.Label(sf_canciones, text="Lista de Canciones", bootstyle='inverse-dark').pack()
        ttk.Label(sf_canciones, text="Lista de Canciones", bootstyle='inverse-dark').pack()
        ttk.Label(sf_canciones, text="Lista de Canciones", bootstyle='inverse-dark').pack()
        ttk.Label(sf_canciones, text="Lista de Canciones", bootstyle='inverse-dark').pack()
        ttk.Label(sf_canciones, text="Lista de Canciones", bootstyle='inverse-dark').pack()
        ttk.Label(sf_canciones, text="Lista de Canciones", bootstyle='inverse-dark').pack()
        ttk.Label(sf_canciones, text="Lista de Canciones", bootstyle='inverse-dark').pack()
        ttk.Label(sf_canciones, text="Lista de Canciones", bootstyle='inverse-dark').pack()
        ttk.Label(sf_canciones, text="Lista de Canciones", bootstyle='inverse-dark').pack()
        # TODO poner las canciones en queue
        # TODO llama display


bottom_frame = ttk.Frame(window, bootstyle='dark', name='bottom_frame')
bottom_frame.pack(side='bottom', fill='x')
bottom_frame.config(height=90)

button_var = ttk.BooleanVar()
boton_mostrar_canciones = ttk.Button(bottom_frame, text="Mostrar Lista de Canciones", command=mostrar_lista_canciones,
                                     textvariable=button_var, bootstyle='secondary')
boton_mostrar_canciones.pack(side='right', padx=10, pady=10)

# run
window.mainloop()
