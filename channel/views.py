from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.timezone import utc
from instabot import Bot
import datetime
import random
import config
import json
import random
import wget
import time
import os


from .models import Source
from .models import Follow
from .models import Settings
from .models import Source_content
from .models import Content
from .models import Description
from .models import Hashtag

from .tasks import post


from .forms import PostForm
from .forms import Follow_SettingsForm
from .forms import Instagram_SettingsForm
from .forms import CreateUserForm
from .forms import Posting_SettingsForm
from .forms import ScrappingForm
from .forms import Post_descriptionForm
from .forms import Post_hashtagForm




#instance = Settings.user
#instance = auth.User.id
#get_object_or_404(Settings, user=user_name)
#a = instance.get_username()

#account_ig = ""
#account_ig = instance.instagram_account
#pass_ig = instance.instagram_password

#if account_ig != "":
bot = Bot() 
#bot.login(username = "rudolphsebas", password = "Filadelfia1!!", is_threaded=True)




# Create your views here.

def login_view(request):
	if request.user.is_authenticated:	
		return redirect('/dashboard')
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password = request.POST.get('password')

			user = authenticate (request, username = username, password = password)
			
			if user is not None:
				login(request, user)
				return redirect('/dashboard')
			else:
				messages.info(request, 'username or password is incorrect')

		context = {
			"title": "Welcome to the Channel Generator",
		}
		return render(request, "login.html", context)

def logoutUser(request):
	logout(request)
	return redirect('/')


def register_view(request):
	if request.user.is_authenticated:	
		return redirect('dashboard')
	else:
		form = CreateUserForm()
		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				user = form.save()
				Settings.objects.create(
					user = user,
					)

				messages.success(request, "Succesfully Registered Account. Please Login")
				return redirect("channel:login")

		context = {
			"title": "Register",
			'form': form,
		}
		return render(request, "register.html", context)


@login_required(login_url = '/')
def dashboard_view(request):
	user_name_id = request.user.id
	user_name = request.user
	
	# Get Settings data from DB for context
	settings_all = get_object_or_404(Settings, user=user_name_id)
	min_follows_per_day = settings_all.min_follows_per_day
	max_follows_per_day = settings_all.max_follows_per_day
	min_waiting_time = settings_all.min_waiting_time
	max_waiting_time = settings_all.max_waiting_time
	days_to_unfollow = settings_all.days_to_unfollow
	instagram_account = settings_all.instagram_account
	instagram_password = settings_all.instagram_password
	daily_posts = settings_all.daily_posts
	time_lapse_posting = settings_all.time_lapse_posting
	min_unfollows_per_day = settings_all.min_unfollows_per_day
	max_unfollows_per_day = settings_all.max_unfollows_per_day
	min_waiting_time_unfollow = settings_all.min_waiting_time_unfollow
	max_waiting_time_unfollow = settings_all.max_waiting_time_unfollow
	posting_on = settings_all.posting_on
	follow_on = settings_all.follow_on
	unfollow = settings_all.unfollow

	# Finnish Get Settings data from DB fro context
	
	total_posted= Content.objects.filter(created_by=user_name,  used = True).count()
	total_posted_queue = Content.objects.filter(created_by=user_name,  used = False).count()

	total_desc = Description.objects.filter(created_by=user_name).count()
	total_hash = Hashtag.objects.filter(created_by=user_name).count()

	total_followed = Follow.objects.filter(created_by=user_name,  followed = True).count()
	total_followers_queue = Follow.objects.filter(created_by=user_name,  followed = False).count()

	total_unfollowed = Follow.objects.filter(created_by=user_name,  followed = True, unfollowed = True).count()

	#validation of time in settinfs we have to wait until unfollow
	unfollow_queue = Follow.objects.filter(created_by=user_name,  followed = True, unfollowed = False).count()
	unfollow_queue_list = Follow.objects.filter(created_by=user_name,  followed = True, unfollowed = False)

	set_time = Settings.objects.get(user = user_name)	
	n = 0
	for item in unfollow_queue_list:
		last_updated = item.updated
		now = datetime.datetime.utcnow().replace(tzinfo=utc)
		timediff = now - last_updated
		seconds_passed = timediff.total_seconds()
		set_time_days_to_unfollow = set_time.days_to_unfollow
		set_time_days_to_unfollow_seconds = int(set_time_days_to_unfollow) * 24 * 60 * 60
		t = False
		if seconds_passed > set_time_days_to_unfollow_seconds:
			n = n + 1



	context = {
		'min_follows_per_day': min_follows_per_day,
		'max_follows_per_day': max_follows_per_day,
		'min_waiting_time': min_waiting_time,
		'max_waiting_time' : max_waiting_time,
		'days_to_unfollow': days_to_unfollow,
		'instagram_account': instagram_account,
		'daily_posts': daily_posts,
		'time_lapse_posting': time_lapse_posting,
		'total_followed': total_followed,
		'total_followers_queue': total_followers_queue,
		'total_posted': total_posted,
		'total_posted_queue': total_posted_queue,
		'min_unfollows_per_day':min_unfollows_per_day,
		'max_unfollows_per_day':max_unfollows_per_day,
		'min_waiting_time_unfollow':min_waiting_time_unfollow,
		'max_waiting_time_unfollow':max_waiting_time_unfollow,
		'total_desc':total_desc,
		'total_hash':total_hash,
		'total_unfollowed': total_unfollowed,
		'unfollow_queue': unfollow_queue,
		'unfollow_queue_accounting_for_time': n,
		'posting_on': posting_on,
		'follow_on': follow_on,
		'unfollow_on': unfollow
	
	

	}

	return render(request, "dashboard.html", context)


