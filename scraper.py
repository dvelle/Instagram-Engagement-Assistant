from sqlalchemy imoprt create_engine
from sqlalchemy.orm import sessionmaker

from InstagramAPI import InstagramAPI

from models import Scan, Instagram_User, Media, Comment, Interaction

import logging
import sys
import config
import models

# expects to be run as 'python scraper.py user1 user2 ...'

if __name__ == "__main__":
	logger = logging.getLogger("insta_engagement_scraper")
	logger.setLevel(config.DEBUG_LEVEL)

	# gather arguments
	if len(sys.argv == 1):
		logger.error("No input arguments supplied")
		logger.error("Try running as 'python scraper.py <user1> <user2> ...")
		logger.error("Goodbye")
		logger.shutdown()
		exit(1)

	# first arg is program name so we don't care about that, just the rest
	users = str(sys.argv)[1:]
	logger.info("Users loaded from input arguments")

	engine = create_engine(config.DB_CONNECTION)
	logger.debug("Database engine created")

	DBSession = sessionmaker(bind=engine)
	session = DBSession()
	logger.debug("Database session binded to engine")

	# create tables if they don't exist
	Base.metadata.create_all(engine)
	logger.debug("Tables created / exist")

	# setup instagram
	api = InstagramAPI(config.INSTA_USER, config.INSTA_PASS)
	api.login()

	###########################################################################
	## Processing
	###########################################################################
	init_scan()
	user_pks = fetch_users(users, api)




def init_scan():

def fetch_users(usernames, api, session, force_update=False):
	"""
	Fetch the user objects from the api for the given usernames and insert them into the DB
	:usernames The list of usernames to look at
	:api The instagram API
	:session the db session
	:force_update if true the queries will overide previous user entries in the db to update them
	:returns list of pk's of the given usernames.
	"""
	pks = []
	for username in usernames:
		api.getInfoByName(username.strip())
		user = api.LastJson["user"];
		user_pk = user["pk"]

		# does the DB contain the user_pk?
		# would demorgans make this more readable?
		if session.query(Instagram_User).get(user_pk) != None and not force_update:
			# skip this instance since they are already in the db and we are not updating them
			continue

		instagram_user = Instagram_User(instagram_user_id = user["pk"],
		 username=user["username"],
		 followers=user['follower_count'],
		 following=user['following_count'],
		 is_business=user['is_business'],
		 is_private=user['is_private'])

		pk.append(instagram_user.instagram_user_id)

		Logger.debug("Got user info for '" + username + "'")
		# can't make requests too fast
		time.sleep(config.SLEEP_TIME)

	Logger.debug("Gatered users committed to database")
	session.commit()
	return pks

def fetch_media(user_pks, api, session, force_update=False):
	"""
	Fetch the media for these user pk's and isnert them into the DB
	:user_pks a list of instagram user primary keys
	:api The isntagram API
	:session the dbsession
	:force_update if true the queries will overide previous user entries in the db to update them
	:returns a list of media pk's
	"""
	pks = []
	for user_pk in user_pks:
		api.getUserFeed(user_pk)
		media = api.LastJson["items"]

		# is medium the singular? probably not...
		for medium in media:
			media_pk = medium["pk"]

			# make sure pk not in db
			if session.query(Media).get(media_pk) != None and not force_update:
				continue

			pks.append(media_pk)
			is_picture = medium['media_type'] == 1 ? True : False

			instagram_media = Media(media_id=media_pk,
				instagram_user_id=user_pk,
				is_picture=is_picture)

		session.commit()
		
	session.commit()
	return pks
