from db import connection
from stored import config


def conn(source):
    session = config.sessions.get(source, None)
    if session is None:
        session = connection.db(source)
        config.sessions[source] = session
    return session


def get_campaign_id(campaign_name):
    return conn('default').execute('SELECT id from ads.campaigns WHERE name=:campaign_name',
                                   {'campaign_name': campaign_name}).first()


def get_adgroup_id(adgroup_name):
    return conn('default').execute('SELECT id from ads.ad_groups WHERE name=:adgroup_name',
                                   {'adgroup_name': adgroup_name}).first()


class Filter:
    def __init__(self, campaign, adgroup, province, district, hotel):
        self.campaign = campaign
        self.adgroup = adgroup
        self.province = province
        self.district = district
        self.hotel = hotel

    def get_campaign_list(self):
        return conn('default').execute('SELECT name from ads.campaigns').all()

    def get_adgroup_list(self):
        return conn('default').execute('SELECT name from ads.ad_groups').all()

    def get_province_list(self):
        return conn('default').execute('SELECT name from hotels.province').all()

    def get_district_list(self):
        return conn('default').execute('SELECT name from hotels.district').all()

    def get_hotel_list(self):
        return conn('default').execute('SELECT hotel_name from hotels.hotels').all()

    def get_keyword_list(self):
        campaign_id = get_campaign_id(self.campaign)
        adgroup_id = get_adgroup_id(self.adgroup)
        keyword_list = []
        if campaign_id is not None:
            campaign_id = campaign_id[0]
            query = conn('default').execute(
                'SELECT nk.id, kw.word, kw.type, \'campaign\' as filter_by, \'negative\' as keyword_type, '
                '(SELECT name FROM ads.campaigns WHERE id = nk.campaign_id) as campaign_name '
                'FROM keywords.negative nk '
                'LEFT JOIN keywords.keyword kw ON nk.keyword_id = kw.id '
                'WHERE nk.campaign_id = :campaign_id',
                {'campaign_id': campaign_id}
            ).all()
            keyword_list.extend(query)

        if adgroup_id is not None:
            adgroup_id = adgroup_id[0]
            query = conn('default').execute(
                'SELECT nk.id, kw.word, kw.type, \'ad_group\' as filter_by, \'negative\' as keyword_type, '
                '(SELECT name FROM ads.ad_groups WHERE id = nk.ad_group_id) as adgroup_name '
                'FROM keywords.negative nk '
                'LEFT JOIN keywords.keyword kw ON nk.keyword_id = kw.id '
                'WHERE nk.ad_group_id = :adgroup_id',
                {'adgroup_id': adgroup_id}
            ).all()
            keyword_list.extend(query)
            query = conn('default').execute(
                'SELECT sk.id, kw.word, kw.type, \'ad_group\' as filter_by, \'positive\' as keyword_type, '
                '(SELECT name FROM ads.ad_groups WHERE id = sk.ad_group_id) as adgroup_name, '
                'CASE WHEN sk.target_type = \'hotels\' '
                'THEN (SELECT hotel_name FROM hotels.hotels WHERE id = sk.target_id) '
                'WHEN sk.target_type = \'district\' '
                'THEN (SELECT name FROM hotels.district WHERE id = sk.target_id) '
                'WHEN sk.target_type = \'province\' '
                'THEN (SELECT name FROM hotels.province WHERE id = sk.target_id) '
                'ELSE Null '
                'END as target_name, '
                'sk.target_type, kw.is_active '
                'FROM keywords.search sk '
                'LEFT JOIN keywords.keyword kw ON sk.keyword_id = kw.id '
                'WHERE sk.ad_group_id = :adgroup_id',
                {'adgroup_id': adgroup_id}
            ).all()
            keyword_list.extend(query)

        return keyword_list