@login_required(login_url = '/')
def settings_view(request):
	user_name_id = request.user.id

	
	# Instagram Settings form
	form_settings_ig = Instagram_SettingsForm(request.POST or None, request.FILES or None)
	if form_settings_ig.is_valid():
		instance = get_object_or_404(Settings, user=user_name_id)
		form = Instagram_SettingsForm(request.POST or None, request.FILES or None, instance = instance)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.save()
			messages.success(request, "Succesfully edited Instagram settings")
		return redirect("channel:settings")

	# Follow Settings form
	form_settings = Follow_SettingsForm(request.POST or None, request.FILES or None)
	if form_settings.is_valid():
		instance = get_object_or_404(Settings, user=user_name_id)
		form = Follow_SettingsForm(request.POST or None, request.FILES or None, instance = instance)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.save()
			messages.success(request, "Succesfully edited Follow/ Unfollow settings")
		return redirect("channel:settings")

	#Posting Settings form
	form_settings_posting = Posting_SettingsForm(request.POST or None, request.FILES or None)
	if form_settings_posting.is_valid():
		instance = get_object_or_404(Settings, user=user_name_id)
		form = Posting_SettingsForm(request.POST or None, request.FILES or None, instance = instance)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.save()
			messages.success(request, "Succesfully edited Posting settings")
		return redirect("channel:settings")

	# Get Settings data from DB for context
	settings_all = get_object_or_404(Settings, user=user_name_id)
	min_follows_per_day = settings_all.min_follows_per_day
	max_follows_per_day = settings_all.max_follows_per_day
	min_waiting_time = settings_all.min_waiting_time
	max_waiting_time = settings_all.max_waiting_time
	days_to_unfollow = settings_all.days_to_unfollow
	instagram_account = settings_all.instagram_account
	instagram_password = settings_all.instagram_password
	daily_posts = settings_all.daily_posts
	hashtags_per_post = settings_all.hashtags_per_post
	time_lapse_posting = settings_all.time_lapse_posting
	min_unfollows_per_day = settings_all.min_unfollows_per_day
	max_unfollows_per_day = settings_all.max_unfollows_per_day
	min_waiting_time_unfollow = settings_all.min_waiting_time_unfollow
	max_waiting_time_unfollow = settings_all.max_waiting_time_unfollow
	# Finnish Get Settings data from DB fro context


	queryset_list = Source.objects.all()
	total_accounts_database = 0
	for obj in queryset_list:
		total_accounts_database = total_accounts_database + 1 #count number of accounts in database

	paginator = Paginator(queryset_list, 25) # Show 25 contacts per page.
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)

	queryset_list_follow = Follow.objects.all()
	total_followers_database = 0
	for obj in queryset_list_follow:
		total_followers_database = total_followers_database + 1 #count number of user accounts in database

	count = 0
	for obj in queryset_list:
		number = obj.id
		count = Follow.objects.filter(followed=True).count()
		t = Source.objects.get(id=number)
		t.account_followers_followed = count  # change field
		t.save() # this will update only


	context = {
		"title": "Settings",
		"object_list": queryset_list,
		'page_obj': page_obj,
		'accounts_database': total_accounts_database,
		'followers_database': total_followers_database,
		"form_settings": form_settings,
		'form_settings_ig': form_settings_ig,
		'form_settings_posting': form_settings_posting,
		'min_follows_per_day': min_follows_per_day,
		'max_follows_per_day': max_follows_per_day,
		'min_waiting_time': min_waiting_time,
		'max_waiting_time' : max_waiting_time,
		'days_to_unfollow': days_to_unfollow,
		'instagram_account': instagram_account,
		'instagram_password': instagram_password,
		'daily_posts': daily_posts,
		'hashtags_per_post': hashtags_per_post,
		'time_lapse_posting': time_lapse_posting,
		'min_unfollows_per_day':min_unfollows_per_day,
		'max_unfollows_per_day':max_unfollows_per_day,
		'min_waiting_time_unfollow':min_waiting_time_unfollow,
		'max_waiting_time_unfollow':max_waiting_time_unfollow,


	}
	return render(request, "settings.html", context)




