from database import *

session = next(conn())

tokens = session.query(IdentifyToken).all( )
for token in tokens:
    print(token.user_info.name + ": " + token.token_id)

session.close()