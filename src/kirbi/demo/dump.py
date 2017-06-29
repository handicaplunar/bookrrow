#!/usr/bin/env python

import sys
from pprint import pprint
#               0       1       2       3       4       5       6   7
book_fields = "book_id isbn13 title edition publisher issued name role".split()


def dump():
    import MySQLdb
    db = MySQLdb.connect(host="localhost", user="luciano", passwd=sys.argv[1],
        db="horde")
    cursor = db.cursor()
    sql = """SELECT 
                bk.book_id , bk.isbn13 , bk.title ,
                bk.edition , bk.publisher , bk.issued ,
                cr.name , lbc.role, lbc.citation_order
            FROM 
                groo_books AS bk
            LEFT JOIN (
                    groo_creators AS cr,
                    groo_l_book_creator AS lbc
                ) ON (
                    bk.book_id = lbc. book_id
                    AND 
                    cr.creator_id = lbc.creator_id
                )
            WHERE
                not isnull(bk.title)
            ORDER BY 
                bk.isbn13, lbc.citation_order
          """
    cursor.execute(sql)
    #pprint(cursor.description)
    books = {}
    while True:
        record = cursor.fetchone()
        if record is None: break
        book_id = record[0]
        if book_id in books:
            rec = books[book_id]
            role = record[7]
            if role == 'author':
                rec['name'] += u'|' +record[6].strip().decode('utf-8')
            else:
                rec['name'] += u'|%s (%s)' % (record[6].strip().decode('utf-8'),
                                              record[7].strip().decode('utf-8'))
        else:        
            rec = {}
            for i, field in enumerate(book_fields):
                value = record[i]
                if field == 'book_id':
                    book_id = value = record[i]               
                else:
                    if value is not None:
                        value = record[i].strip().decode('utf-8')
                    if field == 'name':
                        name = value
                    if field == 'role' and value != 'author':
                        rec['name'] = u'%s (%s)' % (name, value)
                    if field != 'role':
                        rec[field] = value
                    books[book_id] = rec
    
    books2 = []
    for book in books.values():
        books2.append(book)
    pprint(books2)
    
def dump_tr():
    import MySQLdb
    db = MySQLdb.connect(host="localhost", user="luciano", passwd=sys.argv[1],
        db="horde")
    cursor = db.cursor()

        
if __name__=='__main__':
    # dump()
    dump_tr()