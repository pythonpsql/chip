#! /usr/bin/env python3
from database import Database, CursorFromConnectionFromPool as conn
import common_functions as cf



if __name__ == "__main__":
    Database.initialise(database='chip', host='localhost', user='dba_tovak')
    while True:
        place = cf.prompt_("Enter place: ", cf.get_completer_list("place", "customer"))
        if place == "q":
            break
        if place == "a":
            with conn() as cursor:
                cursor.execute("select date_, place from tour")
                all_ = cursor.fetchall()
            cf.pretty_(['Date', 'Place'], all_)
            continue
        date_ = cf.prompt_("Enter date: ", [], default_="2018-")
        if date_:
            with conn() as cursor:
                cursor.execute("insert into tour (place, date_) values (%s, %s) returning date_, place", (place, date_))
                result = cursor.fetchall()
            cf.pretty_(['Date', 'Place'], result)
        else:
            print("No changes were made")
    print("Bye!")

