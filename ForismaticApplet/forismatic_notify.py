#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Sample applet for gnome

#TODO: output to syslog or messages log
#TODO: add threading

import pygtk
import sys
import gtk
import gnome.ui
import gnomeapplet
import os.path
import datetime
import gobject
import Preference
from Forismatic import Forismatic
import os
import webbrowser

#import sys
#out = open('/home/vanuch/log.txt', 'w+')
#outerr = open('/home/vanuch/logerr.txt', 'w+')
#sys.stdout = out
#sys.stderr = outerr
#print "test"


#path = os.getcwd()
#print "folder path: %s"%path
#if  path =="/":
	#path = '/home/vanuch/Documents/python/ForismaticApplet/'
path = '/usr/share/ForismaticApplet'

__version__ = "0.7b"
__license__ = "GNU General Public License v.3"
__author__ = "Vanuch <goncharov.ivan.v@gamil.com>"


class GnomeAppletSkeleton(gnomeapplet.Applet):
	"""Simple applet skeleton
		author Pythy <the.pythy@gmail.com>
	"""

	def __init__(self, applet, iid):
		"""Create applet for proxy"""
		self.applet = applet
		self.__init_core_widgets()
		self.init_additional_widgets()
		self.init_ppmenu()
		self.__connect_events()
		self.applet.connect("destroy", self._cleanup)
		self.after_init()
		self.applet.show_all()

	def __init_core_widgets(self):
		"""Create internal widgets"""
		# making internal widgets
		self.tooltip = gtk.Tooltip() #self.tooltips = gtk.Tooltips()
		self.hbox = gtk.HBox()
		self.ev_box = gtk.EventBox()
		# making widgets' ierarchy
		self.applet.add(self.hbox)
		self.hbox.add(self.ev_box)

	def init_additional_widgets(self):
		"""Create additional widgets"""
		self.image=gtk.Image()
		self.cur_dir=os.path.abspath(path)
		self.cur_dir=os.path.join(self.cur_dir,'Theme/Blue')
		self.icon_path=\
		os.path.join(self.cur_dir,'forismatic_icon_16.png')
		self.image.set_from_file(self.icon_path)
		self.ev_box.add(self.image)

	def init_ppmenu(self):
		"""Create popup menu for properties"""
		self.ppmenu_xml = """
		<popup name="button3">
		<menuitem name="About Item" verb="About" stockid="gtk-about"/>
		</popup>		
		"""
		self.ppmenu_verbs = [("About", self.on_ppm_about),
			]

	def __connect_events(self):
		"""Connect applet's events to callbacks"""
		
		self.ev_box.set_events(gtk.gdk.BUTTON_PRESS_MASK|gtk.gdk.ENTER_NOTIFY_MASK)
		self.ev_box.connect("button-press-event", self.on_button)
		self.ev_box.connect("enter-notify-event", self.on_enter)
		self.button_actions = {
			1: lambda: None,  
			2: lambda: None,
			3: self._show_ppmenu,
			}

	def after_init(self):
		"""After-init hook"""
		pass

	def _cleanup(self, event):
		"""Cleanup callback (on destroy)"""
		del self.applet

	def on_button(self, widget, event):
		"""Action on pressing button in applet"""
		#print "event %s"%event
		#while gtk.gdk.events_pending():
		#	gtk.main_iteration (block=0)
		#	event1=gtk.gdk.event_get()
		#	print event1
		#if event1 != None:
						
		if event.type == gtk.gdk.BUTTON_PRESS:
			#print "1click"
			self.button_actions[event.button]()
			
			

	def _show_ppmenu(self):
		"""Show popup menu"""
		#print self.applet.setup_menu.__doc__
		self.applet.setup_menu(self.ppmenu_xml,
							   self.ppmenu_verbs,
							   None)

	def on_enter(self, widget,event):
		"""Action on entering mouse to widget"""
		self.info = "PopUp info" 
		self.ev_box.set_tooltip_text(str(self.info)) 
		

	def on_ppm_about(self, event, data=None):
		"""Action on chose 'about' in pop-up menu"""
		gnome.ui.About("GnomeApplet skeleton", "0.1", 
					   "GNU General Public License v.2",
					   "Simple skeleton for Python powered GNOME applet",
					   ["Pythy <the.pythy@gmail.com>",],
					   ).show()



