
from __future__ import unicode_literals
from database import Database, CursorFromConnectionFromPool as conn
from six import string_types
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit import prompt
from fuzzyfinder import fuzzyfinder as ff
import common_functions as cf
import owner

__all__ = (
    'WordCompleter',
)


class WordCompleter(Completer):
    def __init__(self, words, ignore_case=False, meta_dict=None, WORD=False,
                 sentence=False, match_middle=False, no_of_sugg=30, invoice_list = None, invoice_type =None, meta_dict_two = None ):
        assert not (WORD and sentence)

        self.words = list(words)
        self.ignore_case = ignore_case
        self.meta_dict = meta_dict or {}
        self.meta_dict_two =  meta_dict_two or {}
        self.WORD = WORD
        self.sentence = sentence
        self.match_middle = match_middle
        self.no_of_sugg = no_of_sugg
        self.invoice_list = invoice_list
        assert all(isinstance(w, string_types) for w in self.words)

    def get_completions(self, document, complete_event):
        # Get word/text before cursor.
        if self.sentence:
            word_before_cursor = document.text_before_cursor
        else:
            word_before_cursor = document.get_word_before_cursor(WORD=self.WORD)

        if self.ignore_case:
            word_before_cursor = word_before_cursor.lower()

        if word_before_cursor.startswith("/"):
            if self.invoice_list:
                for a in self.invoice_list:
                    display_meta = self.meta_dict_two.get(str(a), '')
                    yield Completion("/" +  str(a), -len(word_before_cursor), display_meta=display_meta)
        elif word_before_cursor.startswith("."):
            word_before_cursor = word_before_cursor[1:]
            for a in self.words:
                if word_before_cursor in a.lower():
                # if a.lower().find(word_before_cursor) != -1:
                    display_meta = self.meta_dict.get(a, '')
                    yield Completion(a, -len(word_before_cursor), display_meta=display_meta)
        else:
            result = list(ff(word_before_cursor, [w.lower() for w in self.words]))
            # fuzzy search breaks completion sorting
            l_result = len(result)
            l = l_result if l_result < self.no_of_sugg else self.no_of_sugg
            for i in range(l):
                a = result[i]
                for b in self.words:
                    if a == b.lower():
                        display_meta = self.meta_dict.get(b, '')
                        yield Completion(b, -len(word_before_cursor), display_meta=display_meta)



if __name__ == "__main__":
    Database.initialise(database='chip', host='localhost', user='dba_tovak')
    # invoice_list = owner.get_filter_result("Search By Nickname", invoice_type)
    invoice_list  = owner.get_filter_result("All Invoices", "sale_invoice")
    invoice_dict = {}
    for a in invoice_list:
        invoice_dict[str(a[0])] = "{}, {}, {}, {}".format(str(a[1]), str(a[2]), str(a[3]), str(a[4]))

    completer = WordCompleter(["Connection Pipe 18", "Connection Wired 18", "Connection PVC Heavy 18", "Connection PVC Heavy 24"],sentence=True, match_middle=True, ignore_case=True, invoice_list=[*invoice_dict], meta_dict_two=invoice_dict )
    result = prompt("Enter input: ", completer=completer)

    """
    Simple autocompletion on a list of words.

    :param words: List of words.
    :param ignore_case: If True, case-insensitive completion.
    :param meta_dict: Optional dict mapping words to their meta-information.
    :param WORD: When True, use WORD characters.
    :param sentence: When True, don't complete by comparing the word before the
        cursor, but by comparing all the text before the cursor. In this case,
        the list of words is just a list of strings, where each string can
        contain spaces. (Can not be used together with the WORD option.)
    :param match_middle: When True, match not only the start, but also in the
                         middle of the word.
    """
