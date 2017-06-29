from zope.interface import Interface
from zope.schema import DottedName, Int

# XXX This interface is currently not used.
# It's a draft for future componentization of kirbifetch

class IMetadataSource(Interface):
    """An online book metadata source."""
    
    name = DottedName(
            title = u"Name to identify source in metadata records",
            required = True,
        )
    
    max_ids_per_request = Int(
            title = u"Maximum number of ids per detail request",
            default = 1,
        )

    def buildBbookSearchURL(query):
            """Return the URL to be used to search for book ids."""

    def buildBookDetailsURL(book_id):
            """Return the URL to be used to get book details."""
            
    def buildMultipleBookDetailsURL(isbns):
            """Return the URL to be used to get details for multiple books."""

    def parseBookSearch(xml):
        """Extract the book ids referenced in a page."""
               
    def parseBookDetails(xml):
        """Extract book metadata from a book details page."""

    def parseMultipleBookDetails(xml):        
        """Extract book metadata from a response containing multiple records.
           This is only implemented when max_ids_per_request > 1.
           (Currently Amazon.com is the only source we know where this happens)
        """
    
    


