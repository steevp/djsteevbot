#!/usr/bin/env python
# Copyright 2013 Steven Pledger <steev@yourewinner.com>
"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from ttapi import Bot
from re import match

AUTH = 'XXXXXXXXXXXXXXXXXXXXXXXX'
USERID = 'XXXXXXXXXXXXXXXXXXXXXXXX'
ROOMID = 'XXXXXXXXXXXXXXXXXXXXXXXX'

bot = Bot(AUTH, USERID, ROOMID)
djs = {}

# Callbacks
def onSpeak(data):
	name = data['name']
	text = data['text']
	
	if text == '/join':
		bot.addDj()
	elif text == '/leave':
		bot.remDj()
	elif text == '/rejoin':
		bot.remDj()
		bot.addDj()
	elif text == '/skip':
		bot.skip()
	elif text == '/snag':
		bot.roomInfo(snag)
	elif text == '/yw':
		bot.speak("@" + name + " YOU'RE WINNER !")
	elif 'should i play' in text.lower():
		bot.speak('@' + name + ' play BACK THAT AZZ UP!')
	elif text == '/bop':
		bot.speak('FUCK YEAH I LOVE THIS SONG!!! <3')
		bot.bop()
	elif text == '/turd':
		bot.speak('BOO THIS SHIT SUCKS!!! :thumbsdown:')
		bot.vote('down')
	elif match('^/setlaptop [a-z]+$', text):
		laptop = text.split()[1]
		bot.modifyLaptop(laptop)
	elif match('^/setavatar [0-9]+$', text):
		avatar = int(text.split()[1])
		bot.setAvatar(avatar)
	elif match('^/kick .+$', text):
		if name == 'djsteev':
			name = text.split()[1]
			bot.roomInfo(lambda data: kick(data, name))
		else:
			bot.speak('Only steev can do that. Asshole')
	elif match('^/kickme [0-9]+$', text):
		dj = data['userid']
		num = int(text.split()[1])
		if dj in djs:
			djs[dj]['song_number'] = 0 # reset plays
			djs[dj]['song_limit'] = num
			bot.speak('@' + name + ' I will remove you after ' + str(num) + ' plays.')
	elif text in ('/help', '/commands'):
		bot.speak('DJSteevBot commands: /join, /leave, /rejoin, /skip, /yw, /snag, /bop, /turd, /setlaptop type, /setavatar id, /kickme num, /kick user')

def onEndSong(data):
	song = data['room']['metadata']['current_song']['metadata']['song']
	upvotes = data['room']['metadata']['upvotes']
	downvotes = data['room']['metadata']['downvotes']
	bot.speak(':musical_note: ' + song + ' :thumbsup: ' + str(upvotes) + ' :thumbsdown: ' + str(downvotes))
	
	dj = data['room']['metadata']['current_dj']
	djs[dj]['song_number'] += 1
	if djs[dj]['song_limit'] > 0 and djs[dj]['song_number'] >= djs[dj]['song_limit']:
		bot.remDj(dj)
		del djs[dj]

def onRoomChanged(data):
	currentDjs = data['room']['metadata']['djs']
	for dj in currentDjs:
		djs[dj] = { 'song_number': 0, 'song_limit': 0 }

def onAddDj(data):
	dj = data['user'][0]['userid']
	djs[dj] = { 'song_number': 0, 'song_limit': 0 }

def onRemDj(data):
	dj = data['user'][0]['userid']
	del djs[dj]

def snag(data):
	songid = data['room']['metadata']['current_song']['_id']		
	song = data['room']['metadata']['current_song']['metadata']['song']
	# Add song to the end of the playlist
	bot.playlistAll(lambda playlist: bot.playlistAdd(songid, len(playlist['list'])))
	# show the heart animation
	bot.snag()	
	bot.speak('Added ' + song + ' to the playlist')

def kick(data, name):
	for user in data['users']:
		if user['name'] == name:
			bot.bootUser(user['userid'])
			break

bot.on('speak', onSpeak)
bot.on('endsong', onEndSong)
bot.on('roomChanged', onRoomChanged)
bot.on('add_dj', onAddDj)
bot.on('rem_dj', onRemDj)

bot.start()
