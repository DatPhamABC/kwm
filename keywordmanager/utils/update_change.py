import datetime

from keywordmanager.models.keywords.keyword import Keyword
from keywordmanager.models.keywords.negative import NegativeKeyword
from keywordmanager.models.keywords.search import SearchKeyword
from keywordmanager.utils.insert import query_keyword_id, query_campaign_id, query_adgroup_id, update_on_dupkey, \
    update_on_dupkey_negative, query_negative_id, update_on_dupkey_search, query_search_id
from keywordmanager.utils.search import get_hotel_id, get_district_id, get_province_id


def update_change_negative(keyword, match_type, old_adgroup, adgroup, old_campaign, campaign):
    id = query_keyword_id(keyword)
    old_adgroup_id = None
    old_campaign_id = None
    adgroup_id = None
    campaign_id = None
    if old_adgroup is not None or old_adgroup == "":
        old_adgroup_id = query_adgroup_id(old_adgroup)
    if old_campaign is not None or old_campaign == "":
        old_campaign_id = query_campaign_id(old_campaign)
    if adgroup is not None or adgroup == "":
        adgroup_id = query_adgroup_id(adgroup)
    if campaign is not None or campaign == "":
        campaign_id = query_campaign_id(campaign)

    if old_campaign_id is not None:
        old_campaign_id = old_campaign_id[0]
    if old_adgroup_id is not None:
        old_adgroup_id = old_adgroup_id[0]
    if id is not None:
        id = id[0]
    if campaign_id is not None:
        campaign_id = campaign_id[0]
    if adgroup_id is not None:
        adgroup_id = adgroup_id[0]
    negative_id = query_negative_id(old_campaign_id, old_adgroup_id, id)
    update_on_dupkey(Keyword, {'id': id, 'word': keyword, 'type': match_type,
                               'is_active': True, 'created_time': datetime.datetime.now()})
    update_on_dupkey_negative(NegativeKeyword, {'id': negative_id[0], 'campaign_id': campaign_id,
                                                'ad_group_id': adgroup_id, 'keyword_id': id})


def update_change_positive(keyword, match_type, adgroup, target_type, hotel, district, province):
    id = query_keyword_id(keyword)
    target_id = None
    if target_type == 'hotel':
        target_id = get_hotel_id(hotel)
    elif target_type == 'district':
        target_id = get_district_id(district)
    elif target_type == 'province':
        target_id = get_province_id(province)
    else:
        target_type = None
    adgroup_id = None
    if adgroup is not None or adgroup == "":
        adgroup_id = query_adgroup_id(adgroup)

    if id is not None:
        id = id[0]
    if adgroup_id is not None:
        adgroup_id = adgroup_id[0]
    if target_id is not None:
        target_id = target_id[0]

    search_id = query_search_id(id)
    update_on_dupkey(Keyword, {'id': id, 'type': match_type, 'is_active': True, 'created_time': datetime.datetime.now()})
    update_on_dupkey_search(SearchKeyword, {'id': search_id[0], 'keyword_id': id,
                                            'target_id': target_id,
                                            'target_type': target_type,
                                            'ad_group_id': adgroup_id,
                                            'created_time': datetime.datetime.now()})
