from django.contrib import admin

# Register your models here.
from .models import Follow
from .models import Source
from .models import Settings
from .models import Source_content
from .models import Content
from .models import Description
from .models import Hashtag

class FollowModelAdmin(admin.ModelAdmin):
	list_display = ['userid', 'created_by', 'channel_taken', 'channel_taken_id','updated', 'timestamp_save', 'followed', 'unfollowed']
	class Meta:
		model = Follow


admin.site.register(Follow, FollowModelAdmin)

class SourceModelAdmin(admin.ModelAdmin):
	list_display = ['channel_account', 'created_by','account_followers', 'account_followers_followed', 'updated', 'timestamp']
	class Meta:
		model = Source

admin.site.register(Source, SourceModelAdmin)


class SettingsModelAdmin(admin.ModelAdmin):
	list_display = ['instagram_account','instagram_password', 'posting_on','follow_on','unfollow', 'user','min_follows_per_day', 'max_follows_per_day', 'min_waiting_time', 'max_waiting_time', 'days_to_unfollow', 'min_unfollows_per_day', 'max_unfollows_per_day','min_waiting_time_unfollow','max_waiting_time_unfollow','hashtags_per_post', 'daily_posts']
	class Meta:
		model = Settings

admin.site.register(Settings, SettingsModelAdmin)




class ContentModelAdmin(admin.ModelAdmin):
	list_display = ['created_by', 'channel_taken', 'likes', 'comments','id_instagram', 'type_content', 'used', 'caption', 'hashtags', 'mentions','url_list', 'displayUrl', 'timestamp']
	class Meta:
		model = Content


admin.site.register(Content, ContentModelAdmin)

class DescriptionModelAdmin(admin.ModelAdmin):
	list_display = ['created_by', 'title','updated', 'timestamp_save', 'times_used']
	class Meta:
		model = Description


admin.site.register(Description, DescriptionModelAdmin)


class HashtagModelAdmin(admin.ModelAdmin):
	list_display = ['created_by', 'title','updated', 'timestamp_save', 'times_used']
	class Meta:
		model = Hashtag


admin.site.register(Hashtag, HashtagModelAdmin)

class Source_contentModelAdmin(admin.ModelAdmin):
	list_display = ['request', 'request_name', 'created_by','dataset_id','api_key','status','quantity_contents','updated', 'timestamp']
	class Meta:
		model = Source_content

admin.site.register(Source_content, Source_contentModelAdmin)


		 