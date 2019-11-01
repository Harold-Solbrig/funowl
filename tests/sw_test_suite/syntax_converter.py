"""
OWL format conversion tool.

This converter uses them Linked Data Finland server to convert OWL in any of a variety of format.
"""
import logging
from enum import Enum, auto
from typing import Optional

import requests


class OWLFormat(Enum):
    ttl = auto()
    rdfxml = auto()
    func = auto()
    manc = auto()
    owlxml = auto()
    latex = auto()
    krss2 = auto()


def convert(content: str, output_format: OWLFormat=OWLFormat.func) -> Optional[str]:
    try:
        resp = requests.post('http://www.ldf.fi/service/owl-converter/',
                             data=dict(onto=content, to=output_format.name))
    except ConnectionError as e:
        logging.getLogger().error(str(e))
        return None

    if resp.ok:
        return resp.text
    logging.getLogger().error(str(resp))


if __name__ == '__main__':
    print(convert("""<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:owl="http://www.w3.org/2002/07/owl#"
    xmlns:first="http://www.w3.org/2002/03owlt/SymmetricProperty/premises001#"
    xmlns:second="http://www.w3.org/2002/03owlt/SymmetricProperty/conclusions001#"
    xml:base="http://www.w3.org/2002/03owlt/SymmetricProperty/premises001" >

    <rdf:Description rdf:about="premises001#Ghent">
        <first:path rdf:resource="premises001#Antwerp"/>
    </rdf:Description>

    <owl:SymmetricProperty rdf:about="premises001#path"/>

</rdf:RDF>"""))
