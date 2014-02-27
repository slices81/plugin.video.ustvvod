#!/usr/bin/python
# -*- coding: utf-8 -*-
import _addoncompat
import _common
import _connection
import re
import simplejson
import sys
import urllib
import xbmc
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup, SoupStrainer

pluginHandle = int(sys.argv[1])

SITE = 'msnbc'
SHOWS = 'http://www.msnbc.com/api/1.0/shows.json'
BASE = 'http://www.msnbc.com/'
PLAYLIST = 'http://data.nbcnews.com/VideoRendering/PlaylistTemplate/%s'
FEED = 'http://feed.theplatform.com/f/2E2eJC/%s?form=json'

def masterlist():
	master_db = []
	master_data = _connection.getURL(SHOWS)
	master_menu = simplejson.loads(master_data)['shows']
	for master_item in master_menu:
		master_name = master_item['show']['title']
		season_url = season_url = BASE + master_item['show']['path']
		master_db.append((master_name, SITE, 'seasons', season_url))
	return master_db

def rootlist():
	root_data = _connection.getURL(SHOWS)
	root_menu = simplejson.loads(root_data)['shows']
	for root_item in root_menu:
		root_name = root_item['show']['title']
		season_url = BASE + root_item['show']['path']
		_common.add_show(root_name,  SITE, 'seasons', season_url)
	_common.set_view('tvshows')

def seasons(season_url = _common.args.url):
	season_data = _connection.getURL(season_url)
	season_tree = BeautifulSoup(season_data, 'html.parser', parse_only = SoupStrainer('div'))
	season_source = season_tree.find('div', id = 'TPVideoPlaylistTaxonomyContainer')['source']
	playlist_url = PLAYLIST % season_source
	playlist_data = _connection.getURL(playlist_url)
	playlist_data = playlist_data.replace('$pdk.NBCplayer.ShowPlayerTaxonomy.GetList(', '').replace(');', '')
	season_menu = simplejson.loads(playlist_data)
	for season_item in season_menu['playlistTaxonomy']:
		_common.add_directory(season_item['reference']['name'],  SITE, 'episodes', FEED % season_item['reference']['feed'])
	_common.set_view('seasons')

def episodes(episode_url = _common.args.url):
	episode_data = _connection.getURL(episode_url)
	episode_menu = simplejson.loads(episode_data)['entries']
	for i, episode_item in enumerate(episode_menu):
		default_mediacontent = None
		for mediacontent in episode_item['media$content']:
			if (mediacontent['plfile$isDefault'] == True) and (mediacontent['plfile$format'] == 'MPEG4'):
				default_mediacontent = mediacontent
			elif (mediacontent['plfile$format'] == 'MPEG4'):
				mpeg4_mediacontent = mediacontent
		if default_mediacontent is None:
			default_mediacontent = mpeg4_mediacontent
		url = default_mediacontent['plfile$url']
		episode_duration = int(default_mediacontent['plfile$duration'])
		episode_plot = episode_item['description']
		episode_airdate = _common.format_date(epoch = episode_item['pubDate']/1000)
		episode_name = episode_item['title']
		try:
			season_number = int(episode_item['pl' + str(i + 1) + '$season'][0])
		except:
			season_number = -1
		try:
			episode_number = int(episode_item['pl' + str(i + 1) + '$episode'][0])
		except:
			episode_number = -1
		try:
			episode_thumb = episode_item['plmedia$defaultThumbnailUrl']
		except:
			episode_thumb = None
		u = sys.argv[0]
		u += '?url="' + urllib.quote_plus(url) + '"'
		u += '&mode="' + SITE + '"'
		u += '&sitemode="play_video"'
		infoLabels={	'title' : episode_name,
						'durationinseconds' : episode_duration,
						'season' : season_number,
						'episode' : episode_number,
						'plot' : episode_plot,
						'premiered' : episode_airdate }
		_common.add_video(u, episode_name, episode_thumb, infoLabels = infoLabels)
	_common.set_view('episodes')

def play_video(video_url = _common.args.url):
	hbitrate = -1
	sbitrate = int(_addoncompat.get_setting('quality')) * 1024
	closedcaption = None
	video_data = _connection.getURL(video_url)
	video_tree = BeautifulSoup(video_data, 'html.parser')
	finalurl = video_tree.seq.video['src']
	try:
		closedcaption = video_tree.find('textstream', type = 'text/vtt')['src']
	except:
		pass
	if (_addoncompat.get_setting('enablesubtitles') == 'true') and (closedcaption is not None):
			convert_subtitles(closedcaption)
	xbmcplugin.setResolvedUrl(pluginHandle, True, xbmcgui.ListItem(path = finalurl))
	if (_addoncompat.get_setting('enablesubtitles') == 'true') and (closedcaption is not None):
		while not xbmc.Player().isPlaying():
			xbmc.sleep(100)
		xbmc.Player().setSubtitles(_common.SUBTITLE)

def clean_subs(data):
	br = re.compile(r'<br.*?>')
	tag = re.compile(r'<.*?>')
	apos = re.compile(r'&amp;apos;')
	gt = re.compile(r'&gt;')
	sub = br.sub('\n', data)
	sub = tag.sub(' ', sub)
	sub = apos.sub('\'', sub)
	sub = gt.sub('>', sub)
	return sub

def convert_subtitles(closedcaption):
	str_output = ''
	subtitle_data = _connection.getURL(closedcaption, connectiontype = 0)
	str_output = clean_subs(subtitle_data)
	file = open(_common.SUBTITLE, 'w')
	file.write(str_output)
	file.close()