@login_required(login_url = '/')
def follow_accounts_view(request):

	user_name_id = request.user.id
	user_name = request.user
	
	queryset_list = Source.objects.filter(created_by=user_name)
	total_accounts_database = 0
	for obj in queryset_list:
		total_accounts_database = total_accounts_database + 1 #count number of accounts in database

	queryset_list_follow = Follow.objects.filter(created_by=user_name)
	total_followers_database = 0
	for obj in queryset_list_follow:
		total_followers_database = total_followers_database + 1 #count number of user accounts in database

	#save provess field in Source database
	for obj in queryset_list:
		count = Follow.objects.filter(created_by=user_name, channel_taken = obj.channel_account, followed = True).count()
		if total_followers_database != 0:
			result = count/ total_followers_database * 100
			#update followers in source account fields
			obj.progress = result  # change field
			obj.save() # this will update only


	paginator = Paginator(queryset_list, 3) # Show 25 contacts per page.
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)


	# form to create Accounts to Follow Unfollow
	form = PostForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		#instance.user = user_name
		#instance.user.save()
		instance_id = instance.id
		print (instance_id)
		user_saver = Source.objects.get(id=instance_id)

		user_saver.created_by = str(user_name)
		user_saver.save()

		messages.success(request, "Succesfully Created Account")
		return redirect("channel:follow_accounts")



	# Cuenta Followed people en cada Account
	count = 0
	for obj in queryset_list:
		count = Follow.objects.filter(created_by=user_name, channel_taken = obj.channel_account, followed=True).count()
		obj.account_followers_followed = count  # change field
		obj.save() # this will update only

	context = {
		"title": "Manage your account to follow",
		"object_list": queryset_list,
		'page_obj': page_obj,
		'accounts_database': total_accounts_database,
		'followers_database': total_followers_database,
		"form": form
	}
	return render(request, "follow_accounts.html", context)

@login_required(login_url = '/')
def content_accounts_view(request):
	user_name_id = request.user.id
	user_name = request.user

	queryset_list = Source_content.objects.filter(created_by=user_name)
	total_scrapping_requests = 0
	for obj in queryset_list:
		total_scrapping_requests = total_scrapping_requests + 1 #count number of accounts in database

	paginator = Paginator(queryset_list, 3) # Show 25 contacts per page.
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)


	# form to create Accounts to gather content
	form_content = ScrappingForm(request.POST or None, request.FILES or None)
	if form_content.is_valid():
		instance = form_content.save(commit=False)
		instance.save()
		instance_id = instance.id
		user_saver = Source_content.objects.get(id=instance_id)
		user_saver.created_by = str(user_name)
		user_saver.save()

		messages.success(request, "Succesfully Created Scraping Request")
		return redirect("channel:content_accounts")

	context = {
		"title": "Manage your accounts to get content from",
		"object_list": queryset_list,
		'page_obj': page_obj,
		'total_accounts_database': total_scrapping_requests,
		"form": form_content,

	}
	return render(request, "content_accounts.html", context)

