import unittest

from rdflib import Graph, URIRef


class RDFLIBCacheBugTestCase(unittest.TestCase):
    def test_cache_bug(self):
        g = Graph()
        # Prime the cache w/ myns
        g.parse(data="""
@prefix MYNS: <http://funkyurl.org/> .
MYNS:Foo a MYNS:Bar .""", format="turtle")
        g.serialize(format="turtle")

        # Remove MYNS
        g.bind('YOURNS', 'http://funkyurl.org/')
        # Re-add MYNS with a different URL
        g.bind('MYNS', 'http://gotcha.org/', replace=True)
        g.add((URIRef('http://funkyurl.org/SAM'), URIRef('http://funkyurl.org/SAM'), URIRef('http://funkyurl.org/SAM')))
        self.assertEqual("""@prefix MYNS: <http://funkyurl.org/> .
@prefix YOURNS: <http://funkyurl.org/> .

MYNS:Foo a MYNS:Bar .

YOURNS:SAM YOURNS:SAM YOURNS:SAM .""", g.serialize(format="turtle").decode().strip())


if __name__ == '__main__':
    unittest.main()
