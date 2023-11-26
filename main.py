import ast
import PIL.Image
import pygame as pg
import multiprocessing
from music import music
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
# window.state('zoomed')  # TODO uncomment this line

# pg
pg.mixer.init()
# TODO arreglar el inicio si no hayun pickle
music = music().list_songs()


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
    dll.push(song_data)
    play()


# TODO si termina la barra de reproduccion hacer el pop y update
def play():
    song: tuple[str, dict, PIL.Image.Image] = dll.get()
    pg.mixer_music.load(song[0])
    pg.mixer_music.play(1)
    dll.pop()  # TODO al agregar a queue (funcion abajo) o hacer play hacer que se actualice el frame de queue
    songs_var.set(dll.display(wdata='dict'))
    update_queue()


def add_to_queue(song_data: tuple[str, dict, PIL.Image.Image]):
    dll.append(song_data)
    songs_var.set(dll.display(wdata='dict'))
    pg.mixer_music.queue(song_data[0])
    update_queue()
    # TODO anadir el tiempo total para no pasar los 15 minutos
    if not pg.mixer_music.get_busy():
        play()


# cant be pickled
play_image = open_img('assets/play.png')
add_queue_image = open_img('assets/add_queue.png')
queue_image = open_img('assets/queue.png')

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
songs_var = ttk.StringVar()
songs_var.set(dll.display(wdata='dict'))

for i, v in enumerate(music):
    frame = ttk.Frame(sf)  # individual frame for each song

    play_button_var = ttk.BooleanVar()
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

    duration = ttk.Label(frame, text=f'{add(int(v[1]["duration"]) // 60)}:{add(int(v[1]["duration"]) % 60)}', width=10,
                         font='14')
    duration.pack(side='left', padx=15)

    queue = ttk.Button(frame, width=3, image=add_queue_image, bootstyle='default-link', name='queue_button',
                       command=lambda song_data=v: add_to_queue(song_data))
    queue.pack(side='left', padx=15)

    frame.pack(ipady=10, anchor='w', fill='x')
    frame.bind("<Enter>", on_enter)
    frame.bind("<Leave>", on_leave)


def mostrar_lista_canciones():
    if button_var.get():
        for child in window.winfo_children():
            if child.winfo_name() == 'float_frame':
                button_var.set(ttk.FALSE)
                child.destroy()
    else:
        button_var.set(ttk.TRUE)
        # Crea un nuevo Frame para mostrar la lista de canciones
        frame_canciones = ttk.Frame(window, padding=1, width=420, height=600, borderwidth=1, relief='solid', bootstyle='dark', name='float_frame')
        frame_canciones.propagate(0)
        frame_canciones.place(relx=1.0, rely=1.0, x=-20, y=-70, anchor="se")

        ttk.Label(frame_canciones, text="Lista de Canciones", font='arial 16 bold', bootstyle='inverse-dark').pack()

        sf_canciones = ScrolledFrame(frame_canciones, name='scrolledFrame1')
        # sf_canciones.hide_scrollbars()
        sf_canciones.pack(fill=BOTH, expand=YES)

        update_queue()

def update_queue():
    for child in window.winfo_children():  # root
        if child.winfo_name() == 'float_frame':  # float
            for widgets in child.winfo_children():
                if isinstance(widgets, ttk.Frame):
                    widgets.destroy()

            sf_canciones = ScrolledFrame(child, name='scrolledFrame1')
            # sf_canciones.hide_scrollbars()
            sf_canciones.pack(fill=BOTH, expand=YES)

            # TODO no llame si esta vacio songs_var
            songs = [ast.literal_eval(song) for song in ast.literal_eval(songs_var.get())]

            for it, song_data in enumerate(songs):  # TODO que una funcion haga esto
                song_frame = ttk.Frame(sf_canciones)
                number = ttk.Label(song_frame, text=f'{it + 1}', width=3, image=None, name=str(it), font='14')
                number.pack(side='left', padx=(20, 10))

                title = ttk.Label(song_frame, text=f'{song_data["title"]}', width=45, font='14')
                title.pack(side='left', padx=15)
                song_frame.pack(ipady=20, anchor='w', fill='x')



bottom_frame = ttk.Frame(window, bootstyle='dark', name='bottom_frame')
bottom_frame.pack(side='bottom', fill='x')
bottom_frame.config(height=90)

button_var = ttk.BooleanVar()
boton_mostrar_canciones = ttk.Button(bottom_frame, image=queue_image, command=mostrar_lista_canciones,
                                     textvariable=button_var, bootstyle='secondary')
boton_mostrar_canciones.pack(side='right', padx=10, pady=10)

# run
window.mainloop()
