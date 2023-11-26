import io
import os
import pickle
import hashlib
from tinytag import TinyTag
from PIL import Image, ImageTk


class music:
    def list_songs(self, music_directory="music\\") -> list[tuple[str, dict, Image.Image]]:
        """
                Load song from the given folder

                :return:
                    A list of tuples where each tuple consists of a string representing the full path of the song,
                    a dictionary containing the song tags, and an image representing the album cover
                """
        directory = music_directory
        hash_ = self.__hash_files(directory)

        try:
            with open('assets/music.pkl', 'rb') as f:
                loaded_data: dict = pickle.load(f)
                loaded_hash = loaded_data.get('hash_')
                loaded_music_list = loaded_data.get('music_list')
        except (FileNotFoundError, pickle.UnpicklingError):
            loaded_hash = None
            loaded_music_list = None

        if hash_ == loaded_hash:
            images = []
            for val in loaded_music_list:
                images.append(self.__load_img(val[2]))
            data = [(path, tags, loaded_img) for (path, tags, _), loaded_img in zip(loaded_music_list, images)]
            return data
        else:
            music_list = []
            for song in os.listdir(directory):
                full_dir = directory + song
                music_list.append((full_dir, TinyTag.get(full_dir).as_dict(), Image.open(io.BytesIO(TinyTag.get(full_dir, image=True).get_image()))))

            data = {'hash_': hash_, 'music_list': music_list}

            with open('assets/music.pkl', 'wb') as f:
                pickle.dump(data, f)

            return music_list

    def __hash_files(self, dir_):
        return hashlib.sha256("".join(
            [f for f in os.listdir(dir_) if os.path.isfile(os.path.join(dir_, f))]).encode()).hexdigest()

    def __load_img(self, img: Image.Image, width: int = 45, height: int = 45):
        res_img = img.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(res_img)