## Totem D-Bus plugin
## Copyright (C) 2009 Azala <azalathemad@yahoo.com>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin St, Fifth Floor,
## Boston, MA 02110-1301  USA.
##
## Sunday 13th May 2007: Bastien Nocera: Add exception clause.
## See license_change file for details.

import totem
import gobject, gtk
import dbus, dbus.service
from dbus.mainloop.glib import DBusGMainLoop

class dbusservice(totem.Plugin):
	def __init__(self):
		totem.Plugin.__init__(self)

	def activate(self, totem):
		DBusGMainLoop(set_as_default=True)
		self.notification = Notification("/org/gnome/Totem", totem)
		self.title = ""
		self.artist = ""
		self.album = ""
		self.duration = 0 # may be usable in future
		totem.connect("file-opened", self.do_file_opened)
		totem.connect("file-closed", self.do_file_closed)
		totem.connect("metadata-updated", self.do_update_metadata)
		totem.connect("notify::playing", self.do_notify)

	def deactivate(self, totem):
		self.notification.playingStopped()
		self.notification.disconnect() # ensure we don't leak our path on the bus

	def do_file_opened(self, totem, mrl):
		self.notification.fileOpened(mrl)

	def do_file_closed(self, totem):
		self.notification.fileClosed()	
		
	def do_update_metadata(self, totem, title, artist, album, num):
		self.title = title
		self.artist = artist
		self.album = album
		if not self.title:
			self.title = ""
		if not self.artist:
			self.artist = ""
		if not self.album:
			self.album = ""
		
	def do_notify(self, totem, status):
		if totem.is_playing():
			self.current_mrl = totem.get_current_mrl()
			self.notification.playingStarted(self.current_mrl, self.title, self.album, self.artist, self.duration)
		else:
			self.notification.playingStopped()

class Notification(dbus.service.Object):
	def __init__(self, path, totem):
		dbus.service.Object.__init__(self, dbus.SessionBus(), path)
		self.totem = totem

	def disconnect(self):
		self.remove_from_connection(None, None)

	@dbus.service.signal(dbus_interface="org.gnome.Totem", signature="ssssu")
	def playingStarted(self, current_mrl, title, album, artist, duration):
		pass

	@dbus.service.signal(dbus_interface="org.gnome.Totem", signature="")
	def playingStopped(self):
                pass

	@dbus.service.signal(dbus_interface="org.gnome.Totem", signature="s")
	def fileOpened(self, mrl):
		pass

	@dbus.service.signal(dbus_interface="org.gnome.Totem", signature="")
	def fileClosed(self):
		pass

	@dbus.service.method("org.gnome.Totem", in_signature='', out_signature='')
	def playCurrent(self):
		self.totem.action_play()
