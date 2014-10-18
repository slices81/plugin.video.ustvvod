#!/usr/bin/python
# -*- coding: utf-8 -*-
import _common
import _main_viacom

SITE = 'mtv'
NAME = 'MTV'
DESCRIPTION = "MTV is Music Television. It is the music authority where young adults turn to find out what's happening and what's next in music and popular culture. MTV reaches 412 million households worldwide, and is the #1 Media Brand in the world. Only MTV can offer the consistently fresh, honest, groundbreaking, fun and inclusive youth-oriented programming found nowhere else in the world. MTV is a network that transcends all the clutter, reaching out beyond barriers to everyone who's got eyes, ears and a television set."
API = 'http://api.mtv.com/api/vLaNWq0xlbQB/'
SHOWS = API + 'promolist/10393491.json'

def masterlist():
	return _main_viacom.masterlist(SITE, SHOWS)

def seasons():
	_main_viacom.seasons(SITE, API)

def videos():
	_main_viacom.videos(SITE)

def play():
	_main_viacom.play_video2(API, _common.args.url)

def list_qualities():
	return _main_viacom.list_qualities2(API, _common.args.url)
