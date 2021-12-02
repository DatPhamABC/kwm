from sqlalchemy import literal, Unicode, case, asc, delete, and_, or_

from keywordmanager.db.session import conn
from keywordmanager.models.ads.ad_groups import AdGroup
from keywordmanager.models.ads.campaigns import Campaign
from keywordmanager.models.hotels.district import District
from keywordmanager.models.hotels.hotels import Hotel
from keywordmanager.models.keywords.keyword import Keyword
from keywordmanager.models.keywords.negative import NegativeKeyword
from keywordmanager.models.hotels.province import Province
from keywordmanager.models.keywords.search import SearchKeyword


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
        province_id = get_province_id(self.province)
        district_id = get_district_id(self.district)
        hotel_id = get_hotel_id(self.hotel)
        keyword_list = []
        if self.keyword_type == 'negative':
            keyword_list.extend(query_negative(self.campaign, self.adgroup, hotel_id, district_id, province_id))

        if self.keyword_type == 'positive':
            keyword_list.extend(query_positive(self.campaign, self.adgroup, hotel_id, district_id, province_id))

        if self.keyword_type is None:
            keyword_list.extend(query_negative(self.campaign, self.adgroup, hotel_id, district_id, province_id))
            keyword_list.extend(query_positive(self.campaign, self.adgroup, hotel_id, district_id, province_id))

        return keyword_list


def get_campaign_list():
    return conn('ads').query(Campaign.name).order_by(asc(Campaign.name)).all()


def get_adgroup_list():
    return conn('ads').query(AdGroup.name).group_by(AdGroup.name).order_by(asc(AdGroup.name)).all()


def get_adgroup_list2():
    return conn('default').query(AdGroup.campaignname, AdGroup.name)\
        .order_by(asc(AdGroup.campaignname), asc(AdGroup.name)).all()


def get_province_list():
    return conn('hotels').query(Province.name).order_by(asc(Province.name)).all()


def get_district_list():
    return conn('hotels').query(District.name).order_by(asc(District.name)).all()


def get_hotel_list():
    return conn('hotels').query(Hotel.hotel_name).order_by(asc(Hotel.hotel_name)).all()


def get_campaign_id(campaign_name):
    return conn('ads').query(Campaign.id).filter(Campaign.name == campaign_name).first()


def get_adgroup_id(adgroup_name):
    return conn('ads').query(AdGroup.id).filter(AdGroup.name == adgroup_name).first()


def get_province_id(province_name):
    return conn('hotels').query(Province.id).filter(Province.name == province_name).first()


def get_district_id(district_name):
    return conn('hotels').query(District.id).filter(District.name == district_name).first()


def get_hotel_id(hotel_name):
    return conn('hotels').query(Hotel.id).filter(Hotel.hotel_name == hotel_name).first()


def query_negative(campaign, adgroup, hotel_id, district_id, province_id):
    if hotel_id is None and district_id is None and province_id is None and campaign is None and adgroup is None:
        filter_by = case([(AdGroup.name == None, literal('campaign', type_=Unicode).label('filter_by')),
                          (AdGroup.name != None, literal('ad_group', type_=Unicode).label('filter_by'))],
                         else_=None)
        query = conn('default').query(
            Keyword.id,
            NegativeKeyword.id,
            Keyword.word,
            Keyword.type,
            filter_by,
            literal('negative', type_=Unicode).label('keyword_type'),
            Campaign.name,
            AdGroup.name
        ).select_from(NegativeKeyword) \
            .join(Keyword, Keyword.id == NegativeKeyword.keyword_id, isouter=True)\
            .join(Campaign, Campaign.id == NegativeKeyword.campaign_id, isouter=True) \
            .join(AdGroup, AdGroup.id == NegativeKeyword.ad_group_id, isouter=True) \
            .all()
        return query

    filter_by = case([(AdGroup.name == None, literal('campaign', type_=Unicode).label('filter_by')),
                      (AdGroup.name != None, literal('ad_group', type_=Unicode).label('filter_by'))],
                     else_=None)
    query = conn('default').query(
        Keyword.id,
        NegativeKeyword.id,
        Keyword.word,
        Keyword.type,
        filter_by,
        literal('negative', type_=Unicode).label('keyword_type'),
        Campaign.name,
        AdGroup.name
    ).select_from(NegativeKeyword) \
        .join(Keyword, Keyword.id == NegativeKeyword.keyword_id, isouter=True) \
        .join(Campaign, and_(Campaign.id == NegativeKeyword.campaign_id, adgroup != None), isouter=True) \
        .join(AdGroup, and_(AdGroup.id == NegativeKeyword.ad_group_id, adgroup != None), isouter=True)\
        .filter(or_(and_(adgroup != None, AdGroup.name == adgroup), and_(campaign != None, Campaign.name == campaign))) \
        .all()
    return query


