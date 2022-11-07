import unittest

from rdflib import Graph, URIRef


class RDFLIBCacheBugTestCase(unittest.TestCase):
    def test_cache_bug(self):
        g = Graph()
        # Prime the cache w/ myns
        g.parse(data="""
@prefix MYNS: <http://funkyurl.org/> .
MYNS:Foo a MYNS:Bar .""")
        g.serialize(format="turtle")

        # Remove MYNS
        g.bind('YOURNS', 'http://funkyurl.org/')
        # Re-add MYNS with a different URL
        g.bind('MYNS', 'http://gotcha.org/', replace=True)
        g.add((URIRef('http://funkyurl.org/SAM'), URIRef('http://funkyurl.org/SAM'), URIRef('http://funkyurl.org/SAM')))
        print(g.serialize(format="turtle"))


if __name__ == '__main__':
    unittest.main()