@login_required(login_url = '/')
def content_view(request):
	user_name_id = request.user.id
	user_name = request.user

	queryset_list = Content.objects.filter(created_by=user_name, used = False).order_by('timestamp')
	total_accounts_database = 0
	for obj in queryset_list:
		total_accounts_database = total_accounts_database + 1 #count number of accounts in database

	channel_list = []
	value_list = []
	a = Content.objects.values('channel_taken').distinct()
	for item in a:
		channel_list.append(item['channel_taken'])
		value_list.append(Content.objects.filter(created_by=user_name, used = False, channel_taken = item['channel_taken'] ).count())

	dict_values = dict(zip(channel_list, value_list))

	info_list=[]
	value = ''

	for key, value in dict_values.items():
		value = str(key)+ ' has '+ str(value)+ ' contents stored. '
		info_list.append(value)



	paginator = Paginator(queryset_list, 60) 
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	
	context = {
		"title": "Supervise your contents",
		"object_list": queryset_list,
		'page_obj': page_obj,
		'info_list': info_list,

	}
	return render(request, "content.html", context)





@login_required(login_url = '/')
def descriptions_view(request):
	user_name_id = request.user.id
	user_name = request.user

	queryset_list_description = Description.objects.filter(created_by=user_name)
	total_descriptions_database = 0
	for obj in queryset_list_description:
		total_descriptions_database = total_descriptions_database + 1 #count number of accounts in database

	paginator = Paginator(queryset_list_description, 3) # Show 25 descriptions per page.
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)


	# form to create Descriptions
	form_description = Post_descriptionForm(request.POST or None, request.FILES or None)
	if form_description.is_valid():
		instance = form_description.save(commit=False)
		instance.save()
		instance_id = instance.id
		user_saver = Description.objects.get(id=instance_id)
		user_saver.created_by = str(user_name)
		user_saver.save()

		messages.success(request, "Succesfully Created Description")
		return redirect("channel:descriptions")




	context = {
		"title": "Manage your descriptions",
		'object_list_description': queryset_list_description,
		'page_obj': page_obj,
		'total_descriptions_database':total_descriptions_database,
		'form_description': form_description,
	}
	return render(request, "descriptions.html", context)

@login_required(login_url = '/')
def hashtags_view(request):
	user_name_id = request.user.id
	user_name = request.user

	queryset_list_hashtag = Hashtag.objects.filter(created_by=user_name)
	total_hashtags_database = 0
	for obj in queryset_list_hashtag:
		total_hashtags_database = total_hashtags_database + 1 #count number of accounts in database

	paginator = Paginator(queryset_list_hashtag, 3) # Show 25 contacts per page.
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)

	# form to create Hashtags
	form_hashtag = Post_hashtagForm(request.POST or None, request.FILES or None)
	if form_hashtag.is_valid():
		instance = form_hashtag.save(commit=False)
		instance.save()
		instance_id = instance.id
		user_saver = Hashtag.objects.get(id=instance_id)
		user_saver.created_by = str(user_name)
		user_saver.save()

		messages.success(request, "Succesfully Created Hashtag")
		return redirect("channel:hashtags")



	context = {
		"title": "Manage your hashtags",
		'object_list_hashtag': queryset_list_hashtag,
		'page_obj': page_obj,
		'total_hashtags_database':total_hashtags_database,
		'form_hashtag': form_hashtag,
	}
	return render(request, "hashtags.html", context)

def post_delete(request, id):
	user_name = request.user
	instance = get_object_or_404(Source, id=id, created_by = user_name)
	instance.delete()

	Follow.objects.filter(channel_taken_id=id).delete()

	messages.success(request, "Succesfully deleted account")
	
	return redirect("channel:follow_accounts")

def delete_source_contents(request, id):
	user_name = request.user
	instance = get_object_or_404(Source_content, id=id, created_by = user_name)
	instance.delete()

	Content.objects.filter(channel_taken_id=id).delete()

	messages.success(request, "Succesfully deleted account")
	
	return redirect("channel:content_accounts")


