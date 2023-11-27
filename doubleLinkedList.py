import PIL.Image


class Node:
    """
        Nodo para listas enlazadas.
    """

    def __init__(self, path: str, title: str, author: str, album: str, duration: float, image: PIL.Image.Image):
        """
                Inicializa un nodo.

                Args:
                    path (str): La ruta de la cancion.
                    title (str): El título de la cancion.
                    author (str): El autor de la cancion.
                    album (str): El album de la cancion.
                    duration (float): La duración de la cancion en segundos.
                    image (PIL.Image.Image): La imagen del album.
                Attributes:
                    self.prev (Node): El nodo previo en la lista doblemente enlazada.
                    self.path (str): La ruta de la cancion.
                    self.title (str): El título de la cancion.
                    self.author (str): El autor de la cancion.
                    self.album (str): El album de la cancion.
                    self.duration (float): La duración de la cancion en segundos.
                    self.image (PIL.Image.Image): La imagen del album.
                    self.next (Node): El nodo siguiente en la lista doblemente enlazada.
                """
        self.prev: Node = None
        self.path: str = path
        self.title: str = title
        self.author: str = author
        self.album: str = album
        self.duration: float = duration
        self.image: PIL.Image.Image = image
        self.next: Node = None


class DLL:
    """
    Clase para listas doblemente enlazadas
    """

    def __init__(self):
        """
            Inicializa la clase de lista doblemente enlazada.

            Attributes:
                self.head (Node) : El nodo cabeza en la lista doblemente enlazada.
                self.foot (Node) : El nodo final en la lista doblemente enlazada.
        """
        self.head: Node = None
        self.foot: Node = None

    def append(self, data: tuple[str, dict, PIL.Image.Image]):
        """
            Agrega un elemento al final de la lista

            Args:
                path (str): La ruta de la cancion.
                dict {
                "title" (str): El título de la cancion.
                "author" (str): El autor de la cancion.
                "album" (str): El album de la cancion.
                "duration" (float): La duración de la cancion en segundos. }
                image (PIL.Image.Image): La imagen del album.
            Example:
                Para poner el titulo y duracion de la cancion:\n
                append("Everybody Wants To Rule The World", 251)

        """
        if self.foot is None:
            self.head = Node(data[0], data[1]['title'], data[1]['artist'], data[1]['album'], data[1]['duration'],
                             data[2])
            self.foot = self.head
        else:
            new_node: Node = Node(data[0], data[1]['title'], data[1]['artist'], data[1]['album'], data[1]['duration'],
                                  data[2])
            self.foot.next = new_node
            new_node.prev = self.foot
            new_node.next = None
            self.foot = new_node

    def pop(self) -> bool:
        """
            Elimina el primer elemento de la lista doblemente enlazada.

            Returns:
                 bool: True si se eliminó un elemento, False si la lista está vacía y no se eliminó nada.
        """
        if self.foot is None:
            return False
        elif self.head.next is None:
            self.head = self.foot = None
            return True
        else:
            current: Node = self.head
            self.head: Node = current.next
            current.next = None
            self.head.prev = None
            return True

    def get(self) -> tuple[str, dict, PIL.Image.Image] or None:
        """
        Obtiene el título y la duración del primer elemento de la lista doblemente enlazada, si se confirma la acción.

        :returns:
            tuple[str, dict, PIL.Image.Image] or None; La tupla contiene:
            path (str): La ruta de la cancion.
            dict {
                "title" (str): El título de la cancion.
                "author" (str): El autor de la cancion.
                "album" (str): El album de la cancion.
                "duration" (float): La duración de la cancion en segundos. }
            image (PIL.Image.Image): La imagen del album.
            Si la confirmación es exitosa, o None si no hay elementos en la lista.
        """
        if self.head is None:
            return None
        else:
            data: dict = {
                'title': self.head.title,
                'artist': self.head.author,
                'album': self.head.album,
                'duration': self.head.duration
            }
            return self.head.path, data, self.head.image

    def delete(self, index: int) -> bool:
        """
            Elimina el elemento dado el indice en la lista doblemente enlazada.

            Args:
                 index (int) : El indice del elemento a eliminar. Debe ser mayor a 0 y existir en la lista

            Returns:
                bool: True si se eliminó el elemento, False si la lista está vacía y no se eliminó nada
                o el indice es menor a 0.

            Example:
                Para borrar un elemento dado n:\n
                delete(2)
        """
        if self.foot is None or index < 0:
            return False
        elif self.head.next is None:
            self.head = self.foot = None
            return True
        else:
            i = 0
            current: Node = self.head
            while current is not None and i < index:
                current = current.next
                i += 1

            if current is not None:
                prev_node: Node = current.prev
                next_node: Node = current.next

                if prev_node:
                    prev_node.next = next_node
                else:
                    self.head = next_node

                if next_node:
                    next_node.prev = prev_node
                else:
                    self.foot = prev_node

                current.prev = current.next = None

                return True

            return False

    def display(self, order: str = 'asc', **kwargs):
        """
            Muestra los elementos de la lista en orden ascendente o descendente.

            Args:
                order (str): El tipo de ordenamiento a aplicar. Debe ser "asc" para ascendente o "desc" para descendente
            Returns:
                Lista de tuplas con:
                title (str): El título de la cancion.
                author (str) : El autor de la cancion.
                album (str) : El album de la cancion.
                duration (int): La duración de la cancion en segundos.
                image (PIL.Image.Image) : La imagen del album.
            Example:
                Para mostrar la lista en orden ascendente:\n
                display("asc")
                \n
                Para mostrar la lista en orden descendente:\n
                display("desc")
            """
        wdata = kwargs.get('wdata', str)
        full_list: list[tuple[str, str, str, float, PIL.Image.Image]] = []
        if order == 'asc':
            current: Node = self.head
            while current is not None:
                data: dict = {
                    'title': current.title,
                    'artist': current.author,
                    'album': current.album,
                    'duration': current.duration
                }
                if wdata == 'str':
                    full_list.append(current.path)
                elif wdata == 'dict':
                    full_list.append(data)
                elif wdata == 'img':
                    full_list.append(current.image)
                else:
                    full_list.append((current.path, data, current.image))
                current = current.next
            return full_list
        elif order == 'desc':
            current: Node = self.foot
            while current is not None:
                data: dict = {
                    'title': current.title,
                    'artist': current.author,
                    'album': current.album,
                    'duration': current.duration
                }
                if wdata == 'str':
                    full_list.append(current.path)
                elif wdata == 'dict':
                    full_list.append(data)
                elif wdata == 'img':
                    full_list.append(current.image)
                else:
                    full_list.append((current.path, data, current.image))
                current = current.prev
            return full_list

    def push(self, data: tuple[str, dict, PIL.Image.Image]):
        """
        Inserta un nodo al inicio de la lista
        :param:
            path (str): La ruta de la cancion.
            dict {
            "title" (str): El título de la cancion.
            "author" (str): El autor de la cancion.
            "album" (str): El album de la cancion.
            "duration" (float): La duración de la cancion en segundos. }
            image (PIL.Image.Image): La imagen del album.
        """
        new_node = Node(data[0], data[1]['title'], data[1]['artist'], data[1]['album'], data[1]['duration'], data[2])
        new_node.next = self.head
        new_node.prev = None
        if self.head is not None:
            self.head.prev = new_node
        self.head = new_node
        self.foot = new_node
