import time
from time import sleep

import numpy as np
import pandas as pd
from flask import flash
from sqlalchemy.dialects.mysql import insert

from db import connection
from models.ad_groups import AdGroup
from models.campaigns import Campaign
from utils.db_insert import update_on_dupkey, query_keyword_id, query_campaign_id, query_adgroup_id, \
    update_on_dupkey_negative, update_on_dupkey_search, query_search_id, query_negative_id, insert_keyword
from models.keyword import Keyword, typeEnum
import datetime

from models.negative import NegativeKeyword
from models.search import SearchKeyword
from utils import config


def conn(source):
    session = config.sessions.get(source, None)
    if session is None:
        session = connection.db(source)
        config.sessions[source] = session
    return session


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
    df1.loc[df1['Match type'].str.startswith('"', na=False), 'Match type'] = 'phrase'
    df1.loc[df1['Match type'].str.startswith('[', na=False), 'Match type'] = 'exact'
    df1.loc[~(df1['Match type'].str.startswith('"', na=True)
              & df1['Match type'].str.startswith('[', na=True)), 'Match type'] = 'broad'

    df1['created_time'] = datetime.datetime.now()
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

        # if keyword_id is None:
        #     keyword_to_input.append({'word': keyword, 'type': match_type,
        #                              'is_active': is_active, 'created_time': datetime.datetime.now()})
        #     config.new_insert_count += 1
        #     config.insert_data.append([keyword, match_type.name, 'positive'])
        # else:
        #     keyword_to_update.append({'id': keyword_id[0], 'type': match_type,
        #                               'is_active': is_active, 'created_time': datetime.datetime.now()})
        #     config.update_count += 1
        #     config.update_data.append([keyword, match_type.name, 'positive'])
        #
        # if search_id is None:
        #     search_to_input.append({'keyword_id': keyword_id[0], 'ad_group_id': adgroup_id[0],
        #                             'created_time': datetime.datetime.now()})
        # else:
        #     search_to_update.append({'id': search_id[0], 'keyword_id': keyword_id[0],
        #                              'ad_group_id': adgroup_id[0], 'created_time': datetime.datetime.now()})


def parse_negative_keyword(df1):
    # cleaning
    df1 = df1.astype({"Negative keyword": str, "Campaign": str, "Ad group": str, "Match type": str})
    df1.drop(columns=['Keyword or list'], inplace=True)
    df1.loc[df1['Match type'].str.contains('broad', case=False), 'Match type'] = 'broad'
    df1.loc[df1['Match type'].str.contains('exact', case=False), 'Match type'] = 'exact'
    df1.loc[df1['Match type'].str.contains('phase', case=False), 'Match type'] = 'phase'
    df1['created_time'] = datetime.datetime.now()

    # insert into keyword table
    keyword_df = pd.DataFrame(conn('default').query(Keyword.id, Keyword.word), columns=['id', 'Negative keyword'])
    keyword_insert = df1[['Negative keyword', 'Match type', 'created_time']]
    keyword_insert = pd.merge(keyword_insert, keyword_df, how='left', on=["Negative keyword"])
    keyword_insert = keyword_insert.rename(columns={'Negative keyword': 'word', 'Match type': 'type'})
    keyword_insert.fillna(value='', inplace=True)
    update_on_dupkey(Keyword, keyword_insert.to_dict('record'))

    # insert into negative table
    keyword_df = pd.DataFrame(conn('default').query(Keyword.id, Keyword.word), columns=['keyword_id', 'Negative keyword'])
    negative_df = pd.DataFrame(conn('default').query(NegativeKeyword.id, NegativeKeyword.ad_group_id,
                                                     NegativeKeyword.campaign_id, NegativeKeyword.keyword_id),
                               columns=['id', 'ad_group_id', 'campaign_id', 'keyword_id'])
    adgroup_df = pd.DataFrame(conn('default').query(AdGroup.id, AdGroup.name), columns=['ad_group_id', 'Ad group'])
    campaign_df = pd.DataFrame(conn('default').query(Campaign.id, Campaign.name), columns=['campaign_id', 'Campaign'])
    negative_insert = pd.merge(df1, keyword_df, how='left', on=["Negative keyword"])
    negative_insert = pd.merge(negative_insert, adgroup_df, how='left', on=['Ad group'])
    negative_insert = pd.merge(negative_insert, campaign_df, how='left', on=['Campaign'])
    negative_insert = pd.merge(negative_insert, negative_df, how='left', on=["keyword_id", 'campaign_id', 'ad_group_id'])
    negative_insert = negative_insert[['id', 'campaign_id', 'ad_group_id', 'keyword_id']]
    negative_insert.fillna(value='', inplace=True)
    update_on_dupkey_negative(NegativeKeyword, negative_insert.to_dict('record'))


def parse_search_term(df1):
    # cleaning
    df1 = df1[['Search term', 'Match type', 'Added/Excluded', 'Ad group']]\
        .astype({"Search term": str, "Match type": str, "Added/Excluded": str, "Ad group": str})
    df1 = df1[~df1["Search term"].str.lower().str.contains('total:')]
    df1.loc[df1['Match type'].str.contains('broad', case=False), 'Match type'] = 'broad'
    df1.loc[df1['Match type'].str.contains('exact', case=False), 'Match type'] = 'exact'
    df1.loc[df1['Match type'].str.contains('phase', case=False), 'Match type'] = 'phase'
    df1.loc[df1['Added/Excluded'].str.contains('added', case=False), 'Added/Excluded'] = True
    df1.loc[~df1['Added/Excluded'].str.contains('excluded', case=False), 'Added/Excluded'] = False
    df1['created_time'] = datetime.datetime.now()

    # insert to keyword table
    keyword_df = pd.DataFrame(conn('default').query(Keyword.id, Keyword.word), columns=['id', 'Search term'])
    keyword_insert = df1[['Search term', 'Match type', 'Added/Excluded', 'created_time']]
    keyword_insert = pd.merge(keyword_insert, keyword_df, how='left', on=["Search term"])
    keyword_insert = keyword_insert.rename(columns={'Search term': 'word', 'Match type': 'type',
                                                    'Added/Excluded': 'is_active'})
    keyword_insert = keyword_insert.astype({"is_active": bool})
    keyword_insert.fillna(value='', inplace=True)
    update_on_dupkey(Keyword, keyword_insert.to_dict('record'))

    # insert to searh table
    keyword_df = pd.DataFrame(conn('default').query(Keyword.id, Keyword.word), columns=['keyword_id', 'Search term'])
    search_df = pd.DataFrame(conn('default').query(SearchKeyword.id, SearchKeyword.keyword_id),
                             columns=['id', 'keyword_id'])
    adgroup_df = pd.DataFrame(conn('default').query(AdGroup.id, AdGroup.name), columns=['ad_group_id', 'Ad group'])
    search_insert = pd.merge(df1, keyword_df, how='left', on=["Search term"])
    search_insert = pd.merge(search_insert, search_df, how='left', on=["keyword_id"])
    search_insert = pd.merge(search_insert, adgroup_df, how='left', on=['Ad group'])
    search_insert = search_insert[['id', 'keyword_id', 'ad_group_id', 'created_time']]
    search_insert.fillna(value='', inplace=True)
    update_on_dupkey_search(SearchKeyword, search_insert.to_dict('record'))
