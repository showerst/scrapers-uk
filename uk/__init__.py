# coding: utf-8
from pupa.scrape import Organization
from pupa.scrape import Jurisdiction

from datetime import datetime

from .people import UKPersonScraper
from .bills import UKBillScraper

from .utils import get_all_pages

class UK(Jurisdiction):
    classification = 'legislature'
    division_id = 'ocd-division/country:uk'
    division_name = 'United Kingdom'
    name = 'Parliament of the United Kingdom'
    url = 'http://www.parliament.uk/'
    parties = [
        {'name': 'Conservative Party'},
    ]
    scrapers = {
        "people": UKPersonScraper,
        "bills": UKBillScraper,
    }

    # http://lda.data.parliament.uk/sessions.json
    legislative_sessions = [
        {"identifier":"2016-2017",
         "name":"2016-2017 Session",
         "start_date": "2016-05-18"}
    ]


    def get_organizations(self):
        parliament = Organization(self.name, classification=self.classification)
        yield parliament

        upper = Organization('House of Lords', classification='upper', parent_id=parliament)
        lower = Organization('House of Commons', classification='lower', parent_id=parliament)

        yield upper
        yield lower

    # def get_divisions(self):
    #     url_args = {'exists-endedDate':'false'}
    #     url = 'http://lda.data.parliament.uk/constituencies.json'

    #     areas = utils.get_all_pages(url, url_args)
    #     for area in areas:
    #         ocd_name = area['label']['_value']
    #         ocd_name = ocd_name.replace(' ', '-').lower()
    #         ocd_name = 'ocd-division/country:uk/{}/{}'.format(area['constituencyType'].lower(),
    #                                                           ocd_name)
    #         div = Division(
    #             id=ocd_name,
    #             country='uk',
    #             display_name=area['label']['_value']
    #         )
    #         yield div

        # for division in Division.get(self.division_id).children('ed'):
        #     if division.attrs.get('validFrom') and division.attrs['validFrom'] <= datetime.now().strftime('%Y-%m-%d'):
        #         lower.add_post(role='MP', label=division.name, division_id=division.id)
