=============================
Kirbi: a P2P library manager
=============================

Kirbi is a sample application to test Grok and help programmers learn
how to use it to build a complete app.

Kirbi also aims to be useful and not just a sample. It is a system to allow
friends and colleagues to share their books and DVDs without losing track
of them.

Use cases
===========

Done
-----

* Add books to the public catalog via a Web form or XML-RPC

* Allow searches to the public catalog

* Add books by entering just the ISBN, and letting Kirbi fetch the book data
  from Amazon.com

* User self-registration

* User catalogs own collection

To Do
------

* User invites friends to share specific collections

* User requests to borrow an item

* User approves the loan of an item

* User tracks lent items

* User tracks borrowed items

* Add books by entering title words or author names, and letting Kirbi fetch
  some likely candidates from Amazon.com

* User adds book which belongs to a friend, who maybe a current user or someone
  to be invited (recovering a lost book is a very strong motivation to join!)

Features
==============

This is a list of other use cases, organized by view.

app/index
-------------

* implement recent additions

pac/index
-------------

For each item listed:

* button: "i own it/add to my collection"

* button: "borrow"

* list: owners

* display: rating

book/index
------------

* button: "i own it/add to my collection"

* button: "borrow"

* list: owners

* button: "recommend" (to a friend/to yourself also?)

* display: rating

* control: "rate it"

* list: reviews

* button: "review"

* button: rate review

* display: tags

* control: "tag"

* button: "liberate"

user/menu
-------------

(currently this is part of app/master and not a separate view)

* link: invite

* link: preferences

user/index
------------

(currently this is part of collection/index and not a separate view)

* list: lease requests/due

* list: borrow requests/due

* list: recent invitations (pending/accepted)

* list: recomendations for you

item/borrow
--------------

* list: alternative manifestations based on OCLC xISBN service

* control: duration needed

* text area: suggested time/place for pickup

item/lend
---------------

* control: duration approved

* text area: edit suggested time/place for pickup

* control: date when available

* button: approve

* text line: reason for denial

* button: deny

new views
-------------

* manage invitations

* preferences (at least passwd change; default lease time; create
    alternative collecions; privacy)