def fetch_users(request, id):
	#login into instagram account
	user_name_id = request.user.id
	user_name = request.user
	follows_done = 0
	instance = get_object_or_404(Settings, user_id=request.user.id)	
	instance_instagram_account = instance.instagram_account
	instance_instagram_password = instance.instagram_password
	bot.login(username = instance_instagram_account, password = instance_instagram_password, is_threaded=True)


	#followers fetcher
	queryset_list = Source.objects.filter(created_by = user_name)
	queryset_list_follow = Follow.objects.filter(created_by = user_name)
	follower_list = []
	choosen_channel = ''
	for obj in queryset_list:
		if obj.id == id:
			choosen_channel = obj.channel_account
	follower_list = bot.get_user_followers(choosen_channel)
	n = 0

	for i in follower_list:
		b2 = Follow(title = choosen_channel, userid=i, channel_taken = choosen_channel, created_by = user_name, channel_taken_id = id)
		b2.save()
		n = n + 1
	
	#update followers in source account fields
	t = Source.objects.get(id=id, created_by = user_name)
	t.account_followers = n  # change field
	t.save() # this will update only


	messages.success(request, n)	

	return redirect("channel:follow_accounts")


def delete_users(request, id):
	user_name_id = request.user.id
	user_name = request.user
	Follow.objects.filter(channel_taken_id=id, created_by = user_name).delete()

	t = Source.objects.get(id=id)
	t.account_followers = 0  # change field
	t.save() # this will update only

	messages.success(request, "Succesfully deleted users")
	return redirect("channel:follow_accounts")

def delete_descriptions(request, id):
	user_name = request.user
	instance = get_object_or_404(Description, id=id, created_by = user_name)
	instance.delete()

	messages.success(request, "Succesfully deleted description")
	
	return redirect("channel:descriptions")

def delete_hashtags(request, id):
	user_name = request.user
	instance = get_object_or_404(Hashtag, id=id, created_by = user_name)
	instance.delete()

	messages.success(request, "Succesfully deleted hashtag")
	
	return redirect("channel:hashtags")

def delete_contents(request, id):
	user_name = request.user
	instance = get_object_or_404(Content, id=id, created_by = user_name)
	instance.delete()

	messages.success(request, "Succesfully deleted Content")
	
	return redirect("channel:contents")


def follow_individual(request):
	#login into instagram account
	user_name_id = request.user.id
	user_name = request.user
	instance = get_object_or_404(Settings, user_id=request.user.id)	
	instance_instagram_account = instance.instagram_account
	instance_instagram_password = instance.instagram_password
	bot.login(username = instance_instagram_account, password = instance_instagram_password, is_threaded=True)

	#looking for followers in DB
	followers_list = []
	followers_list = Follow.objects.filter(created_by = user_name)	

	#choosing a random user
	chosen_user =  random.choice(followers_list) 
	chosen_user_id = chosen_user.userid

	#get data of past actions with the follower
	f = Follow.objects.get(userid=chosen_user_id, created_by = user_name)
	f2 = f.followed
	f3 = f.channel_taken_id
	f4 = f.unfollowed

	#follow and save
	if f2 == False and f4 == False:
		bot.follow(chosen_user_id)

		t = Follow.objects.get(userid=chosen_user_id, created_by = user_name)
		t.followed = True  # change field
		t.save() # this will update only

		messages.success(request, 'We followed '+str(chosen_user_id)+' succesfully')
	else:
		messages.success(request, 'Error: could not follow')
	return redirect("channel:dashboard")


