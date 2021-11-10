from sqlalchemy import text, String, literal, Unicode, case
from sqlalchemy.sql.elements import Null

from db import connection
from models.ad_groups import AdGroup
from models.campaigns import Campaign
from models.district import District
from models.hotels import Hotel
from models.keyword import Keyword
from models.negative import NegativeKeyword
from models.province import Province
from models.search import SearchKeyword
from stored import config


def conn(source):
    session = config.sessions.get(source, None)
    if session is None:
        session = connection.db(source)
        config.sessions[source] = session
    return session


class Filter:
    def __init__(self, campaign_name, adgroup_name, province_name, district_name, hotel_name, keyword_type):
        self.campaign = campaign_name
        self.adgroup = adgroup_name
        self.province = province_name
        self.district = district_name
        self.hotel = hotel_name
        self.keyword_type = keyword_type

        if self.campaign == 'Tất cả':
            self.campaign = None
        if self.adgroup == 'Tất cả':
            self.adgroup = None
        if self.province == 'Tất cả':
            self.province = None
        if self.district == 'Tất cả':
            self.district = None
        if self.hotel == 'Tất cả':
            self.hotel = None
        if self.keyword_type == 'Tất cả':
            self.keyword_type = None

    def get_keyword_list(self):
        campaign_id = get_campaign_id(self.campaign)
        adgroup_id = get_adgroup_id(self.adgroup)
        province_id = get_province_id(self.province)
        keyword_list = []
        if campaign_id is not None:
            campaign_id = campaign_id[0]
            # query = conn('default').execute(
            #     'SELECT nk.id, kw.word, kw.type, \'campaign\' as filter_by, \'negative\' as keyword_type, '
            #     '(SELECT name FROM ads.campaigns WHERE id = :campaign_id) as campaign_name '
            #     'FROM keywords.negative nk '
            #     'LEFT JOIN keywords.keyword kw ON nk.keyword_id = kw.id '
            #     'WHERE nk.campaign_id = :campaign_id',
            #     {'campaign_id': campaign_id}
            # ).all()

            query = conn('default').query(
                Keyword.id, Keyword.word, text(Keyword.type.name),
                literal("campaign", type_=Unicode).label('filter_by'),
                literal("negative", type_=Unicode).label('keyword_type'), Campaign.name
            )\
                .join(Keyword, Keyword.id == NegativeKeyword.keyword_id, isouter=True)\
                .join(Campaign, Campaign.id == NegativeKeyword.campaign_id, isouter=True)\
                .filter(NegativeKeyword.campaign_id == campaign_id)\
                .all()

            keyword_list.extend(query)

        if adgroup_id is not None:
            adgroup_id = adgroup_id[0]
            # query = conn('default').execute(
            #     'SELECT nk.id, kw.word, kw.type, \'ad_group\' as filter_by, \'negative\' as keyword_type, '
            #     '(SELECT name FROM ads.ad_groups WHERE id = nk.ad_group_id) as adgroup_name '
            #     'FROM keywords.negative nk '
            #     'LEFT JOIN keywords.keyword kw ON nk.keyword_id = kw.id '
            #     'WHERE nk.ad_group_id = :adgroup_id',
            #     {'adgroup_id': adgroup_id}
            # ).all()
            query = conn('default').query(
                Keyword.id, Keyword.word, text(Keyword.type.name),
                literal('ad_group', type_=Unicode).label('filter_by'),
                literal('negative', type_=Unicode).label('keyword_type'),
                AdGroup.name
            ).join(Keyword, Keyword.id == NegativeKeyword.keyword_id, isouter=True)\
                .join(AdGroup, AdGroup.id == NegativeKeyword.ad_group_id, isouter=True)\
                .filter(NegativeKeyword.ad_group_id == adgroup_id)\
                .all()
            keyword_list.extend(query)

            # query = conn('default').execute(
            #     'SELECT sk.id, kw.word, kw.type, \'ad_group\' as filter_by, \'positive\' as keyword_type, '
            #     '(SELECT name FROM ads.ad_groups WHERE id = sk.ad_group_id) as adgroup_name, '
            #     'CASE WHEN sk.target_type = \'hotels\' '
            #     'THEN (SELECT hotel_name FROM hotels.hotels WHERE id = sk.target_id) '
            #     'WHEN sk.target_type = \'district\' '
            #     'THEN (SELECT name FROM hotels.district WHERE id = sk.target_id) '
            #     'WHEN sk.target_type = \'province\' '
            #     'THEN (SELECT name FROM hotels.province WHERE id = sk.target_id) '
            #     'ELSE Null '
            #     'END as target_name, '
            #     'sk.target_type, kw.is_active '
            #     'FROM keywords.search sk '
            #     'LEFT JOIN keywords.keyword kw ON sk.keyword_id = kw.id '
            #     'WHERE sk.ad_group_id = :adgroup_id',
            #     {'adgroup_id': adgroup_id}
            # ).all()

            target_name = case([(SearchKeyword.target_type == 'hotels',
                                 conn('hotels').query(Hotel.hotel_name).filter(Hotel.id == SearchKeyword.target_id)),
                                (SearchKeyword.target_type == 'province',
                                 conn('hotels').query(Province.name).filter(Province.id == SearchKeyword.target_id)),
                                (SearchKeyword.target_type == 'district',
                                 conn('hotels').query(District.name).filter(District.id == SearchKeyword.target_id))],
                               else_=None)

            query = conn('default').query(
                Keyword.id, Keyword.word, text(Keyword.type.name),
                literal('ad_group', type_=Unicode).label('filter_by'),
                literal('positive', type_=Unicode).label('keyword_type'),
                AdGroup.name, SearchKeyword.target_type, target_name.label('target_name')
            ).join(Keyword, Keyword.id == SearchKeyword.keyword_id, isouter=True)\
                .join(AdGroup, AdGroup.id == SearchKeyword.ad_group_id, isouter=True)\
                .filter(SearchKeyword.ad_group_id == adgroup_id)\
                .all()
            keyword_list.extend(query)

        return keyword_list


def get_campaign_list():
    return conn('ads').query(Campaign.name).all()


def get_adgroup_list():
    return conn('ads').query(AdGroup.name).all()


def get_province_list():
    return conn('hotels').query(Province.name).all()


def get_district_list():
    return conn('hotels').query(District.name).all()


def get_hotel_list():
    return conn('hotels').query(Hotel.hotel_name).all()


def get_campaign_id(campaign_name):
    return conn('ads').query(Campaign.id).filter(Campaign.name == campaign_name).first()


def get_adgroup_id(adgroup_name):
    return conn('ads').query(AdGroup.id).filter(AdGroup.name == adgroup_name).first()


def get_province_id(province_name):
    return conn('hotels').query(Province.id).filter(Province.name == province_name).first()


def get_district_id(district_name):
    return conn('hotels').query(District.id).filter(District.name == district_name).first()


def get_hotel_id(hotel_name):
    return conn('hotels').query(Hotel.id).filter(Hotel.name == hotel_name).first()
