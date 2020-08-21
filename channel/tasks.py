from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import utc
from instabot import Bot
import datetime
import random
import wget
import os
import time
import json

from .models import Source
from .models import Follow
from .models import Settings
from .models import Source_content
from .models import Content
from .models import Description
from .models import Hashtag

from django_celery_beat.models import CrontabSchedule, PeriodicTask
from celery import shared_task

bot = Bot() 


@shared_task
def post():
	user_list = []
	users = Settings.objects.filter(posting_on = True)
	for i in users:
		user_list.append(i.user)

	for u in user_list:
		instance = get_object_or_404(Settings, user=u)	
		instance_instagram_account = instance.instagram_account
		instance_instagram_password = instance.instagram_password
		bot.login(username = instance_instagram_account, password = instance_instagram_password, is_threaded=True)

		description_list = []
		hashtag_list = []
		c_list = []

		settings_all = Settings.objects.get(user = u)
		hashtags_per_post = settings_all.hashtags_per_post

		description_list_all = Description.objects.filter(created_by = u)
		for description in description_list_all:
			description_list.append(description)

		hashtag_list_all = Hashtag.objects.filter(created_by = u)
		for hashtag in hashtag_list_all:
			hashtag_list.append(hashtag)

		content_list_all = Content.objects.filter(created_by = u, used = False)
		for c in content_list_all:
			c_list.append(c)



		#create post

		cap = []
		posted = []

		#choose a random Content 
		content = random.sample(c_list, 1)
		content_id = content[0].id_instagram
		content_url = content[0].displayUrl
		content_channel = content[0].channel_taken

		image_path = wget.download(content_url, out='static/img') #image


		#choose a random description
		description =  random.sample(description_list, 1) 
		description_post =  description[0].title

		#choose 30 random hashtags
		random_hashtags =  random.sample(hashtag_list, int(hashtags_per_post))
		hashtag_list_final = []
		for hashtag in random_hashtags:
			hashtag_list_final.append(hashtag.title)

		joined_hashtags = " ".join(hashtag_list_final)

		cap = description_post  + """
		Credit: @"""+ str(content_channel) + """
		.
		.
		. 
		""" + str(joined_hashtags)

		bot.upload_photo(image_path, caption = cap)


		os.remove(image_path+'.REMOVE_ME') #erase the pic


		#update use field
		content_change = Content.objects.get(id_instagram = content_id)
		content_change.used = True
		content_change.save()

@shared_task
def follow():
	#login into instagram account
	user_list = []
	users = Settings.objects.filter(follow_on = True)
	for i in users:
		user_list.append(i.user)

	for u in user_list:
		instance = get_object_or_404(Settings, user=u)	
		instance_instagram_account = instance.instagram_account
		instance_instagram_password = instance.instagram_password
		min_follows_per_day = instance.min_follows_per_day
		max_follows_per_day = instance.max_follows_per_day
		min_waiting_time = instance.min_waiting_time
		max_waiting_time = instance.max_waiting_time

		#looking for followers in DB
		followers_list = []
		followers_list = Follow.objects.filter(created_by = u)	
	
		follows_per_day = random.randint(int(min_follows_per_day), int(max_follows_per_day))
		#pace = random.randint(int(min_waiting_time), int(max_waiting_time))

		#follows_done = 0
		#while follows_done < follows_per_day:
		if len(followers_list) > 0:

			chosen_user =  random.choice(followers_list) 
			chosen_user_id = chosen_user.userid

			f = Follow.objects.get(userid=chosen_user_id, created_by = u)
			f2 = f.followed
			f3 = f.channel_taken_id
			f4 = f.unfollowed


			if f2 == False and f4 == False :
				bot.login(username = instance_instagram_account, password = instance_instagram_password, is_threaded=True)
				bot.follow(chosen_user_id)

				t = Follow.objects.get(userid=chosen_user_id, created_by = u)
				t.followed = True  # change field
				t.save() # this will update only
		else:
				print('no followers in queue')
			#time.sleep(pace)

	

@shared_task
def unfollow():
	user_list = []
	users = Settings.objects.filter(unfollow = True)
	for i in users:
		user_list.append(i.user)

	for u in user_list:
		instance = get_object_or_404(Settings, user=u)	
		instance_instagram_account = instance.instagram_account
		instance_instagram_password = instance.instagram_password
		min_unfollows_per_day = instance.min_unfollows_per_day
		max_unfollows_per_day = instance.max_unfollows_per_day
		min_waiting_time_unfollow = instance.min_waiting_time_unfollow
		max_waiting_time_unfollow = instance.max_waiting_time_unfollow
		days_to_unfollow = instance.days_to_unfollow

	#looking for followers in DB
		followers_list = []
		followers_list = Follow.objects.filter(created_by = u, followed = True, unfollowed = False)	



		unfollows_per_day = random.randint(int(min_unfollows_per_day), int(max_unfollows_per_day))
#	pace = random.randint(int(min_waiting_time_unfollow), int(max_waiting_time_unfollow))

#	unfollows_done = 0
#	while unfollows_done < unfollows_per_day:
#		#choosing a random user
		if len(followers_list) > 0:

			chosen_user =  random.choice(followers_list) 
			chosen_user_id = chosen_user.userid
			#get fata of past actions with the follower
			f = Follow.objects.get(userid=chosen_user_id, created_by = u)
			f2 = f.followed
			f3 = f.channel_taken_id
			last_updated = f.updated

			now = datetime.datetime.utcnow().replace(tzinfo=utc)
			timediff = now - last_updated
			seconds_passed = timediff.total_seconds()

			set_time = Settings.objects.get(user = u)	
			set_time_days_to_unfollow = set_time.days_to_unfollow
			set_time_days_to_unfollow_seconds = int(set_time_days_to_unfollow) * 24 * 60 * 60
			t = False
			if seconds_passed > set_time_days_to_unfollow_seconds:
				t = True

			#follow and save
			if t == True :
				if f2 == True or f4 == False :
					bot.login(username = instance_instagram_account, password = instance_instagram_password, is_threaded=True)
					bot.unfollow(chosen_user_id)

					t = Follow.objects.get(userid=chosen_user_id, created_by = u)
					t.unfollowed = True  # change field
					t.save() # this will update only

					#time.sleep(pace)



