from flask import flash

from db.db_insert import update_on_dupkey, query_keyword_id, query_campaign_id, query_adgroup_id, \
    update_on_dupkey_negative, update_on_dupkey_search, query_search_id, query_negative_id, insert_keyword
from models.keyword import Keyword, typeEnum
import datetime

from models.negative import NegativeKeyword
from models.search import SearchKeyword
from stored import config


def parse_xlsx(df1):
    if 'Keyword' in df1.columns:
        parse_keyword(df1)
    elif 'Negative keyword' in df1.columns:
        parse_negative_keyword(df1)
    elif 'Search term' in df1.columns:
        parse_search_term(df1)
    else:
        flash('Incorrect file format')


def parse_keyword(df1):
    df1 = df1.astype({"Keyword status": str, "Keyword": str, "Campaign": str, "Ad group": str})
    for i, row in df1.iterrows():
        if row['Keyword'].startswith('"'):
            match_type = typeEnum.phrase
            keyword = row['Keyword'][1:-1]
        elif row['Keyword'].startswith('['):
            match_type = typeEnum.exact
            keyword = row['Keyword'][1:-1]
        else:
            match_type = typeEnum.broad
            keyword = row['Keyword']

        if row['Keyword status'] == "Enabled":
            is_active = True
        else:
            is_active = False

        keyword_id = query_keyword_id(keyword)

        if keyword_id is None:
            insert_keyword(Keyword, {'word': keyword, 'type': match_type,
                                     'is_active': is_active, 'created_time': datetime.datetime.now()})
            config.new_insert_count += 1
        else:
            update_on_dupkey(Keyword, {'id': keyword_id[0], 'word': keyword, 'type': match_type,
                                       'is_active': is_active, 'created_time': datetime.datetime.now()})
            config.update_count += 1

        keyword_id = query_keyword_id(keyword)
        adgroup_id = query_adgroup_id(row['Ad group'])
        search_id = query_search_id(keyword_id[0])
        if search_id is None:
            insert_keyword(SearchKeyword, {'keyword_id': keyword_id[0], 'ad_group_id': adgroup_id[0],
                                           'created_time': datetime.datetime.now()})
        else:
            update_on_dupkey_search(SearchKeyword, {'id': search_id[0], 'keyword_id': keyword_id[0],
                                                    'ad_group_id': adgroup_id[0],
                                                    'created_time': datetime.datetime.now()})


def parse_negative_keyword(df1):
    df1 = df1.astype({"Negative keyword": str, "Campaign": str, "Ad group": str, "Match type": str})
    for i, row in df1.iterrows():
        if 'broad' in row['Match type'].lower():
            match_type = typeEnum.broad
        elif 'exact' in row['Match type'].lower():
            match_type = typeEnum.exact
        elif 'phrase' in row['Match type'].lower():
            match_type = typeEnum.phrase
        else:
            match_type = None

        keyword = row['Negative keyword'][1:-1]
        keyword_id = query_keyword_id(keyword)
        if keyword_id is None:
            insert_keyword(Keyword, {'word': keyword, 'type': match_type,
                                     'created_time': datetime.datetime.now()})
            config.new_insert_count += 1
        else:
            update_on_dupkey(Keyword, {'id': keyword_id[0], 'word': keyword,
                                       'type': match_type, 'created_time': datetime.datetime.now()})
            config.update_count += 1
        keyword_id = query_keyword_id(keyword)
        campaign_id = query_campaign_id(row['Campaign'])
        ad_group_id = query_adgroup_id(row['Ad group'])
        if campaign_id is not None:
            campaign_id = campaign_id[0]
        if ad_group_id is not None:
            ad_group_id = ad_group_id[0]
        negative_id = query_negative_id(campaign_id, ad_group_id, keyword_id[0])
        if negative_id is None:
            insert_keyword(NegativeKeyword, {'campaign_id': campaign_id, 'ad_group_id': ad_group_id,
                                             'keyword_id': keyword_id[0]})
        else:
            update_on_dupkey_negative(NegativeKeyword, {'id': negative_id[0], 'campaign_id': campaign_id,
                                                        'ad_group_id': ad_group_id, 'keyword_id': keyword_id[0]})


def parse_search_term(df1):
    df1 = df1.astype({"Search term": str, "Match type": str, "Added/Excluded": str, "Ad group": str})
    for i, row in df1.iterrows():
        if 'total:' in row['Search term'].lower():
            continue

        if 'broad' in row['Match type'].lower():
            match_type = typeEnum.broad
        elif 'exact' in row['Match type'].lower():
            match_type = typeEnum.exact
        elif 'phase' in row['Match type'].lower():
            match_type = typeEnum.phrase
        else:
            match_type = None

        if "added" in row["Added/Excluded"].lower():
            is_added = True
        else:
            is_added = False

        keyword_id = query_keyword_id(row['Search term'])
        if keyword_id is None:
            insert_keyword(Keyword, {'word': row['Search term'], 'type': match_type,
                                     'is_active': is_added, 'created_time': datetime.datetime.now()})
            config.new_insert_count += 1
        else:
            update_on_dupkey(Keyword, {'id': keyword_id[0], 'word': row['Search term'], 'type': match_type,
                                       'is_active': is_added, 'created_time': datetime.datetime.now()})
            config.update_count += 1

        keyword_id = query_keyword_id(row['Search term'])
        ad_group_id = query_adgroup_id(row['Ad group'])
        if ad_group_id is not None:
            ad_group_id = ad_group_id[0]
        term_id = query_search_id(keyword_id[0])
        if term_id is None:
            insert_keyword(SearchKeyword, {'keyword_id': keyword_id[0], 'ad_group_id': ad_group_id,
                                           'created_time': datetime.datetime.now()})
        else:
            update_on_dupkey_search(SearchKeyword, {'id': term_id[0], 'keyword_id': keyword_id[0],
                                                    'ad_group_id': ad_group_id,
                                                    'created_time': datetime.datetime.now()})
