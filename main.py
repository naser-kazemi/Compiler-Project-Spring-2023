class Dummy:

    def call_routine(self, name, token):
        name = name.replace("#", "")
        routine = self.__getattribute__(name)
        if routine.__code__.co_argcount == 2:
            routine(token)
        else:
            routine()

    def test(self, token):
        print(token)

    def test2(self):
        print("test2")


if __name__ == "__main__":
    d = Dummy()
    d.call_routine("test", "token is test")
    d.call_routine("test2", "token is test")
