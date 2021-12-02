from sqlalchemy import text, literal, Unicode, case, and_

from keywordmanager.db.session import conn
from keywordmanager.models.ads.ad_groups import AdGroup
from keywordmanager.models.ads.campaigns import Campaign
from keywordmanager.models.hotels.district import District
from keywordmanager.models.hotels.hotels import Hotel
from keywordmanager.models.keywords.keyword import Keyword
from keywordmanager.models.keywords.negative import NegativeKeyword
from keywordmanager.models.hotels.province import Province
from keywordmanager.models.keywords.search import SearchKeyword


def get_keyword_info(id, keyword_type, type_id):
    # type_id is the id of keyword in it respective table (search or negative)
    keyword_info = []
    if keyword_type == 'positive' is not None:
        keyword_info = conn('default').query(
            Keyword.id,
            Keyword.word,
            literal('positive', type_=Unicode).label('form_type'),
            Keyword.type,
            literal('ad_group', type_=Unicode).label('filter_by'),
            AdGroup.campaignname,
            AdGroup.name,
            SearchKeyword.target_type,
            Hotel.hotel_name,
            District.name,
            Province.name,
            SearchKeyword.id
        ).select_from(SearchKeyword) \
            .join(Keyword, Keyword.id == SearchKeyword.keyword_id, isouter=True) \
            .join(AdGroup, AdGroup.id == SearchKeyword.ad_group_id, isouter=True)\
            .join(Hotel, and_(Hotel.id == SearchKeyword.target_id, SearchKeyword.target_type == 'hotels'), isouter=True)\
            .join(Province, and_(Province.id == SearchKeyword.target_id, SearchKeyword.target_type == 'province'), isouter=True)\
            .join(District, and_(District.id == SearchKeyword.target_id, SearchKeyword.target_type == 'district'), isouter=True) \
            .filter(SearchKeyword.keyword_id == id, SearchKeyword.id == type_id)\
            .first()

    if keyword_type == 'negative':
        level = case([(NegativeKeyword.ad_group_id != None, literal("adgroup", type_=Unicode)),
                      (NegativeKeyword.campaign_id != None, literal("campaign", type_=Unicode))],
                     else_=None)
        keyword_info = conn('default').query(
            Keyword.id,
            Keyword.word,
            literal("negative", type_=Unicode).label('match_type'),
            text(Keyword.type.name),
            level,
            Campaign.name,
            AdGroup.name,
            NegativeKeyword.id
        ).select_from(NegativeKeyword) \
            .join(Keyword, Keyword.id == NegativeKeyword.keyword_id) \
            .join(Campaign, Campaign.id == NegativeKeyword.campaign_id, isouter=True)\
            .join(AdGroup, AdGroup.id == NegativeKeyword.ad_group_id, isouter=True) \
            .filter(Keyword.id == id, NegativeKeyword.id == type_id) \
            .first()
    return keyword_info


def delete_positive(keyword_id, positive_id):
    conn('default').query(Keyword).filter(Keyword.id == keyword_id).delete()
    conn('default').query(SearchKeyword).filter(SearchKeyword.id == positive_id).delete()


def delete_negative(keyword_id, negative_id):
    conn('default').query(NegativeKeyword).filter(NegativeKeyword.id == negative_id).delete()
    negative_check = conn('default').query(NegativeKeyword).filter(NegativeKeyword.keyword_id == keyword_id).first()
    if negative_check is None:
        conn('default').query(Keyword).filter(Keyword.id == keyword_id).delete()
