from utils import *

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
    import pickle
     # = open("assets/grammar_with_actions.txt")
    # pickle.dump(file.readlines(), open("assets/grammar_with_actions.pkl", "wb"))
    rule = convert_grammar_to_rule_dict("assets/grammar.txt")
    pickle.dump(rule, open("assets/grammar.pkl", "wb"))
