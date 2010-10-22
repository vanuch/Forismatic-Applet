#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import os.path
import pynotify
import urllib
import xml.dom.minidom
#import httplib

class Forismatic:
	"""Return random quote form www.forismatic.com"""
	def __init__(self, conf,path = None):
		"""init some variables"""
		self.conf = conf
		if path == None:
			self.path = '/usr/share/ForismaticApplet'
		else:
			self.path = path
		
		
	def get_quote(self):
		"""Read last quote from gconf (or file)"""
		#saved_quote_path=os.path.join(cur_dir, 'forismatic') # if quote write to file
		#print logo_path
		#0) read file with saved quote
		"""with codecs.open(saved_quote_path,
						encoding='utf-8',mode='r') as file_r:
			quote = file_r.readlines()
		file_r.closed
		quote=u"".join(quote)
		"""
		#read from GConf
		(self.QuoteText,self.quoteAuthor,self.QuoteLink)=self.conf.get_Quote()
		#print "%s  \n   %s :: %s"%(self.QuoteText,self.quoteAuthor,self.QuoteLink)
		if self.quoteAuthor == "":
			quote=self.QuoteText
		else:
			quote=self.QuoteText+"\n"+self.quoteAuthor
		#print quote
		return quote
		
	def show_notify(self,body):
		"""show quote using Notification"""
		(self.TimePeriod,self.Theme, self.Lang) = self.conf.get_settings()
		cur_dir=os.path.abspath(self.path)
		self.theme_path = os.path.join(self.path,'Themes',self.Theme)
		logo_path=os.path.join(self.theme_path,'forismatic_logo48x48.png')
		#print logo_path
		title='Forismatic'
		icon='file://'+logo_path
		notif = pynotify.Notification (title, body, icon);
		notif.show ()
		
	def save_quote(self):
		"""Saved new quote to gconf"""
		#1)get quote form forismatic
		#exampl of quote:
		"""
		<forismatic>
			<quote>
				<quoteText>
					Для любви не существует вчера, любовь не думает \
					о завтра. 
					Она жадно тянется к нынешнему дню, но этот день \
					нужен ей весь, неограниченный, не омраченный. 
				</quoteText>
				<quoteAuthor>
					Генрих Гейне 
				</quoteAuthor>
				<senderName>
				</senderName>
				<senderLink>
					http://ru.forismatic.com/8d9098bc35/
				</senderLink>
				<quoteLink>
					http://ru.forismatic.com/13d15ebb9a/
				</quoteLink>
			</quote>
		</forismatic>
		"""
		#TODO: add check of bad response
		self.lang = u"".join(self.quote_lang())
		params = urllib.urlencode({ 'format': 'xml','key': '',
			'lang': self.lang,'method': 'getQuote' })
		#new version
		"""
			headers = {"Content-type": "application/x-www-form-urlencoded",
				"Accept": "*/*"}
			conn = httplib.HTTPConnection('api.forismatic.com')
			conn.request("POST", "/api/1.0/", params, headers)
			response = conn.getresponse()
			print response.status, response.reason
			quote_xml = response.read()
			conn.close()
		"""
		#old version:
		f =urllib.urlopen("http://api.forismatic.com/api/1.0/",params)
		quote_xml = f.read()

		#2)parseQuote:
		quoteText = "can not get quote"
		quoteAuthor = ""
		quoteLink = "error"
		
		quote=xml.dom.minidom.parseString(quote_xml)
		#text
		text = quote.getElementsByTagName('quoteText')
		for node in text[0].childNodes:
			if node.nodeType == node.TEXT_NODE:
				quoteText=node.data
		#author		
		text = quote.getElementsByTagName('quoteAuthor')
		for node in text[0].childNodes:
			if node.nodeType == node.TEXT_NODE:
				quoteAuthor =node.data
				quoteAuthor = "--"+ quoteAuthor
				quoteAuthor = quoteAuthor.rjust(30," ")
		#link							
		text = quote.getElementsByTagName('quoteLink')
		for node in text[0].childNodes:
			if node.nodeType == node.TEXT_NODE:
				quoteLink =node.data
		#write to file			
		"""with codecs.open(saved_quote_path, 
						encoding='utf-8',mode='w') as file_w:
			file_w.write(quoteText)
			file_w.write("\n"+quoteAuthor)
		file_w.closed"""
		#write to GConf
		self.conf.set_Quote(quoteText, quoteAuthor, quoteLink)
		#print "%s \n     %s \n  %s "%(quoteText, quoteAuthor, quoteLink)
		#print "end"
	
	def quote_lang(self):
		"""Return current language for quote"""
		self.Language=self.conf.get_settings()[2]
		if self.Language == 'English' or self.Language == 'english' \
			or self.Language == 'en':
			return 'en'
		elif self.Language == 'Russian' or self.Language == 'russian' \
			or self.Language == 'ru':
			return 'ru'
		else: 
			return None

if __name__ == '__main__':
	import Preference
	conf = Preference.Config()
	path = os.getcwd()
	
	quote=Forismatic(conf,path)
	quote.save_qote()
