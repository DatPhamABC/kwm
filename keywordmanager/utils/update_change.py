import datetime
import json
from collections import defaultdict

from flask import flash
from sqlalchemy import and_, or_

from keywordmanager.db.session import conn
from keywordmanager.models.ads.ad_groups import AdGroup
from keywordmanager.models.ads.campaigns import Campaign
from keywordmanager.models.hotels.district import District
from keywordmanager.models.hotels.hotels import Hotel
from keywordmanager.models.hotels.province import Province
from keywordmanager.models.keywords.keyword import Keyword
from keywordmanager.models.keywords.negative import NegativeKeyword
from keywordmanager.models.keywords.search import SearchKeyword
from keywordmanager.utils.insert import query_keyword_id, query_adgroup_id, update_on_dupkey, \
    update_on_dupkey_negative, update_on_dupkey_search, query_search_id
from keywordmanager.utils.search import get_hotel_id, get_district_id, get_province_id


def update_change_negative(id, negative_id, keyword, match_type, adgroup, campaign):
    if adgroup != 'None':
        adgroup_info = conn('default').query(AdGroup.id, AdGroup.campaignid)\
            .filter(and_(AdGroup.campaignname == campaign, AdGroup.name == adgroup)).first()
        if adgroup_info is None:
            flash('Wrong campaign and adgroup match.')
        else:
            update_on_dupkey(Keyword, {'id': id, 'word': keyword, 'type': match_type,
                                       'is_active': True, 'created_time': datetime.datetime.now()})
            update_on_dupkey_negative(NegativeKeyword, {'id': negative_id, 'campaign_id': adgroup_info[1],
                                                        'ad_group_id': adgroup_info[0], 'keyword_id': id})
    else:
        campaign_info = conn('default').query(Campaign.id).filter(Campaign.name == campaign).first()
        update_on_dupkey(Keyword, {'id': id, 'word': keyword, 'type': match_type,
                                   'is_active': True, 'created_time': datetime.datetime.now()})
        update_on_dupkey_negative(NegativeKeyword, {'id': negative_id, 'campaign_id': campaign_info[0],
                                                    'ad_group_id': None, 'keyword_id': id})


def update_change_positive(id, positive_id,
                           keyword, match_type,
                           campaign,
                           adgroup,
                           target_type,
                           hotel,
                           district,
                           province):
    target_id = None
    if target_type == 'hotels':
        target_id = get_hotel_id(hotel)
    elif target_type == 'district':
        target_id = get_district_id(district)
    elif target_type == 'province':
        target_id = get_province_id(province)
    else:
        target_type = None

    if target_id is not None:
        target_id = target_id[0]

    adgroup_info = conn('default').query(AdGroup.id) \
        .filter(and_(AdGroup.campaignname == campaign, AdGroup.name == adgroup)).first()

    time = datetime.datetime.now()
    update_on_dupkey(Keyword, {'id': id, 'type': match_type, 'is_active': True, 'created_time': time})
    update_on_dupkey_search(SearchKeyword, {'id': positive_id,
                                            'keyword_id': id,
                                            'target_id': target_id,
                                            'target_type': target_type,
                                            'ad_group_id': adgroup_info[0],
                                            'created_time': time})
