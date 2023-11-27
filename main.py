import ast
import tkinter
import PIL.Image
import pygame as pg
import multiprocessing
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
# window.state('zoomed')

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
    dll.push(song_data)
    play()


# TODO si termina la barra de reproduccion hacer el pop y update
def play():
    song: tuple[str, dict, PIL.Image.Image] = dll.get()
    pg.mixer_music.load(song[0])
    pg.mixer_music.play(1)  # TODO buscar algo que siempre se este actualizando que verifique si paso o esta reproduciendo la siguiente cancion
    # TODO o sino en lugar de hacer pg.mixer_music.queue(song_data[0]) , no hacer queue y cada que verifique que se termino una cancion volver a llamar play()
    # TODO si empezo la siguiente cancion de la lista quitar su tiempo de el maximo y quitar el error, probablemente se quite solo con el update_queue()
    dll.pop()  # TODO al agregar a queue (funcion abajo) o hacer play hacer que se actualice el frame de queue
    songs_var.set(dll.display(wdata='dict'))
    update_queue()


def add_to_queue(song_data: tuple[str, dict, PIL.Image.Image]):
    if (time_var.get() + song_data[1]['duration']) <= 900:
        time_var.set(time_var.get() + song_data[1]['duration'])
        dll.append(song_data)
        songs_var.set(dll.display(wdata='dict'))
        pg.mixer_music.queue(song_data[0])
        update_queue()
        if not pg.mixer_music.get_busy():
            time_var.set(time_var.get() - song_data[1]['duration'])
            play()
    else:
        time_limit()


# cant be pickled
play_image = open_img('assets/play.png')
add_queue_image = open_img('assets/add_queue.png')
queue_image = open_img('assets/queue.png')

# add 0 to one-digit numbers as str
add = lambda x: '0' + str(x) if len(str(x)) == 1 else x

# set app sizes for low res
fhd = [60, 45, 25, 25, 600]
hd = [40, 30, 10, 15, 450]
res: list[int] = hd if window.winfo_width() < 1880 else fhd

# main frame with scroller
sf = ScrolledFrame(window, name='main_sf')
sf.hide_scrollbars()
sf.pack(fill=BOTH, expand=YES)

# double linked list st
dll = DLL()
songs_var = ttk.StringVar()
songs_var.set(dll.display(wdata='dict'))
time_var = ttk.IntVar()

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
        frame_canciones.place(relx=1.0, rely=1.0, x=-20, y=-70, anchor="se")

        ttk.Label(frame_canciones, text="Lista de Canciones", font='arial 16 bold', bootstyle='inverse-dark', name='label_lista_canciones').pack()
        ttk.Label(frame_canciones, text=f'{add(time_var.get() // 60)}:{add(time_var.get() % 60)}', font='arial 16 bold', bootstyle='inverse-dark', name='tiempo').pack()

        sf_canciones = ScrolledFrame(frame_canciones, name='frame_scroll')
        sf_canciones.hide_scrollbars()
        sf_canciones.pack(fill=BOTH, expand=YES)

        update_queue()


def update_queue():
    if button_var.get():
        sf_widget = window.nametowidget('.float_frame.!frame.frame_scroll')
        window.nametowidget('.float_frame.tiempo')['text'] = f'{add(time_var.get() // 60)}:{add(time_var.get() % 60)}'
        for child in sf_widget.winfo_children():
            child.destroy()

        try:
            songs = [ast.literal_eval(song) for song in ast.literal_eval(songs_var.get())]

            for it, song_data in enumerate(songs):
                song_frame = ttk.Frame(sf_widget, name=f'song{it}')
                number = ttk.Label(song_frame, text=f'{it + 1}', width=3, image=None, name=str(it), font='14')
                number.pack(side='left', padx=(20, 10))

                title = ttk.Label(song_frame, text=f'{song_data["title"]}', width=45, font='14')
                title.pack(side='left', padx=15)
                song_frame.pack(ipady=20, anchor='w', fill='x')
        except SyntaxError:
            ...


def time_limit():
    if button_var.get():
        sf_widget = window.nametowidget('.float_frame.!frame.frame_scroll')

        error_frame = ttk.Frame(sf_widget, name='error_frame')
        title = ttk.Label(error_frame, text='Tiempo limite alcanzado: maximo 15 minutos', width=45, font='20', bootstyle='danger')
        title.pack(side='left', padx=15)
        error_frame.pack(ipady=20, anchor='w', fill='x')


bottom_frame = ttk.Frame(window, bootstyle='dark', name='bottom_frame')
bottom_frame.pack(side='bottom', fill='x')
bottom_frame.config(height=90)

button_var = ttk.BooleanVar()
boton_mostrar_canciones = ttk.Button(bottom_frame, image=queue_image, command=mostrar_lista_canciones,
                                     textvariable=button_var, bootstyle='secondary')
boton_mostrar_canciones.pack(side='right', padx=10, pady=10)

# run
window.mainloop()