def unfollow_individual(request):
	#login into instagram account
	user_name_id = request.user.id
	user_name = request.user
	instance = get_object_or_404(Settings, user_id=request.user.id)	
	instance_instagram_account = instance.instagram_account
	instance_instagram_password = instance.instagram_password
	bot.login(username = instance_instagram_account, password = instance_instagram_password, is_threaded=True)

	#looking for followers in DB
	followers_list = []
	followers_list = Follow.objects.filter(created_by = user_name, followed = True, unfollowed = False)	

	#choosing a random user
	chosen_user =  random.choice(followers_list) 
	chosen_user_id = chosen_user.userid

	#get fata of past actions with the follower
	f = Follow.objects.get(userid=chosen_user_id, created_by = user_name)
	f2 = f.followed
	f3 = f.channel_taken_id
	f4 = f.unfollowed
	last_updated = f.updated



	#validation of time in settinfs we have to wait until unfollow
	now = datetime.datetime.utcnow().replace(tzinfo=utc)
	timediff = now - last_updated
	seconds_passed = timediff.total_seconds()

	set_time = Settings.objects.get(user = user_name)	
	set_time_days_to_unfollow = set_time.days_to_unfollow
	set_time_days_to_unfollow_seconds = int(set_time_days_to_unfollow) * 24 * 60 * 60
	t = False
	if seconds_passed > set_time_days_to_unfollow_seconds:
		t = True

	#follow and save
	if t == True :
		if f2 == True or f4 == False :
			bot.unfollow(chosen_user_id)

			t = Follow.objects.get(userid=chosen_user_id, created_by = user_name)
			t.unfollowed = True  # change field
			t.save() # this will update only

			messages.success(request, 'We unfollowed '+str(chosen_user_id)+' succesfully')
	else:
		messages.success(request, 'Error: could not unfollow')	

	return redirect("channel:dashboard")

def how_view(request):
	context = {
	"title": "How it works",
	#"object_list": queryset_list,
	#'page_obj': page_obj,

	}

	return render(request, "howitworks.html", context)


def fetch_content(request, id):
	#login into instagram account
	user_name_id = request.user.id
	user_name = request.user
	instance = get_object_or_404(Settings, user_id=request.user.id)	
	instance_instagram_account = instance.instagram_account
	instance_instagram_password = instance.instagram_password
	bot.login(username = instance_instagram_account, password = instance_instagram_password, is_threaded=True)

	#Scrape Intagram
	settings = Source_content.objects.get(id=id)	
	dataset = settings.dataset_id
	api_key = settings.api_key

	
	dataset = Request('https://api.apify.com/v2/datasets/'+str(dataset)+'/items?token='+str(api_key)+'&format=json')
	df = urlopen(dataset).read()
	df_json = json.loads(df)

	#Create variables and dataframe
	channel_list = []
	e = 0
	f = 0
	n = 0
	for i in df_json:
		if i.get("comments") != '0' or i.get("likes") != '0'or i.get("likes") != 0 or i.get("likes") != 0:
			f = f+1	
			if type(i.get("mentions"))==list:
				if len(i.get("mentions")) < 2:
					if i.get("caption") != []:
						if i.get("type") == 'Image':
							if Content.objects.filter(id_instagram = i.get("id"), created_by = user_name).exists():
								e = e + 1
							else:
								instance = Content(created_by = user_name, 
									title = i.get("id"),
									id_instagram = i.get("id"),
									type_content = i.get("type"),
									caption = i.get("caption"),
									hashtags = i.get("hashtags"),
									mentions = i.get("mentions"),
									url_list = i.get("url"),
									displayUrl = i.get("displayUrl"),
									timestamp = i.get("timestamp"),
									channel_taken = i.get("ownerUsername"),
									likes = i.get("likesCount"),
									comments= i.get("commentsCount"), 
									)
								channel_list.append(i.get("ownerUsername"))
								instance.save()
								n = n + 1
						else:
							e = e + 1
					else:
						e = e + 1			
				else:
					e = e + 1
			else:
				e = e + 1
		else:
			e = e + 1
	
	settings.status = 'Dataset used'
	settings.quantity_contents = n
	settings.save()

	#account = Accounts(created_by = user_name, title = i.get("id"))
	#account.save()
	#messages.success(request, 'We fetched '+str(n)+' contents.'+' Discarded contents'+str(e))

	messages.success(request, f)

	
	return redirect("channel:content_accounts")

