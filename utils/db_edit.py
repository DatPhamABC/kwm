from sqlalchemy import text

from db import connection
from stored import config


def conn(source):
    session = config.sessions.get(source, None)
    if session is None:
        session = connection.db(source)
        config.sessions[source] = session
    return session


# def get_keyword_info(keyword_id, keyword_form_type):
#     if keyword_form_type == 'negative':
#         query_string = 'SELECT kw.word, kw.type, \'negative\' as keyword_type, ' \
#                        'CASE ' \
#                        '    WHEN nk.campaign_id IS NOT NULL ' \
#                        '    THEN \'campaign\' ' \
#                        '    WHEN nk.ad_group_id IS NOT NULL ' \
#                        '    THEN \'ad_group\' ' \
#                        'END AS level, ' \
#                        'CASE ' \
#                        '    WHEN nk.campaign_id IS NOT NULL ' \
#                        '    THEN (SELECT name FROM ads.campaigns WHERE id = nk.campaign_id) ' \
#                        '    WHEN nk.ad_group_id IS NOT NULL ' \
#                        '    THEN (SELECT name FROM ads.ad_groups WHERE id = nk.ad_group_id) ' \
#                        'END AS level_name ' \
#                        'FROM keywords.negative nk LEFT JOIN keywords.keyword kw ON nk.keyword_id = kw.id ' \
#                        'WHERE kw.id = :keyword_id'
#
#     if keyword_form_type == 'positive':
#         query_string = 'SELECT kw.word, \'positive\' as keyword_type, kw.type, ' \
#                        '(SELECT name FROM ads.ad_groups ag WHERE ag.id = sk.ad_group_id), ' \
#                        'sk.target_type,' \
#                        'CASE' \
#                        '    WHEN sk.target_type = \'province\' ' \
#                        '    THEN (SELECT name FROM hotels.province p WHERE sk.target_id = p.id) ' \
#                        '    WHEN sk.target_type = \'district\' ' \
#                        '    THEN (SELECT name FROM hotels.district d WHERE sk.target_id = d.id) ' \
#                        '    WHEN sk.target_type = \'hotels\' ' \
#                        '    THEN (SELECT name FROM hotels.hotels h WHERE sk.target_id = h.id) ' \
#                        '    ELSE NULL ' \
#                        'END AS target_name ' \
#                        'FROM keywords.search sk LEFT JOIN keywords.keyword kw ON sk.keyword_id = kw.id ' \
#                        'WHERE kw.id = :keyword_id'
#     query = text(query_string)
#     return conn('default').execute(query, {'keyword_id': keyword_id}).first()


def get_adgroup_id(adgroup_name):
    return conn('default').execute('SELECT id from ads.ad_groups WHERE name=:adgroup_name',
                                   {'adgroup_name': adgroup_name}).first()


