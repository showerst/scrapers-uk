
import lxml.html
from pupa.scrape import Scraper, Person
from lxml import etree
import json
from .utils import get_all_pages

class UKPersonScraper(Scraper):
    # http://lda.data.parliament.uk/commonsmembers.json?_pageSize=50
    # http://lda.data.parliament.uk/lordsmembers.json?_pageSize=50
    # http://lda.data.parliament.uk/members.json?_pageSize=500
    # http://lda.data.parliament.uk/members.json

    #http://lda.data.parliament.uk/constituencies.json?exists-endedDate=false
    api_base = 'http://lda.data.parliament.uk/'


    def scrape(self):
        yield self.scrape_lower()

    def scrape_lower(self):
        url = "{}commonsmembers.json".format(self.api_base)
        members = get_all_pages(url)
        for member in members:
            person = Person(name=member['fullName']['_value'],
                            district=member['constituency']['label']['_value'],
                            role="Member",
                            primary_org="House of Commons"
                           )
            person.add_source(url=member['_about'])
            yield person
