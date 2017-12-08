
import lxml.html
from pupa.scrape import Scraper, Person
from lxml import etree
import json
from .utils import get_all_pages
import pprint

class UKPersonScraper(Scraper):
    # http://lda.data.parliament.uk/commonsmembers.json?_pageSize=50
    # http://lda.data.parliament.uk/lordsmembers.json?_pageSize=50
    # http://lda.data.parliament.uk/members.json?_pageSize=500

    # http://data.parliament.uk/membersdataplatform/services/mnis/Department/0/Government/Current/
    # http://data.parliament.uk/membersdataplatform/services/mnis/HouseOverview/Commons/2012-01-01/

    # TODO: This looks like a better source...
    # http://data.parliament.uk/membersdataplatform/memberquery.aspx#outputs
    # http://data.parliament.uk/membersdataplatform/services/mnis/members/query/house=Commons/BasicDetails/
    # http://data.parliament.uk/membersdataplatform/services/mnis/members/query/House=Commons%7CIsEligible=true/Addresses/
    # http://data.parliament.uk/membersdataplatform/services/mnis/members/query/House=Commons%7CIsEligible=true/Addresses%7CConstituencies%7CStaff/

    api_base = 'http://lda.data.parliament.uk/'

    def scrape(self):
        yield self.scrape_lower()
        yield self.scrape_upper()

    def scrape_lower(self):
        # I haven't found a way to filter the API by Active,
        # but it returns more metadata. So scrape the web version
        # then cross-ref.
        web_url = 'http://www.parliament.uk/mps-lords-and-offices/mps/'
        page = lxml.html.fromstring(self.get(url=web_url).content)
        member_rows = page.xpath('//div[@id="pnlListing"]/table//tr[@id]/td[1]/a/@href')
        member_ids = []
        for row in member_rows:
            member_ids.append(row.rsplit('/', 1)[-1])

        url = "{}commonsmembers.json".format(self.api_base)
        url_args = {'exists-constituency':'true',
                    '_properties':'birthDate,deathDate'}
        members = get_all_pages(url, url_args)

        for member in members:
            member_id = member['_about'].rsplit('/', 1)[-1]
            if member_id in member_ids:
                person = Person(name=member['fullName']['_value'],
                                district=member['constituency']['label']['_value'],
                                role="Member",
                                primary_org="House of Commons")
                person = self.add_extras(member, person)
                person.add_source(url=member['_about'])
                yield person

    def scrape_upper(self):
        web_url = 'http://www.parliament.uk/mps-lords-and-offices/lords/'
        page = lxml.html.fromstring(self.get(url=web_url).content)
        member_rows = page.xpath('//div[@id="pnlListing"]/table//tr[@id]/td[1]/a/@href')
        member_ids = []
        for row in member_rows:
            member_ids.append(row.rsplit('/', 1)[-1])

        url = "{}lordsmembers.json".format(self.api_base)
        url_args = {'_properties':'birthDate,deathDate'}
        members = get_all_pages(url, url_args)
        for member in members:
            member_id = member['_about'].rsplit('/', 1)[-1]
            if member_id in member_ids:
                person = Person(name=member['fullName']['_value'],
                                role="Member",
                                primary_org="House of Lords",
                            )
                person = self.add_extras(member, person)
                person.add_source(url=member['_about'])
                yield person

    def add_extras(self, member, person):
        person.extras = {'family_name':member['familyName']['_value'],
                         'sort_name':member['familyName']['_value'],
                        }

        if 'birth_date' in member:
            person.birth_date = member['birthDate']['_value']

        if 'death_date' in member:
            person.death_date = member['deathDate']['_value']

        if 'gender' in member:
            person.gender = member['gender']['_value']

        if 'givenName' in member:
            person.extras['given_name'] = member['givenName']['_value']

        if 'party' in member:
            person.extras['party'] = member['party']['_value']

        if 'twitter' in member:
            if member['twitter']['_value'][0:4] != 'http':
                member['twitter']['_value'] = 'https://twitter.com/{}'.format(member['twitter']['_value'])
            person.links.append({'note':'twitter', 'url': member['twitter']['_value']})

        if 'homepage' in member:
            person.links.append({'note':'Home Page', 'url':member['homepage']})

        return person
