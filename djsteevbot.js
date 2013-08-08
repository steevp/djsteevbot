/* Copyright 2013 Steven Pledger <steev@yourewinner.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
var Bot    = require('ttapi'), repl = require('repl');
var AUTH   = 'XXXXXXXXXXXXXXXXXXXXXXXX';
var USERID = 'XXXXXXXXXXXXXXXXXXXXXXXX';
var ROOMID = 'XXXXXXXXXXXXXXXXXXXXXXXX';

var bot = new Bot(AUTH, USERID, ROOMID);
var djs = {};

repl.start('> ').context.bot = bot;

bot.on('speak', function (data) {
	// Get the data
	var name = data.name;
	var text = data.text;
	
	if (text.match(/^\/join$/)) {
		bot.addDj();
	} else if (text.match(/^\/leave$/)) {
		bot.remDj();
	} else if (text.match(/^\/skip$/)) {
		bot.skip();
	} else if (text.match(/^\/snag$/)) {
		bot.roomInfo(function(data) {
			var songid = data.room.metadata.current_song._id;
			var song = data.room.metadata.current_song.metadata.song;
			bot.snag();
			bot.playlistAll(function(playlist) {
				// Use the length so that it gets added to the end of the list.
				bot.playlistAdd(songid, playlist.list.length); 
			});
			bot.speak('Added '+song+' to the playlist.');
		});
	} else if (text.match(/^\/yw$/)) {
		bot.speak("You're Winner!");
	} else if (text.match(/should +i +play/i)) {
		bot.speak('@'+name+' play BACK THAT AZZ UP!');
	} else if (text.match(/bop/)) {
		bot.speak('FUCK YEAH I LOVE THIS SONG!!! <3');
		bot.bop();
	} else if (text.match(/turd/)) {
		bot.speak("BOO THIS SHIT SUCKS!!!");
		bot.vote('down');
	} else if (text.match(/^\/kickme [0-9]+$/)) {
		var djId = data.userid;
		var num = parseInt(text.split(" ")[1]);
		if (djs[djId]) {
			djs[djId].nbSong = 0; // reset plays
			djs[djId].songsLimit = num;
			bot.speak('@'+name+' I will remove you after '+num+' plays.');
		}
	} else if (text.match(/^\/setlaptop .+$/)) {
		var type = text.split(" ")[1];
		bot.modifyLaptop(type);
	} else if (text.match(/^\/setavatar [0-9]+$/)) {
		num = parseInt(text.split(" ")[1]);
		bot.setAvatar(num);
	} else if (text.match(/^\/bootuser .+$/)) {
		if (name == "djsteev") {
			var user = text.split(" ")[1];
			bot.roomInfo(function (data) {
				for (var i = 0; i < data.users.length; i++) {
					if (data.users[i].name == user) {
						bot.bootUser(data.users[i].userid);
						break;
					}
				}
			});
		} else {
			bot.speak("Only steev can do that. Asshole");
		}
	}

});

bot.on('endsong', function (data) {
	var room = data.room;
	var song = room.metadata.current_song.metadata.song;
	var upvotes = room.metadata.upvotes;
	var downvotes = room.metadata.downvotes;
	bot.speak(':musical_note: '+song+' :thumbsup: '+upvotes+' :thumbsdown: '+downvotes+'');
	
	var djId = data.room.metadata.current_dj;
	if (djs[djId] && djs[djId].songsLimit > 0 && ++djs[djId].nbSong >= djs[djId].songsLimit) {
		bot.remDj(djId);
		delete djs[djId];
	}
});

bot.on('roomChanged', function (data) {
	var currentDjs = data.room.metadata.djs;
	for (var i = 0; i < currentDjs.length; i++) {
		djs[currentDjs[i]] = { nbSong: 0, songsLimit: 0 };
	}
});

bot.on('add_dj', function (data) {
	djs[data.user[0].userid] = { nbSong: 0, songsLimit: 0 };
});

bot.on('rem_dj', function (data) {
	delete djs[data.user[0].userid];
});