def post_individual(request):
	#login into instagram account
	user_name_id = request.user.id
	user_name = request.user
	instance = get_object_or_404(Settings, user_id=request.user.id)	
	instance_instagram_account = instance.instagram_account
	instance_instagram_password = instance.instagram_password
	bot.login(username = instance_instagram_account, password = instance_instagram_password, is_threaded=True)

	description_list = []
	hashtag_list = []
	c_list = []

	settings_all = Settings.objects.get(user = user_name)
	hashtags_per_post = settings_all.hashtags_per_post

	description_list_all = Description.objects.filter(created_by = user_name)
	for description in description_list_all:
		description_list.append(description)

	hashtag_list_all = Hashtag.objects.filter(created_by = user_name)
	for hashtag in hashtag_list_all:
		hashtag_list.append(hashtag)

	content_list_all = Content.objects.filter(created_by = user_name, used = False)
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
	content_mention = content[0].mentions
	#m1 = content_mention.replace("[", '')
	#m2 = m1.replace("]", '')
	m3 = content_mention[2:-2]
	m4 = ' / @'+str(m3)
	if m4 == ' / @':
		m4 = ""

	print(m3)
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
	Credit: @"""+ str(content_channel) +str(m4) +"""
	.
	.
	. 
	""" + str(joined_hashtags)

	bot.upload_photo(image_path, caption = cap)


	os.remove(image_path+'.REMOVE_ME') #erase the pic


	#update use field
	content_change = Content.objects.filter(id_instagram = content_id)
	for obj in content_change:
		obj.used = True
		obj.save()


	messages.success(request,  'Posted content number ' + str(content_id))
	return redirect("channel:dashboard")


def posting_on(request):
	user_name_id = request.user.id
	user_name = request.user
	settings_all = get_object_or_404(Settings, user=user_name)
	hashtags_per_post = settings_all.hashtags_per_post

	descriptions_count =  Description.objects.filter(created_by=user_name).count()
	hashtags_count =  Hashtag.objects.filter(created_by=user_name).count()

	if descriptions_count > 0:
		if hashtags_count >= int(hashtags_per_post):
			settings_all = get_object_or_404(Settings, user=user_name_id)
			status = True
			t = Settings.objects.get(user=user_name_id)
			t.posting_on = status  # change field
			t.save() # this will update only
			messages.success(request,  'Automatic Posting is ON')
			return redirect("channel:dashboard")
		else:
			messages.success(request,  'Error: add more hashtags or change your hashtags settings')
			return redirect("channel:dashboard")
	else:
		messages.success(request,  'Error: add more descriptions')
		return redirect("channel:dashboard")	


def follow_on(request):
	user_name_id = request.user.id
	user_name = request.user
	settings_all = get_object_or_404(Settings, user=user_name_id)
	status = True
	t = Settings.objects.get(user=user_name_id)
	t.follow_on = status  # change field
	t.save() # this will update only
	messages.success(request,  'Automatic Follow is ON')	
	return redirect("channel:dashboard")


def unfollow_on(request):
	user_name_id = request.user.id
	user_name = request.user
	settings_all = get_object_or_404(Settings, user=user_name_id)
	status = True
	t = Settings.objects.get(user=user_name_id)
	t.unfollow = status  # change field
	t.save() # this will update only
	messages.success(request,  'Automatic Unfollow is ON')	
	return redirect("channel:dashboard")

def posting_off(request):
	user_name_id = request.user.id
	user_name = request.user
	settings_all = get_object_or_404(Settings, user=user_name_id)
	status = False
	t = Settings.objects.get(user=user_name_id)
	t.posting_on = status  # change field
	t.save() # this will update only
	messages.success(request,  'Automatic Posting is OFF')
	return redirect("channel:dashboard")

def follow_off(request):
	user_name_id = request.user.id
	user_name = request.user
	settings_all = get_object_or_404(Settings, user=user_name_id)
	status = False
	t = Settings.objects.get(user=user_name_id)
	t.follow_on = status  # change field
	t.save() # this will update only
	messages.success(request,  'Automatic Follow is OFF')	
	return redirect("channel:dashboard")


def unfollow_off(request):
	user_name_id = request.user.id
	user_name = request.user
	settings_all = get_object_or_404(Settings, user=user_name_id)
	status = False
	t = Settings.objects.get(user=user_name_id)
	t.unfollow = status  # change field
	t.save() # this will update only
	messages.success(request,  'Automatic Unfollow is OFF')	
	return redirect("channel:dashboard")