class GnomeForismaticApplet(GnomeAppletSkeleton):
	def __init__(self, applet, iid):
		"""Create applet for Forismatic Notify"""
		self.applet=applet
		self.iid=iid
		self.conf = Preference.Config(applet,self.cb_TimePeriod,self.cb_Theme,self.cb_Lang)
		(self.TimePeriod, self.Theme,self.Language) =\
			self.conf.get_settings()
		self.theme_path = os.path.join(path,'Themes',self.Theme)
		self.time = self.TimePeriod*60
		if self.time==0:
			self.time = 300
		GnomeAppletSkeleton.__init__(self, applet, iid)
	
	def init_additional_widgets(self):
		"""Create additional widgets"""
		self.icon_path=\
		os.path.join(self.theme_path,'forismatic_icon_16.png')
		self.pixbuff = gtk.gdk.pixbuf_new_from_file(self.icon_path)
		self.image=gtk.Image()
		#print "thme path from init_add_widgets func: %s"%self.theme_path
		self.image.set_from_pixbuf(self.pixbuff)
		self.ev_box.add(self.image)
	
	def after_init(self):
		"""Connect Forismatic class
			and map action to mouse keys"""
		self.forism=Forismatic(self.conf,path)
		self.button_actions[1]=self.show_quote
		self.button_actions[2]=self.show_quote_on_site
		self.timer()
	
	def on_enter(self, widget,event):
		"""show info when enter cursor on applet icon"""
		try:
			self.delta_time=datetime.datetime.today()-self.start_timer
			self.left_time=self.time-self.delta_time.seconds
			
			self.delta_time_norm=\
			datetime.timedelta(seconds=self.delta_time.seconds)
			
			self.left_time_norm=\
			datetime.timedelta(seconds=self.left_time)
			self.info="Last quote was %s ago\n Next quote after %s" %\
			(self.delta_time_norm,self.left_time_norm)
			#print "on enter notif: %s"%self.info
		except :
			self.info = "Forismatic" 
		self.ev_box.set_tooltip_text(str(self.info)) 
	
	def next_quote(self):
		"""Show next quote"""
		#change icon to refresh-icon:
		self.refresh_path=\
		os.path.join(self.theme_path,'icon_refresh_15.png')
		self.pixbuff = gtk.gdk.pixbuf_new_from_file(self.refresh_path)
		self.image.set_from_pixbuf(self.pixbuff)
		#get new quote
		self.forism.save_quote() #remember last quote for next redirect to site
		#return old quote:
		self.pixbuff = gtk.gdk.pixbuf_new_from_file(self.icon_path)
		self.image.set_from_pixbuf(self.pixbuff)
		#show quote:
		self.quote = self.forism.get_quote()
		self.forism.show_notify(self.quote)
					
	def timer_handler(self):
		"""Timer handler"""
		self.next_quote()
		self.start_timer=datetime.datetime.today()
		return True
		
	def timer(self):
		"""Timer. Show newt quote after time period"""
		self.TimePeriod = self.conf.get_settings()[0]
		self.time=self.TimePeriod*60
		self.source_event=\
		gobject.timeout_add_seconds(self.time, self.timer_handler)
		#print self.source_event
		self.start_timer=datetime.datetime.today()
				
	def show_quote(self):
		"""Action: show quote not waiting timer handler"""
		gobject.source_remove(self.source_event)
		self.next_quote()
		#thread.start_new_thread(self.forism.save_qote,()) dont work. why????
		self.timer()

	def on_ppm_about(self, event, data=None):
		"""Callback for pop-up menu item 'About', show About dialog"""
		self.icon_path=\
		os.path.join(self.theme_path,'forismatic_icon_100.png')
		self.pixbuf=gtk.gdk.pixbuf_new_from_file(self.icon_path)
		msg_applet_name = u"Forismatic Notify"
		msg_applet_description = \
		u"""Forismatic applet for Python powered GNOME applet"""
		msg_applet_documentation=\
		[u"left mouse key   - show next quote",
		 u"middle mouse key - show last quote on the site",
		 u"right mouse key  - show menu"]
		gnome.ui.About(msg_applet_name, __version__, __license__,
					   msg_applet_description,
					   [__author__,],   # programming
						msg_applet_documentation,   # documentation
						None,   # translating
						self.pixbuf,
					   ).show()
	
	def init_ppmenu(self):
		"""Create popup menu for properties"""
		self.ppmenu_xml = """
		<popup name="button3">
			<menuitem name="ItemPreferences" 
				verb="Preferences" 
				label="_Preferences" 
				pixtype="stock" 
				pixname="gtk-preferences"/>
			<menuitem name="ItemShowQuote" 
				verb="ShowQuote" 
				label="_ShowQuote" 
				pixtype="stock" 
				pixname="gtk-web"/>
			<separator/>
			<menuitem name="About Item" 
				verb="About"
				label=" About"
				pixtype="stock" 
				stockid="gtk-about"/>
		</popup> """
		self.ppmenu_verbs = [("About", self.on_ppm_about),
							 ('Preferences', self.show_preferences),
							 ('ShowQuote', self.show_quote_on_site)
							]
	
	def show_preferences(self,*arguments):
		"""Show Preference windows"""	
		self.pref = Preference.Preference(self.applet, path)

	def show_quote_on_site(self, *arguments):
		"""Open last quote in browser"""
		self.QuoteLink = self.conf.get_Quote()[2]
		webbrowser.open(self.QuoteLink,2, False)
			
	def cb_TimePeriod(self,client, cnxn_id, entry, params):
		"""CallBack function, which runing after changed Time Period"""
		gobject.source_remove(self.source_event)
		self.timer()
		self.TimePeriod = self.conf.get_settings()[0]
		#TODO: add analise left time befo calc time for show next quote
	
	def cb_Theme(self,client, cnxn_id, entry, params):
		"CallBack fuction, run when changing Theme"
		self.Theme = self.conf.get_settings()[1]
		self.theme_path = os.path.join(path,'Themes',self.Theme)
		self.icon_path=\
		os.path.join(self.theme_path,'forismatic_icon_16.png')
		self.pixbuff = gtk.gdk.pixbuf_new_from_file(self.icon_path)
		self.image.set_from_pixbuf(self.pixbuff)
				
	def cb_Lang(self,client, cnxn_id, entry, params):
		"CallBack fuction, run when changing language"
		#change icon to refresh-icon
		self.refresh_path=\
		os.path.join(self.theme_path,'icon_refresh_15.png')
		self.pixbuff = gtk.gdk.pixbuf_new_from_file(self.refresh_path)
		self.image.set_from_pixbuf(self.pixbuff)
		self.forism.save_quote()# need disable waiting finish of function
		#TODO: return old quote
		self.pixbuff = gtk.gdk.pixbuf_new_from_file(self.icon_path)
		self.image.set_from_pixbuf(self.pixbuff)

def applet_factory(applet, iid):
	GnomeForismaticApplet(applet, iid)
	return True
	

def run_in_panel():
	gnomeapplet.bonobo_factory("OAFIID:GNOME_ForismaticNotify_Factory",
							   GnomeForismaticApplet.__gtype__,
							   "Applet Forismatic Notify",
							   "0",
							   applet_factory)
							   

def run_in_window():
	main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
	main_window.set_title("GNOME Applet Forismatic")
	main_window.connect("destroy", gtk.main_quit)
	app = gnomeapplet.Applet()
	applet_factory(app, None)
	app.reparent(main_window)
	main_window.show_all()
	gtk.main()
	sys.exit()
	

def main(args):
	if len(args) == 2 and args[1] == "run-in-window":
		run_in_window()
	else:
		run_in_panel()
		

if __name__ == '__main__':
	main(sys.argv)
