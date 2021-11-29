import time

import numpy as np
import pandas as pd
from flask import flash

from keywordmanager.db.session import conn
from keywordmanager.models.ads.ad_groups import AdGroup
from keywordmanager.models.ads.campaigns import Campaign
from keywordmanager.utils import config
from keywordmanager.utils.insert import update_on_dupkey, update_on_dupkey_negative, update_on_dupkey_search
from keywordmanager.models.keywords.keyword import Keyword
import datetime

from keywordmanager.models.keywords.negative import NegativeKeyword
from keywordmanager.models.keywords.search import SearchKeyword

pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 10)


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
    df1 = df1[['Keyword status', 'Keyword', 'Campaign', 'Ad group']]\
        .astype({"Keyword status": str, "Keyword": str, "Campaign": str, "Ad group": str})
    df1.loc[df1['Keyword'].str.startswith('"', na=False), 'Match type'] = 'phrase'
    df1.loc[df1['Keyword'].str.startswith('[', na=False), 'Match type'] = 'exact'
    df1.loc[~(df1['Keyword'].str.startswith('"', na=False)
              | df1['Keyword'].str.startswith('[', na=False)), 'Match type'] = 'broad'
    # df1['Keyword'] = np.where(df1['Keyword'].str.startswith('"', na=False),
    #                           df1['Keyword'].str[1:-1], df1['Keyword'])
    # df1['Keyword'] = np.where(df1['Keyword'].str.startswith('[', na=False),
    #                           df1['Keyword'].str[1:-1], df1['Keyword'])
    df1['Keyword status'] = np.where(~df1['Keyword status'].str.contains("enable", case=False),
                                     False, df1['Keyword status'])
    df1['Keyword status'] = np.where(df1['Keyword status'].str.contains("enable", case=False),
                                     True, df1['Keyword status'])
    df1 = df1.astype({"Keyword status": bool})
    df1['created_time'] = datetime.datetime.now()
    df1.drop_duplicates(inplace=True)

    # insert into keyword table
    keyword_df = pd.DataFrame(conn('default').query(Keyword.id, Keyword.word),
                              columns=['id', 'Keyword'])
    keyword_insert = df1[['Keyword', 'Match type', 'created_time']]
    keyword_insert.drop_duplicates(inplace=True)
    keyword_insert = pd.merge(keyword_insert, keyword_df, how='left', on=["Keyword"])
    keyword_insert.drop_duplicates(inplace=True)
    keyword_insert = keyword_insert.rename(columns={'Keyword': 'word', 'Match type': 'type'})
    keyword_not_null = keyword_insert.loc[keyword_insert['id'].notnull()]
    keyword_null = keyword_insert.loc[~keyword_insert['id'].notnull()]
    config.update_count = len(keyword_not_null.to_dict('record'))
    config.new_insert_count = len(keyword_null.to_dict('record'))
    config.update_data = keyword_not_null.to_dict('record')
    config.insert_data = keyword_null.to_dict('record')
    keyword_insert = keyword_insert.replace({np.nan: None})
    keyword_insert.drop_duplicates(inplace=True)
    for item in chunks(keyword_insert.to_dict('record'), 10000):
        update_on_dupkey(Keyword, item)

    # insert to search table
    keyword_df = pd.DataFrame(conn('default').query(Keyword.id, Keyword.word), columns=['keyword_id', 'Keyword'])
    search_df = pd.DataFrame(conn('default').query(SearchKeyword.id, SearchKeyword.keyword_id),
                             columns=['id', 'keyword_id'])
    campaign_df = pd.DataFrame(conn('default').query(Campaign.id, Campaign.name), columns=['campaign_id', 'Campaign'])
    adgroup_df = pd.DataFrame(conn('default').query(AdGroup.id, AdGroup.name, AdGroup.campaignid),
                              columns=['ad_group_id', 'Ad group', 'campaign_id'])
    search_insert = pd.merge(df1, keyword_df, how='left', on=["Keyword"])
    search_insert = pd.merge(search_insert, search_df, how='left', on=["keyword_id"])
    search_insert = pd.merge(search_insert, campaign_df, how='left', on=["Campaign"])
    search_insert = pd.merge(search_insert, adgroup_df, how='left', on=['Ad group', 'campaign_id'])
    search_insert = search_insert[['id', 'keyword_id', 'ad_group_id', 'created_time']]
    search_insert.fillna(value='', inplace=True)
    for item in chunks(search_insert.to_dict('record'), 10000):
        update_on_dupkey_search(SearchKeyword, item)


