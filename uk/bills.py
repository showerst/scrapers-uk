import lxml.html
from pupa.scrape import Scraper, Bill, VoteEvent
from lxml import etree
from datetime import datetime
import pytz
from .utils import get_all_pages

# http://lda.data.parliament.uk/meta/bills/_id.json
# http://lda.data.parliament.uk/bills.json?session.displayName=2016-2017&_view=description&_pageSize=10&_page=0&originatingLegislature.prefLabel=House%20of%20Lords

class UKBillScraper(Scraper):
    api_base = 'http://lda.data.parliament.uk/'
    tz = pytz.timezone('Europe/London')

    def scrape(self,session=None,chamber=None):
        if not session:
            session = self.latest_session()
            self.info('no session specified, using %s', session)

        chambers = [chamber] if chamber else ['upper', 'lower']
        for chamber in chambers:
            print(chamber)
            yield from self.scrape_chamber(session, chamber)

    def scrape_chamber(self,session,chamber):
        # By default the description view is good, 
        # but pulling a few additional fields will save us queries later
        additional_fields = ['billPublications.homePage',
                             'billPublications.contentType',
                             'billPublications.date',
                             'billPublications.publicationType',
                             'billAmendment.homePage',
                             'billAmendment.contentType',
                             'billAmendment.date',
                             'billAmendment.publicationType',
                             'sponsors.legislature.prefLabel',
                             'sponsors.legislature.prefLabel',
                             'sponsors.member',
                             'sponsors.sponsorPrinted',
                             'billStages.billStageSittings.date',
                             'billStages.billStageType.label',
                             'billStages.billStageType.displayName',
                             'billStages.billStageType.formal',
                             'billStages.billStageType.provisional']

        # fields are collapsed into a single comma seperated url argument
        additional_fields = ','.join(additional_fields)

        url = "{}bills.json".format(self.api_base)
        url_args = {'session.displayName':session,
                    '_properties':additional_fields,
                    '_view':'description'}
        if 'upper' == chamber:
            url_args['originatingLegislature.prefLabel'] = 'House of Lords'
        elif 'lower' == chamber:
            url_args['originatingLegislature.prefLabel'] = 'House of Commons'

        pages = get_all_pages(url, url_args)

        for page in pages:
            print(page)
            page['title'] = page['title'].replace(' [HL]', '')
            bill = Bill(identifier=page['identifier']['_value'],
                        legislative_session=session,
                        title=page['label']['_value'],
                        classification='bill')
            
            if 'sponsors' in page:
                for sponsor in page['sponsors']:
                    bill.add_sponsorship(name=str(sponsor['sponsorPrinted']), 
                                        classification="Primary",
                                        entity_type="person",
                                        primary=True)
            
            for version in page['billPublications']:
                print(version)
                # Occasionally they publish version metadata with no link
                if 'homePage' in version:
                    if self.classify_version(version) == 'version':
                        bill.add_version_link(note=version['label']['_value'],
                                            url=version['homePage'],
                                            date=version['date']['_value'],
                                            media_type=version['contentType'],
                                            on_duplicate='ignore')
                    else:
                        bill.add_document_link(note=version['label']['_value'],
                                            url=version['homePage'],
                                            date=version['date']['_value'],
                                            media_type=version['contentType'],
                                            on_duplicate='ignore')
            
            bill.add_source(page['homePage'])
            yield bill

    def classify_version(self, version):
        if 'publicationType' in version:
            if version['publicationType']['_value'] == 'Bill' or version['publicationType']['_value'] == 'Amendment Paper':
                return 'version'
            else:
                return 'document'
        else:
            if 'bill' in version['label']['_value'].lower():
                return 'version'
        return 'document'