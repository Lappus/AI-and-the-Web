from whoosh.index import create_in
from whoosh.field import *

#Titel = URL?
schema = Schema(title=TEXT(stored=True), content=TEXT)
ix = create_in("indexdir", schema)
writer = ix.writer() #schreibt sachen in den Index

# adding documents
writer.add_document()

from whoosh.qparser import QueryParser
with ix.search() as searcher:
    query = QueryParser("content", ix.schema).parse("#Text we are searching")