def parse_negative_keyword(df1):
    t0 = time.time()
    # cleaning
    df1 = df1.astype({"Negative keyword": str, "Campaign": str, "Ad group": str, "Match type": str})
    df1.drop(columns=['Keyword or list'], inplace=True)
    df1.loc[df1['Match type'].str.contains('broad', case=False), 'Match type'] = 'broad'
    df1.loc[df1['Match type'].str.contains('exact', case=False), 'Match type'] = 'exact'
    df1.loc[df1['Match type'].str.contains('phrase', case=False), 'Match type'] = 'phrase'
    # df1['Negative keyword'] = np.where(df1['Negative keyword'].str.startswith('"', na=False),
    #                                    df1['Negative keyword'].str[1:-1], df1['Negative keyword'])
    # df1['Negative keyword'] = np.where(df1['Negative keyword'].str.startswith('[', na=False),
    #                                    df1['Negative keyword'].str[1:-1], df1['Negative keyword'])
    df1['created_time'] = datetime.datetime.now()
    df1.drop_duplicates(inplace=True)

    # insert into keyword table
    keyword_df = pd.DataFrame(conn('default').query(Keyword.id, Keyword.word), columns=['id', 'Negative keyword'])
    keyword_insert = df1[['Negative keyword', 'Match type', 'created_time']]
    keyword_insert = pd.merge(keyword_insert, keyword_df, how='left', on=["Negative keyword"])
    keyword_insert = keyword_insert.rename(columns={'Negative keyword': 'word', 'Match type': 'type'})
    keyword_insert.drop_duplicates(inplace=True)
    keyword_not_null = keyword_insert.loc[keyword_insert['id'].notnull()]
    keyword_null = keyword_insert.loc[~keyword_insert['id'].notnull()]
    config.update_count = len(keyword_not_null.to_dict('record'))
    config.new_insert_count = len(keyword_null.to_dict('record'))
    config.update_data = keyword_not_null.to_dict('record')
    config.insert_data = keyword_null.to_dict('record')
    keyword_insert = keyword_insert.replace({np.nan: None})
    keyword_insert.drop_duplicates(inplace=True)
    print(time.time() - t0)
    for item in chunks(keyword_insert.to_dict('record'), 10000):
        update_on_dupkey(Keyword, item)

    # insert into negative table
    ad_group_level = df1[df1['Level'].str.contains('ad group', case=False)]
    campaign_level = df1[df1['Level'].str.contains('campaign', case=False)]
    keyword_df = pd.DataFrame(conn('default').query(Keyword.id, Keyword.word),
                              columns=['keyword_id', 'Negative keyword'])
    negative_df = pd.DataFrame(conn('default').query(NegativeKeyword.id, NegativeKeyword.ad_group_id,
                                                     NegativeKeyword.campaign_id, NegativeKeyword.keyword_id),
                               columns=['id', 'ad_group_id', 'campaign_id', 'keyword_id'])
    adgroup_df = pd.DataFrame(conn('default').query(AdGroup.id, AdGroup.name, Campaign.id, Campaign.name)
                              .select_from(AdGroup)
                              .join(Campaign, AdGroup.campaignid == Campaign.id),
                              columns=['ad_group_id', 'Ad group', 'campaign_id', 'Campaign'])
    campaign_df = pd.DataFrame(conn('default').query(Campaign.id, Campaign.name), columns=['campaign_id', 'Campaign'])
    campaign_level = pd.merge(campaign_level, campaign_df, how='left', on=["Campaign"])
    ad_group_level = pd.merge(ad_group_level, adgroup_df, how='left', on=['Campaign', 'Ad group'])
    negative_insert = pd.concat([campaign_level, ad_group_level])
    negative_insert = pd.merge(negative_insert, keyword_df, how='left', on=['Negative keyword'])
    negative_insert = pd.merge(negative_insert, negative_df, how='left',
                               on=["keyword_id", 'campaign_id', 'ad_group_id'])
    negative_insert = negative_insert[['id', 'campaign_id', 'ad_group_id', 'keyword_id']]
    negative_insert = negative_insert.replace({np.nan: None})
    negative_insert.drop_duplicates(inplace=True)
    print(len(negative_insert.index))
    print(time.time() - t0)
    for item in chunks(negative_insert.to_dict('record'), 10000):
        update_on_dupkey_negative(NegativeKeyword, item)
    print(time.time() - t0)


