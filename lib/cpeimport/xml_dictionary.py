import xml.sax
from .base import CPEImportHandler


class XMLCPEHandler(CPEImportHandler, xml.sax.ContentHandler):
    """Handler for legacy XML CPE format."""

    def __init__(self, rdb):
        super().__init__(rdb)
        xml.sax.ContentHandler.__init__(self)
        self.record = {}
        self.refs = []
        self.title = ""
        self.title_seen = False

    def _parse_impl(self, filepath):
        parser = xml.sax.make_parser()
        parser.setContentHandler(self)
        parser.parse(filepath)

    def startElement(self, tag, attributes):
        if tag == "cpe-23:cpe23-item":
            self.record["cpe-23"] = attributes["name"]
        if tag == "title":
            self.title_seen = True
        if tag == "reference":
            self.refs.append(attributes["href"])

    def characters(self, data):
        if self.title_seen:
            self.title += data

    def endElement(self, tag):
        if tag == "title":
            self.record["title"] = self.title
            self.title = ""
            self.title_seen = False
        if tag == "references":
            self.record["refs"] = self.refs
            self.refs = []
        if tag == "cpe-item":
            self.process_cpe(self.record["cpe-23"])
            self.record = {}
