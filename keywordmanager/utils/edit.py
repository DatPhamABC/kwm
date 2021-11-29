from sqlalchemy import text, literal, Unicode, case

from keywordmanager.db.session import conn
from keywordmanager.models.ads.ad_groups import AdGroup
from keywordmanager.models.ads.campaigns import Campaign
from keywordmanager.models.hotels.district import District
from keywordmanager.models.hotels.hotels import Hotel
from keywordmanager.models.keywords.keyword import Keyword
from keywordmanager.models.keywords.negative import NegativeKeyword
from keywordmanager.models.hotels.province import Province
from keywordmanager.models.keywords.search import SearchKeyword


def get_keyword_info(id):
    positive_id = conn('default').query(SearchKeyword.id).filter(SearchKeyword.keyword_id == id).first()
    if positive_id is not None:
        target_name = case([(SearchKeyword.target_type == 'hotels',
                             conn('hotels').query(Hotel.hotel_name).filter(Hotel.id == SearchKeyword.target_id)),
                            (SearchKeyword.target_type == 'province',
                             conn('hotels').query(Province.name).filter(Province.id == SearchKeyword.target_id)),
                            (SearchKeyword.target_type == 'district',
                             conn('hotels').query(District.name).filter(District.id == SearchKeyword.target_id))],
                           else_=None)
        keyword_info = conn('default').query(
            Keyword.id,
            Keyword.word,
            literal('positive', type_=Unicode).label('form_type'),
            Keyword.type,
            literal('ad_group', type_=Unicode).label('filter_by'),
            AdGroup.name,
            SearchKeyword.target_type,
            target_name,
            SearchKeyword.id
        ).select_from(SearchKeyword) \
            .join(Keyword, Keyword.id == SearchKeyword.keyword_id) \
            .join(AdGroup, AdGroup.id == SearchKeyword.ad_group_id) \
            .filter(SearchKeyword.keyword_id == id)\
            .first()
    else:
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
            .filter(Keyword.id == id) \
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