def parse_search_term(df1):
    # cleaning
    df1 = df1[['Search term', 'Match type', 'Added/Excluded', 'Ad group']] \
        .astype({"Search term": str, "Match type": str, "Added/Excluded": str, "Ad group": str})
    df1 = df1[~df1["Search term"].str.lower().str.contains('total:')]
    df1.loc[df1['Match type'].str.contains('broad', case=False), 'Match type'] = 'broad'
    df1.loc[df1['Match type'].str.contains('exact', case=False), 'Match type'] = 'exact'
    df1.loc[df1['Match type'].str.contains('phrase', case=False), 'Match type'] = 'phrase'
    df1['Search term'] = np.where(df1['Match type'].str.contains('exact', case=False),
                                  '[' + df1['Search term'] + ']', df1['Search term'])
    df1['Search term'] = np.where(df1['Match type'].str.contains('phrase', case=False),
                                  '"' + df1['Search term'] + '"', df1['Search term'])
    df1.loc[df1['Added/Excluded'].str.contains('added', case=False), 'Added/Excluded'] = True
    df1.loc[~df1['Added/Excluded'].str.contains('excluded', case=False), 'Added/Excluded'] = False
    df1['created_time'] = datetime.datetime.now()

    # insert to keyword table
    keyword_df = pd.DataFrame(conn('default').query(Keyword.id, Keyword.word), columns=['id', 'Search term'])
    keyword_insert = df1[['Search term', 'Match type', 'Added/Excluded', 'created_time']]
    keyword_insert.drop_duplicates(inplace=True)
    keyword_insert = pd.merge(keyword_insert, keyword_df, how='left', on=["Search term"])
    keyword_insert.drop_duplicates(inplace=True)
    keyword_insert = keyword_insert.rename(columns={'Search term': 'word', 'Match type': 'type',
                                                    'Added/Excluded': 'is_active'})
    keyword_insert = keyword_insert.astype({"is_active": bool})
    keyword_not_null = keyword_insert.loc[keyword_insert['id'].notnull()]
    keyword_null = keyword_insert.loc[~keyword_insert['id'].notnull()]
    config.update_count = len(keyword_not_null.to_dict('record'))
    config.new_insert_count = len(keyword_null.to_dict('record'))
    config.update_data = keyword_not_null.to_dict('record')
    config.insert_data = keyword_null.to_dict('record')
    keyword_insert.fillna(value='', inplace=True)
    keyword_insert.drop_duplicates(inplace=True)
    for item in chunks(keyword_insert.to_dict('record'), 10000):
        update_on_dupkey(Keyword, item)

    # insert to search table
    keyword_df = pd.DataFrame(conn('default').query(Keyword.id, Keyword.word), columns=['keyword_id', 'Search term'])
    search_df = pd.DataFrame(
        conn('default').query(SearchKeyword.id, SearchKeyword.keyword_id, SearchKeyword.ad_group_id),
        columns=['id', 'keyword_id', 'ad_group_id'])
    adgroup_df = pd.DataFrame(conn('default').query(AdGroup.id, AdGroup.name), columns=['ad_group_id', 'Ad group'])
    search_insert = pd.merge(df1, keyword_df, how='left', on=["Search term"])
    search_insert.drop_duplicates(inplace=True)
    search_insert = pd.merge(search_insert, adgroup_df, how='left', on=['Ad group'])
    search_insert.drop_duplicates(inplace=True)
    search_insert = pd.merge(search_insert, search_df, how='left', on=["keyword_id", "ad_group_id"])
    search_insert.drop_duplicates(inplace=True)
    search_insert = search_insert[['id', 'keyword_id', 'ad_group_id', 'created_time']]
    search_insert = search_insert.replace({np.nan: None})
    search_insert.drop_duplicates(inplace=True)
    for item in chunks(search_insert.to_dict('record'), 10000):
        update_on_dupkey_search(SearchKeyword, item)


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
