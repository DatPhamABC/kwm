from sqlalchemy import and_, or_
from sqlalchemy.dialects.mysql import insert

from db import connection
from models.negative import NegativeKeyword
from stored import config


def conn(source):
    session = config.sessions.get(source, None)
    if session is None:
        session = connection.db(source)
        config.sessions[source] = session
    return session


def insert_keyword(model, insert_dict):
    insert_db = insert(model).values(**insert_dict)
    conn('default').execute(insert_db)


def update_on_dupkey(model, insert_dict):
    insert_db = insert(model).values(**insert_dict)
    update_on_duplicate_key = insert_db.on_duplicate_key_update(word=insert_db.inserted.word,
                                                                type=insert_db.inserted.type,
                                                                is_active=insert_db.inserted.is_active)
    conn('default').execute(update_on_duplicate_key)


def update_on_dupkey_search(model, insert_dict):
    insert_db = insert(model).values(**insert_dict)
    update_on_duplicate_key = insert_db.on_duplicate_key_update(keyword_id=insert_db.inserted.keyword_id,
                                                                target_id=insert_db.inserted.target_id,
                                                                ad_group_id=insert_db.inserted.ad_group_id)
    conn('default').execute(update_on_duplicate_key)


def update_on_dupkey_negative(model, insert_dict):
    insert_db = insert(model).values(**insert_dict)
    update_on_duplicate_key = insert_db.on_duplicate_key_update(campaign_id=insert_db.inserted.campaign_id,
                                                                ad_group_id=insert_db.inserted.ad_group_id,
                                                                keyword_id=insert_db.inserted.keyword_id)
    conn('default').execute(update_on_duplicate_key)


def query_keyword_id(keyword):
    return conn('default').execute('SELECT id from keywords.keyword where word = :keyword',
                                   {'keyword': keyword}).first()


def query_campaign_id(campaign):
    return conn('default').execute('SELECT id from ads.campaigns where name = :campaign',
                                   {'campaign': campaign}).first()


def query_adgroup_id(adgroup):
    return conn('default').execute('SELECT id from ads.ad_groups where name = :adgroup',
                                   {'adgroup': adgroup}).first()


def query_search_id(keyword_id):
    return conn('default').execute('SELECT id from keywords.search where keyword_id = :keyword_id',
                                   {'keyword_id': keyword_id}).first()


def query_negative_id(campaign_id, ad_group_id, keyword_id):
    return conn('default').query(NegativeKeyword.id) \
        .filter(and_(NegativeKeyword.keyword_id == keyword_id,
                     or_(NegativeKeyword.campaign_id == campaign_id,
                         NegativeKeyword.ad_group_id == ad_group_id))).first()
