from django.contrib import admin
from django.urls import path
from .views import (
	dashboard_view,
	settings_view,
	follow_accounts_view, 
	fetch_users,
	post_delete,
	delete_users,
	login_view,
	register_view, 
	logoutUser,
	content_accounts_view,
	descriptions_view,
	hashtags_view,
	content_view,
	delete_descriptions,
	delete_hashtags,
	follow_individual,
	unfollow_individual,
	post_individual,
	fetch_content,
	delete_contents,
	delete_source_contents,
	how_view,
	posting_on,
	follow_on,
	unfollow_on,
	posting_off,
	follow_off,
	unfollow_off,
	)


urlpatterns = [
    path('', login_view, name='login'),
	path('logout', logoutUser, name='logout'),
    path('register', register_view, name='register'),
    path('dashboard', dashboard_view, name='dashboard'),
    path('settings', settings_view, name='settings'),
    path('follow_accounts', follow_accounts_view, name='follow_accounts'),
    path('content_accounts', content_accounts_view, name='content_accounts'),
    path('<int:id>/fetch', fetch_users, name='fetch'),
    path('<int:id>/fetch_content', fetch_content, name='fetch_content'),
    path('follow_individual', follow_individual),
    path('unfollow_individual', unfollow_individual),
    path('<int:id>/delete', post_delete),
    path('<int:id>/delete-source-content', delete_source_contents),
    path('<int:id>/delete-users', delete_users),
    path('content', content_view, name='contents'),
    path('descriptions', descriptions_view, name='descriptions'),
    path('hashtags', hashtags_view, name='hashtags'),
    path('<int:id>/delete-description', delete_descriptions),
    path('<int:id>/delete-hashtag', delete_hashtags),
    path('<int:id>/delete-content', delete_contents),
    path('post', post_individual),
    path('howitworks', how_view, name='how'),
    path('posting_on', posting_on),
    path('follow_on', follow_on),
    path('unfollow_on', unfollow_on),
    path('posting_off', posting_off),
    path('follow_off', follow_off),
    path('unfollow_off', unfollow_off)



]




app_name = 'channel'