def query_positive(campaign, adgroup, hotel_id, district_id, province_id):
    if hotel_id is not None:
        hotel_id = hotel_id[0]
        query = conn('default').query(
            Keyword.id,
            SearchKeyword.id,
            Keyword.word,
            Keyword.type,
            literal('ad_group', type_=Unicode).label('filter_by'),
            literal('positive', type_=Unicode).label('keyword_type'),
            AdGroup.campaignname,
            AdGroup.name,
            literal('hotel', type_=Unicode).label('target_type'),
            Hotel.hotel_name
        ).select_from(SearchKeyword) \
            .join(Keyword, Keyword.id == SearchKeyword.keyword_id, isouter=True) \
            .join(AdGroup, AdGroup.id == SearchKeyword.ad_group_id, isouter=True) \
            .join(Hotel, Hotel.id == SearchKeyword.target_id, isouter=True) \
            .filter(Hotel.id == hotel_id) \
            .all()
        return query

    if district_id is not None:
        district_id = district_id[0]
        query = conn('default').query(
            Keyword.id,
            SearchKeyword.id,
            Keyword.word,
            Keyword.type,
            literal('ad_group', type_=Unicode).label('filter_by'),
            literal('positive', type_=Unicode).label('keyword_type'),
            AdGroup.campaignname,
            AdGroup.name,
            literal('district', type_=Unicode).label('target_type'),
            District.name
        ).select_from(SearchKeyword) \
            .join(Keyword, Keyword.id == SearchKeyword.keyword_id, isouter=True) \
            .join(AdGroup, AdGroup.id == SearchKeyword.ad_group_id, isouter=True) \
            .join(District, District.id == SearchKeyword.target_id, isouter=True) \
            .filter(District.id == district_id) \
            .all()
        return query

    if province_id is not None:
        province_id = province_id[0]
        query = conn('default').query(
            Keyword.id,
            SearchKeyword.id,
            Keyword.word,
            Keyword.type,
            literal('ad_group', type_=Unicode).label('filter_by'),
            literal('positive', type_=Unicode).label('keyword_type'),
            AdGroup.campaignname,
            AdGroup.name,
            literal('province', type_=Unicode).label('target_type'),
            Province.name
        ).select_from(SearchKeyword) \
            .join(Keyword, Keyword.id == SearchKeyword.keyword_id, isouter=True) \
            .join(AdGroup, AdGroup.id == SearchKeyword.ad_group_id, isouter=True) \
            .join(Province, Province.id == SearchKeyword.target_id, isouter=True) \
            .filter(Province.id == province_id) \
            .all()
        return query

    if adgroup is not None:
        target_name = case([(SearchKeyword.target_type == 'hotels', Hotel.hotel_name),
                            (SearchKeyword.target_type == 'province', Province.name),
                            (SearchKeyword.target_type == 'district', District.name)],
                           else_=None)
        query = conn('default').query(
            Keyword.id,
            SearchKeyword.id,
            Keyword.word,
            Keyword.type,
            literal('ad_group', type_=Unicode).label('filter_by'),
            literal('positive', type_=Unicode).label('keyword_type'),
            AdGroup.campaignname,
            AdGroup.name,
            SearchKeyword.target_type,
            target_name
        ).select_from(SearchKeyword) \
            .join(Keyword, Keyword.id == SearchKeyword.keyword_id) \
            .join(AdGroup, AdGroup.id == SearchKeyword.ad_group_id)\
            .join(Hotel, and_(Hotel.id == SearchKeyword.target_id, SearchKeyword.target_type == 'hotels'), isouter=True)\
            .join(District, and_(District.id == SearchKeyword.target_id, SearchKeyword.target_type == 'district'), isouter=True)\
            .join(Province, and_(Province.id == SearchKeyword.target_id, SearchKeyword.target_type == 'province'), isouter=True)\
            .filter(AdGroup.name == adgroup) \
            .all()
        return query

    if campaign is not None:
        target_name = case([(SearchKeyword.target_type == 'hotels', Hotel.hotel_name),
                            (SearchKeyword.target_type == 'province', Province.name),
                            (SearchKeyword.target_type == 'district', District.name)],
                           else_=None)
        query = conn('default').query(
            Keyword.id,
            SearchKeyword.id,
            Keyword.word,
            Keyword.type,
            literal('ad_group', type_=Unicode).label('filter_by'),
            literal('positive', type_=Unicode).label('keyword_type'),
            AdGroup.campaignname,
            AdGroup.name,
            SearchKeyword.target_type,
            target_name
        ).select_from(SearchKeyword) \
            .join(Keyword, Keyword.id == SearchKeyword.keyword_id) \
            .join(AdGroup, AdGroup.id == SearchKeyword.ad_group_id) \
            .join(Hotel, and_(Hotel.id == SearchKeyword.target_id, SearchKeyword.target_type == 'hotels'), isouter=True) \
            .join(District, and_(District.id == SearchKeyword.target_id, SearchKeyword.target_type == 'district'),
                  isouter=True) \
            .join(Province, and_(Province.id == SearchKeyword.target_id, SearchKeyword.target_type == 'province'),
                  isouter=True) \
            .filter(Campaign.name == campaign) \
            .all()
        return query

    target_name = case([(SearchKeyword.target_type == 'hotels', Hotel.hotel_name),
                        (SearchKeyword.target_type == 'province', Province.name),
                        (SearchKeyword.target_type == 'district', District.name)],
                       else_=None)
    query = conn('default').query(
        Keyword.id,
        SearchKeyword.id,
        Keyword.word,
        Keyword.type,
        literal('ad_group', type_=Unicode).label('filter_by'),
        literal('positive', type_=Unicode).label('keyword_type'),
        AdGroup.campaignname,
        AdGroup.name,
        SearchKeyword.target_type,
        target_name
    ).select_from(SearchKeyword) \
        .join(Keyword, Keyword.id == SearchKeyword.keyword_id) \
        .join(AdGroup, AdGroup.id == SearchKeyword.ad_group_id) \
        .join(Hotel, and_(Hotel.id == SearchKeyword.target_id, SearchKeyword.target_type == 'hotels'), isouter=True) \
        .join(District, and_(District.id == SearchKeyword.target_id, SearchKeyword.target_type == 'district'),
              isouter=True) \
        .join(Province, and_(Province.id == SearchKeyword.target_id, SearchKeyword.target_type == 'province'),
              isouter=True) \
        .all()
    return query


def delete_multiple(id_list):
    for item in id_list:
        if item['type'] == 'positive':
            delete_db = delete(SearchKeyword).where(SearchKeyword.id == item['type_id'])
            conn('default').execute(delete_db)
        if item['type'] == 'negative':
            delete_db = delete(NegativeKeyword).where(NegativeKeyword.id == item['type_id'])
            conn('default').execute(delete_db)
        remain_positive = conn('default').query(SearchKeyword).filter(SearchKeyword.keyword_id == item['id']).first()
        remain_negative = conn('default').query(NegativeKeyword).filter(NegativeKeyword.keyword_id == item['id']).first()
        if remain_positive is None and remain_negative is None:
            delete_db = delete(Keyword).where(Keyword.id == item['id'])
            conn('default').execute(delete_db)
