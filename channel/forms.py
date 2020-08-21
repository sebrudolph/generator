from django.forms import ModelForm
from django import forms

from .models import Source
from .models import Source_content
from .models import Follow
from .models import Settings
from .models import Description
from .models import Hashtag

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class PostForm(forms.ModelForm):
	class Meta:
		model = Source
		fields = [
			"channel_account",
			#"account_followers",
			#"account_followers_followed"
		]

class ScrappingForm(forms.ModelForm):
	class Meta:
		model = Source_content
		fields = [
			"request",
			#"account_followers",
			#"account_followers_followed"
		]

class Post_descriptionForm(forms.ModelForm):
	class Meta:
		model = Description
		fields = [
			"title",
		]

class Post_hashtagForm(forms.ModelForm):
	class Meta:
		model = Hashtag
		fields = [
			"title",
		]

class Follow_SettingsForm(forms.ModelForm):
	class Meta:
		model = Settings
		fields = [
			"min_follows_per_day",
			"max_follows_per_day",
			"min_waiting_time",
			"max_waiting_time",
			'days_to_unfollow', 
			'min_unfollows_per_day',
			'max_unfollows_per_day',
			'min_waiting_time_unfollow',
			'max_waiting_time_unfollow',
		]

class Instagram_SettingsForm(forms.ModelForm):
	class Meta:
		model = Settings
		fields = [
			"instagram_account",
			"instagram_password",
		]

class Posting_SettingsForm(forms.ModelForm):
	class Meta:
		model = Settings
		fields = [
			'hashtags_per_post',
		]


class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = [
			"username",
			"email",
			"password1",
			"password2",

		]
