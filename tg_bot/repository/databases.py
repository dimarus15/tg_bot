"""
Module with sqlite3 database structure
"""

from pony import orm

db = orm.Database()

class def_dtb():
    @staticmethod
    def get_dtb(name: str) -> db.Entity:
        if name == 'DesiredFilm':
            return DesiredFilm
        elif name == 'WatchedFilm':
            return WatchedFilm
        elif name == 'User':
            return User

def convert_from_py2sqlite(data):
    if isinstance(data, int) and data == -1000:
        return None
    else:
        return data

class User(db.Entity):
    pk = orm.PrimaryKey(int, auto=True)
    username = orm.Required(str, 30)
    desired_film_list = orm.Required(str, 100)
    watched_film_list = orm.Required(str, 100)

    def get_data(self):
        return {
            'pk': convert_from_py2sqlite(self.pk),
            'username': self.username,
            'film_lists': self.film_lists
        }

class DesiredFilm(db.Entity):
    pk = orm.PrimaryKey(int, auto=True)
    title = orm.Required(str, 100)
    release_year = orm.Required(int)
    priority = orm.Required(int)

    def get_data(self):
        return {
            'pk': convert_from_py2sqlite(self.pk),
            'title': self.title,
            'release_year': self.release_year,
            'priority': self.priority
        }

class WatchedFilm(db.Entity):
    pk = orm.PrimaryKey(int, auto=True)
    title = orm.Required(str, 100)
    release_year = orm.Required(int)
    rate = orm.Required(int)
    comment = orm.Optional(str, 500)

    def get_data(self):
        return {
            'pk': convert_from_py2sqlite(self.pk),
            'title': self.title,
            'release_year': self.release_year,
            'rate': self.rate,
            'comment': self.comment
        }