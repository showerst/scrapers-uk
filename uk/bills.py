import lxml.html
from pupa.scrape import Scraper, Bill, VoteEvent
from lxml import etree
from datetime import datetime
import pytz


class UKBillScraper(Scraper):
    base_url = 'http://164.100.47.194/'
    search_url = 'http://164.100.47.194/Loksabha/Legislation/NewAdvsearch.aspx'
    tz = pytz.timezone('Europe/London')

    def scrape(self,session=None,chamber=None):
        if not session:
            session = self.latest_session()
            self.info('no session specified, using %s', session)
        
        chambers = [chamber] if chamber else ['upper', 'lower']
        for chamber in chambers:
            yield from self.scrape_chamber(session, chamber)
    
    def scrape_chamber(self,session,chamber):
        return