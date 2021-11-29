from keywordmanager.db import connection

sessions = dict()


def conn(source):
    session = sessions.get(source, None)
    if session is None:
        session = connection.db(source)
        sessions[source] = session
    return session
