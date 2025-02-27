# acces db  : products and stats
import sqlite3


def get_product_info(item_idx):
    # print("inside get_class_item")
    con = sqlite3.connect("data/projet_balance")
    cur = con.cursor()
    # print("after con/cursor")
    try:
        cur.execute("SELECT label,price,type  FROM products WHERE id = ?", (item_idx,))
        label, price, type = cur.fetchone()
    except Exception as e:
        print("error in get_product_info", e)
        return "error", 0, "error"

    con.close()
    return label, price, type
