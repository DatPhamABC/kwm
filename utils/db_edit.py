from sqlalchemy import text, literal, Unicode, case

from db import connection
from models.ad_groups import AdGroup
from models.campaigns import Campaign
from models.district import District
from models.hotels import Hotel
from models.keyword import Keyword
from models.negative import NegativeKeyword
from models.province import Province
from models.search import SearchKeyword
from utils import config


def conn(source):
    session = config.sessions.get(source, None)
    if session is None:
        session = connection.db(source)
        config.sessions[source] = session
    return session


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
            text(Keyword.type.name),
            literal('ad_group', type_=Unicode).label('filter_by'),
            AdGroup.name,
            text(SearchKeyword.target_type.name),
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
