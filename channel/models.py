from __future__ import unicode_literals

from django.db import models

from django.urls import reverse

from django.views.generic import ListView

from django.db.models.signals import pre_save

import uuid

from django.contrib.auth.models import User


# Create your models here.


	#def __str__(self):
		#return self.title

class Source(models.Model):
	created_by = models.CharField(max_length=120, null=True)
	channel_account = models.CharField(max_length=120, null=True)
	updated = models.DateTimeField(auto_now=True, auto_now_add=False, null=True)
	title = models.CharField(max_length=120, null=True)
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)
	account_followers = models.DecimalField(max_digits=100000, decimal_places=0, default = 0, null=True)
	account_followers_followed = models.DecimalField(max_digits=100000, decimal_places=0, default = 0, null=True)
	progress = models.CharField(max_length=120, null=True)

	def __unicode__(self):
		return self.title

	class Meta:
		ordering = ["-timestamp","-updated"]

class Follow(models.Model):
	userid = models.CharField(max_length=120, null=True)
	channel_taken = models.CharField(max_length=120, null=True)
	channel_taken_id = models.CharField(max_length=120, null=True)
	title = models.CharField(max_length=120, null=True)
	updated = models.DateTimeField(auto_now=True, auto_now_add=False, null=True)
	timestamp_save = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)
	followed = models.BooleanField(default = False)
	unfollowed = models.BooleanField(default = False)
	created_by = models.CharField(max_length=120, null=True)

	def __unicode__(self):
		return self.title
	
class Settings(models.Model):
	user = models.OneToOneField(User, null=True, on_delete = models.CASCADE)
	min_follows_per_day = models.CharField(max_length=120, null=True)
	max_follows_per_day = models.CharField(max_length=120, null=True)
	min_waiting_time = models.CharField(max_length=120, null=True)
	max_waiting_time = models.CharField(max_length=120, null=True)
	days_to_unfollow = models.CharField(max_length=120, null=True)
	min_unfollows_per_day = models.CharField(max_length=120, null=True)
	max_unfollows_per_day = models.CharField(max_length=120, null=True)
	min_waiting_time_unfollow = models.CharField(max_length=120, null=True)
	max_waiting_time_unfollow = models.CharField(max_length=120, null=True)
	instagram_account = models.CharField(max_length=120, null=True)
	instagram_password = models.CharField(max_length=120, null=True)
	daily_posts = models.CharField(max_length=120, null=True)
	time_lapse_posting  = models.CharField(max_length=120, null=True)
	hashtags_per_post  = models.CharField(max_length=120, null=True)
	posting_on = models.BooleanField(default = False)
	follow_on = models.BooleanField(default = False)
	unfollow = models.BooleanField(default = False)
	
	def __unicode__(self):
		return self.title

status_choices = ( 
    ("Requested, waiting for dataset to be uploaded", "Requested, waiting for dataset to be uploaded"), 
    ("Dataset uploaded. Please proceed to click on scrape button", "Dataset uploaded. Please proceed to click on scrape button"), 
    ("Dataset used", "Dataset used"), 
) 
  

class Source_content(models.Model):
	created_by = models.CharField(max_length=120, null=True)
	request_name = models.CharField(max_length=120, null=True)
	request = models.CharField(max_length=120, null=True)
	request_number = models.CharField(max_length=120, null=True)
	status = models.CharField(max_length=120, choices=status_choices, default='Requested, waiting for dataset to be uploaded')
	channel_account = models.CharField(max_length=120, null=True)
	updated = models.DateTimeField(auto_now=True, auto_now_add=False, null=True)
	title = models.CharField(max_length=120, null=True)
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)
	dataset_id = models.CharField(max_length=120, null=True)
	api_key = models.CharField(max_length=120, null=True)
	quantity_contents = models.CharField(max_length=120, null=True)



	def __unicode__(self):
		return self.title

	class Meta:
		ordering = ["-timestamp","-updated"]


class Content(models.Model):
	title = models.CharField(max_length=120, null=True)
	updated = models.DateTimeField(auto_now=True, auto_now_add=False, null=True)
	timestamp_save = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)
	used = models.BooleanField(default = False)
	created_by = models.CharField(max_length=120, null=True)
	id_instagram = models.CharField(max_length=120, null=True) # IDs
	type_content = models.CharField(max_length=120, null=True) #type, ecample, image or video
	caption = models.CharField(max_length=120, null=True) #description used in the post
	hashtags = models.CharField(max_length=120, null=True) #hashtags used in the post
	mentions = models.CharField(max_length=120, null=True) # mentions used. Has to be empty
	url_list = models.CharField(max_length=120, null=True) #post URL
	displayUrl = models.CharField(max_length=120, null=True)# image URL
	timestamp = models.CharField(max_length=120, null=True) #updated time
	channel_taken = models.CharField(max_length=120, null=True)  #owner
	#channel_taken_id = models.CharField(max_length=120, null=True)
	likes = models.DecimalField(max_digits=10000, decimal_places=0, null=True) 
	comments= models.DecimalField(max_digits=10000, decimal_places=0, null=True) 

	def __unicode__(self):
		return self.title



class Description(models.Model):
	title = models.CharField(max_length=120, null=True)
	updated = models.DateTimeField(auto_now=True, auto_now_add=False, null=True)
	timestamp_save = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)
	times_used = models.CharField(max_length=120, null=True)
	created_by = models.CharField(max_length=120, null=True)

	def __unicode__(self):
		return self.title

class Hashtag(models.Model):
	title = models.CharField(max_length=120, null=True)
	updated = models.DateTimeField(auto_now=True, auto_now_add=False, null=True)
	timestamp_save = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)
	times_used = models.CharField(max_length=120, null=True)
	created_by = models.CharField(max_length=120, null=True)

	def __unicode__(self):
		return self.title	



