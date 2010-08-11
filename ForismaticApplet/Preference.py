#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk
import gtk
import gconf
import os

#debug
#import sys
#out = open('/home/vanuch/log_pref.txt', 'w+')
#sys.stdout = out
#sys.stderr = out

DefaultTimePeriod = 30
DefaultTheme='Blue'
DefaultQuoteText = u"Лишь те, кто отваживаются потерпеть большую неудачу, могут прийти к большим достижениям."
DefaultQuoteLink = "http://ru.forismatic.com/e91bb392d1/"
DefaultQuoteAuthor = "       --Роберт Кеннеди"
DefaultLanguage = 'Russian'
theme_id = {"Blue" : "0","Black" : "1"}
lang_id = {"Russian" : "1","English" : "0"} 


class Preference(object):
	"""Show preference menu, and allow make changes to config"""       
	def __init__(self, applet = None,path = "./"):
		"""Drow Preference windows and current preferences"""
		self.applet = applet
		builder = gtk.Builder()
		self.glade = os.path.join(path,"preference.glade")
		builder.add_from_file(self.glade)
		builder.connect_signals(
				{ "on_preference_close" : self.destroy,
				"on_Exit_clicked" : self.destroy, 
				"on_Ok_clicked" : self.save_config}
				)
		self.window = builder.get_object("preference")
		self.ThemeSelect = builder.get_object("ThemeSelect")
		self.RefreshSpinButton = builder.get_object("RefreshSpinButton")
		self.ThemeList = builder.get_object("ThemeList")
		self.Adj = gtk.SpinButton.get_adjustment(self.RefreshSpinButton)
		self.LangSelect = builder.get_object("LangSelect")
		self.LangList = builder.get_object("LangList")
		#read config file
		if self.applet == None:
			self.conf=Config(None)
		else:
			self.conf=Config(self.applet)
		(self.TimePeriod, self.Theme,self.Language) = self.conf.get_settings()
		self.Adj.set_value(self.TimePeriod)
		IterTheme = self.ThemeList.get_iter_from_string(theme_id[self.Theme])
		self.ThemeSelect.set_active_iter(IterTheme)
		IterLang = self.LangList.get_iter_from_string(lang_id[self.Language])
		self.LangSelect.set_active_iter(IterLang)
		#show preference windows
		self.window.show()
		
	def get_config(self):
		"""Read current config"""
		self.conf.get_settings()

	def save_config(self,*arg):
		"""Saved new config"""
		#print arg
		#print  gtk.ComboBox.get_active(self.LangSelect), gtk.ComboBox.get_active_text(self.LangSelect)
		#print gtk.Adjustment.get_value(gtk.SpinButton.get_adjustment(self.RefreshSpinButton))
		#save config
		self.NewTheme = gtk.ComboBox.get_active_text(self.ThemeSelect)
		self.NewTimePeriod = int(gtk.Adjustment.get_value
			(gtk.SpinButton.get_adjustment(self.RefreshSpinButton)))
		self.NewLanguage = gtk.ComboBox.get_active_text(self.LangSelect)
		self.conf.set_settings(self.NewTimePeriod,
			self.NewTheme,self.NewLanguage)
	
	def destroy(self, *arg):
		"""Closed windows"""
		#print arg
		self.window.destroy()


class Config():
	"""Save all config in GConf"""
	def __init__(self,applet= None, cb_TimePeriod = None, cb_Theme = None, cb_Lang = None):
		"""Init variables"""
		self.applet = applet
		self.client = gconf.client_get_default()
		#self.prefs_key = self.client.get_preferences_key("/app/panel/applets/forismatic") #for applet
		if self.applet == None:
			self.client.add_dir(
			"/apps/panel/applets/forismatic",gconf.CLIENT_PRELOAD_NONE) #delete for applet
			self.prefs_key="/apps/panel/applets/forismatic"            #delete for applet
		else:
			self.prefs_key = self.applet.get_preferences_key()
		#print "pref: %s" %(self.prefs_key)
		if self.prefs_key == None:
			self.client.add_dir(
			"/apps/panel/applets/forismatic",gconf.CLIENT_PRELOAD_NONE)
			self.prefs_key="/apps/panel/applets/forismatic"
		#self.set_settings(15,'Black')
		self.get_settings()
		self.notify_cb(cb_TimePeriod,cb_Theme,cb_Lang)
		
	def get_settings(self):
		"""Return all settings"""
		self.Theme = self.client.get_string(self.prefs_key+"/Theme")
		if self.Theme == None:
			self.client.set_string(self.prefs_key+"/Theme",DefaultTheme)
			self.Theme = DefaultTheme
		self.TimePeriod = self.client.get_int(self.prefs_key+"/TimePeriod")
		#print self.TimePeriod
		if self.TimePeriod == None or self.TimePeriod == 0:
			self.client.set_int(self.prefs_key+"/TimePeriod", DefaultTimePeriod)
			self.TimePeriod = DefaultTimePeriod
		#print self.TimePeriod
		self.Language = self.client.get_string(self.prefs_key+"/Language")
		if self.Language == None:
			self.client.set_string(self.prefs_key+"/Language",DefaultLanguage)
			self.Language = DefaultLanguage
		return self.TimePeriod, self.Theme,self.Language
	
	def set_settings(self,TimePeriod,Theme,Language):
		"""Saved settings"""
		self.client.set_int(self.prefs_key+"/TimePeriod",TimePeriod)
		self.client.set_string(self.prefs_key+"/Theme",Theme)
		self.client.set_string(self.prefs_key+"/Language",Language)
	
	def set_Quote(self,QuoteText,QuoteAuthor, QuoteLink):
		"""Saved new quote"""
		self.client.set_string(self.prefs_key+"/QuoteText",QuoteText)
		self.client.set_string(self.prefs_key+"/QuoteLink",QuoteLink)
		self.client.set_string(self.prefs_key+"/QuoteAuthor",QuoteAuthor)
	
	def get_Quote(self):
		"""Return saved quote"""
		self.QouteText = self.client.get_string(self.prefs_key+"/QuoteText")
		if self.QouteText == None:
			self.client.set_string(self.prefs_key+"/QuoteText",DefaultQuoteText)
			self.QouteText = DefaultQuoteText
		#link
		self.QuoteLink = self.client.get_string(self.prefs_key+"/QuoteLink")
		if self.QuoteLink == None:
			self.client.set_string(self.prefs_key+"/QuoteLink", DefaultQuoteLink)
			self.QuoteLink = DefaultQuoteLink
		#author
		self.QuoteAuthor = self.client.get_string(self.prefs_key+"/QuoteAuthor")
		if self.QuoteAuthor == None:
			self.client.set_string(self.prefs_key+"/QuoteLink", DefaultQuoteAuthor)
			self.QuoteAuthor = DefaultQuoteAuthor
		return self.QouteText,self.QuoteAuthor, self.QuoteLink
	
	def notify_cb(self,cb_TimePeriod,cb_Theme, cb_Lang):
		"""Callback for config changed"""
		if cb_TimePeriod == None:
			cb_TimePeriod = lambda client, cnxn_id, entry, params: None
		if cb_Theme == None:
			cb_Theme = lambda client, cnxn_id, entry, params: None
		if cb_Lang == None:
			cb_Lang = lambda client, cnxn_id, entry, params: None
		self.client.notify_add(self.prefs_key+"/TimePeriod",cb_TimePeriod)
		self.client.notify_add(self.prefs_key+"/Theme",cb_Theme)
		self.client.notify_add(self.prefs_key+"/Language",cb_Lang)
			
		
if __name__ == "__main__":
	app = Preference()
	gtk.main()

