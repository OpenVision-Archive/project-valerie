# -*- coding: utf-8 -*-

from Components.ActionMap import ActionMap, HelpableActionMap
from Components.MenuList import MenuList
from Components.Sources.List import List
from Screens.ChoiceBox import ChoiceBox
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen

from DataElement import DataElement

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import getPlugins, Plugin

#------------------------------------------------------------------------------------------

import gettext
import os
from Components.Language import language
from Tools.Directories import resolveFilename, fileExists, pathExists, createDir, SCOPE_MEDIA, SCOPE_SKIN_IMAGE, SCOPE_PLUGINS, SCOPE_LANGUAGE

def localeInit():
	lang = language.getLanguage()
	os.environ["LANGUAGE"] = lang[:2]
	gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
	gettext.textdomain("enigma2")
	gettext.bindtextdomain("ProjectValerie", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/ProjectValerie/locale/"))

def _(txt):
	if len(txt) == 0:
		return ""
	t = gettext.dgettext("ProjectValerie", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

#------------------------------------------------------------------------------------------

def getViews():
	return (
			(_("List"), "DMC_ListView", "PVMC_ListView"), 
			(_("Poster-Flow"), "DMC_PosterView", "PVMC_PosterView"), 
		)

def getViewClass():
	return DMC_View

class DMC_View(Screen, HelpableScreen):

	skin = """
	<screen name="DMC_View" position="0,0" size="1280,720" title=" " flags="wfNoBorder" backgroundColor="#ff000000">
<widget name="API" text="1" position="0,0" zPosition="0" size="1,1"/>
<widget name="listview_itemsperpage" text="12" position="0,0" zPosition="0" size="1,1" />
<widget source="listview" render="Listbox" zPosition="3" position="106,181" size="391,390" scrollbarMode="showNever" transparent="0" backgroundColor="#10303030" backgroundColorSelected="#0018587A">
<convert type="TemplatedMultiContent">
 {"template": [ MultiContentEntryText(pos = (0,0), size = (373,32), flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER, text = 0) ], "fonts": [gFont("Modern", 20)], "itemHeight": 32, "scrollbarMode": "showNever" } 
</convert>
</widget>
</screen>
	"""

	ON_CLOSED_CAUSE_CHANGE_VIEW = 1

	FAST_STILLPIC = False

	def __init__(self, session, libraryName, loadLibrary, playEntry, viewName, select=None, sort=None, filter=None):
		print "viewName", viewName
		self.skinName = viewName[2]
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		self.skinName = viewName[2]
		self.select = select
		self.onFirstExecSort = sort
		self.onFirstExecFilter = filter
		
		self.libraryName = libraryName
		self.loadLibrary = loadLibrary
		self.viewName = viewName
		self._playEntry = playEntry
		
		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.nav.stopService()
		
		# Initialise API Level for this screen
		self.APILevel = 1 
		try:
			self.APILevel = int(DataElement().getDataPreloading(self, "API"))
		except Exception, ex:
			printl(str(ex))
			self.APILevel = 1
		
		printl("APILevel=" + str(self.APILevel))
		
		if self.APILevel >= 2:
			self["API"] = DataElement()
		
		# Initialise library list
		list = []
		if self.APILevel == 1:
			self["listview"] = MenuList(list)
		elif self.APILevel >= 2:
			self["listview"] = List(list, True)
			self["listview_itemsperpage"] = DataElement()
		
		self["actions"] = HelpableActionMap(self, "DMC_View", 
		{
			"ok":         (self.onKeyOk, ""),
			"cancel":     (self.onKeyCancel, ""),
			"left":       (self.onKeyLeft, ""),
			"right":      (self.onKeyRight, ""),
			"left_quick": (self.onKeyLeftQuick, ""),
			"right_quick": (self.onKeyRightQuick, ""),
			"up":         (self.onKeyUp, ""),
			"down":       (self.onKeyDown, ""),
			"up_quick":   (self.onKeyUpQuick, ""),
			"down_quick": (self.onKeyDownQuick, ""),
			"info":       (self.onKeyInfo, ""),
			"menu":       (self.onKeyMenu, ""),

			"red":        (self.onKeyRed, ""),
			"green":      (self.onKeyGreen, ""),
			"yellow":     (self.onKeyYellow, ""),
			"blue":       (self.onKeyBlue, ""),

			"red_long":        (self.onKeyRedLong, ""),
			"green_long":      (self.onKeyGreenLong, ""),
			"yellow_long":     (self.onKeyYellowLong, ""),
			"blue_long":       (self.onKeyBlueLong, ""),

		}, -2)
		
		self.onLayoutFinish.append(self.setCustomTitle)
		self.onFirstExecBegin.append(self.onFirstExec)

	def setCustomTitle(self):
		self.setTitle(_(self.libraryName))

	def onFirstExec(self):
		
		
		if self.select is None: # Initial Start of View, select first entry in list
			sort = False
			if self.onFirstExecSort is not None:
				self.activeSort = self.onFirstExecSort
				sort = True
			filter = False
			if self.onFirstExecFilter is not None:
				self.activeFilter = self.onFirstExecFilter
				filter = True
			
			self._load(ignoreSort=sort, ignoreFilter=filter)
			self.refresh()
		else: # changed views, reselect selected entry
			print self.select #(None, {'ImdbId': 'tt1190080'})
			sort = False
			if self.onFirstExecSort is not None:
				self.activeSort = self.onFirstExecSort
				sort = True
			filter = False
			if self.onFirstExecFilter is not None:
				self.activeFilter = self.onFirstExecFilter
				filter = True
			
			self._load(self.select[0], ignoreSort=sort, ignoreFilter=filter)
			keys = self.select[1].keys()
			listViewList = self["listview"].list
			for i in range(len(listViewList)):
				entry = listViewList[i]
				found = True
				for key in keys:
					if entry[1][key] != self.select[1][key]:
						found = False
						break
				if found:
					self["listview"].setIndex(i)
					break
			self.refresh()

	def onKeyOk(self):
		self.onEnter()

	def onKeyCancel(self):
		self.onLeave()

	def onKeyInfo(self):
		pass

	def onKeyMenu(self):
		self.displayPluginsMenu()

	def onKeyLeft(self):
		pass
	def onKeyRight(self):
		pass

	def onKeyLeftQuick(self):
		pass
	def onKeyRightQuick(self):
		pass

	def onKeyUp(self):
		self.onPreviousEntry()

	def onKeyDown(self):
		self.onNextEntry()

	def onKeyUpQuick(self):
		self.onPreviousEntryQuick()

	def onKeyDownQuick(self):
		self.onNextEntryQuick()

	def onKeyRed(self):
		self.onToggleSort()

	def onKeyRedLong(self):
		self.onChooseSort()

	def onKeyGreen(self):
		self.onToggleFilter()

	def onKeyGreenLong(self):
		self.onChooseFilter()

	def onKeyYellow(self):
		pass

	def onKeyYellowLong(self):
		pass

	def onKeyBlue(self):
		self.onToggleView()

	def onKeyBlueLong(self):
		self.onChooseView()

	activeSort = ("Default", None, False)
	def onToggleSort(self):
		for i in range(len(self.onSortKeyValuePair)):
			if self.activeSort[1] == self.onSortKeyValuePair[i][1]:
				if (i+1) < len(self.onSortKeyValuePair):
					self.activeSort = self.onSortKeyValuePair[i + 1]
				else:
					self.activeSort = self.onSortKeyValuePair[0]
				break
		
		self.sort()
		self.filter()
		
		self.refresh()

	def onChooseSortCallback(self, choice):
		if choice is not None:
			self.activeSort = choice[1]
			self.sort()
			self.filter()
			self.refresh()

	def onChooseSort(self):
		menu = []
		for e in self.onSortKeyValuePair:
			menu.append((_(e[0]), e, ))
		selection = 0
		for i in range(len(self.onSortKeyValuePair)):
			if self.activeSort[1] == self.onSortKeyValuePair[i][1]:
				selection = i
				break
		self.session.openWithCallback(self.onChooseSortCallback, ChoiceBox, title=_("Select sort"), list=menu, selection=selection)

	activeFilter = ("All", (None, False), "")
	def onToggleFilter(self):
		for i in range(len(self.onFilterKeyValuePair)):
			if self.activeFilter[1][0] == self.onFilterKeyValuePair[i][1][0]:
				# Genres == Genres
				
				# Try to select the next genres subelement
				found = False
				subelements = self.onFilterKeyValuePair[i][2]
				for j in range(len(subelements)):
					#print "if self.activeFilter[2] == subelements[j]:", self.activeFilter[2], subelements[j]
					if self.activeFilter[2] == subelements[j]:
						# Action == Action
						if (j+1) < len(subelements):
							y = subelements[j + 1]
							found = True
							break
				
				if found is True:
					x = self.onFilterKeyValuePair[i]
					self.activeFilter = (x[0], x[1], y, )
				else:
					# If we are at the end of all genres subelements select the next one
					if (i+1) < len(self.onFilterKeyValuePair):
						x = self.onFilterKeyValuePair[i + 1]
					else:
						x = self.onFilterKeyValuePair[0]
					self.activeFilter = (x[0], x[1], x[2][0], )
				
				break
		
		self.sort()
		self.filter()
		
		self.refresh()

	def onChooseFilterCallback(self, choice):
		if choice is not None:
			self.activeFilter = choice[1]
			self.sort()
			self.filter()
			
			self.refresh()

	def onChooseFilter(self):
		menu = []
		
		selection = 0
		counter = 0
		
		for i in range(len(self.onFilterKeyValuePair)):
			x = self.onFilterKeyValuePair[i]
			subelements = self.onFilterKeyValuePair[i][2]
			for j in range(len(subelements)):
				y = subelements[j]
				text = "%s: %s" % (_(x[0]), _(y))
				menu.append((text, (x[0], x[1], y, )))
				if self.activeFilter[1][0] == self.onFilterKeyValuePair[i][1][0]:
					if self.activeFilter[2] == subelements[j]:
						selection = counter
				counter += 1
		
		self.session.openWithCallback(self.onChooseFilterCallback, ChoiceBox, title=_("Select filter"), list=menu, selection=selection)

	def onToggleView(self):
		# These allow us to get the correct list
		#self.currentKeyValuePair
		# But we also need the selected element
		select = None
		selection = self["listview"].getCurrent()
		if selection is not None:
			primaryKeyValuePair = {}
			print self.onEnterPrimaryKeys
			for key in self.onEnterPrimaryKeys:
				if key != "play":
					primaryKeyValuePair[key] = selection[1][key]
			select = (self.currentKeyValuePair, primaryKeyValuePair)
		self.close((DMC_View.ON_CLOSED_CAUSE_CHANGE_VIEW, select, self.activeSort, self.activeFilter))

	def onChooseViewCallback(self, choice):
		if choice is not None:
			# These allow us to get the correct list
			#self.currentKeyValuePair
			# But we also need the selected element
			select = None
			selection = self["listview"].getCurrent()
			if selection is not None:
				primaryKeyValuePair = {}
				print self.onEnterPrimaryKeys
				for key in self.onEnterPrimaryKeys:
					if key != "play":
						primaryKeyValuePair[key] = selection[1][key]
				select = (self.currentKeyValuePair, primaryKeyValuePair)
			self.close((DMC_View.ON_CLOSED_CAUSE_CHANGE_VIEW, select, self.activeSort, self.activeFilter, choice[1]))

	def onChooseView(self):
		menu = getViews()
		selection = 0
		for i in range(len(menu)):
			if self.viewName[1] == menu[i][1]:
				selection = i
				break
		self.session.openWithCallback(self.onChooseViewCallback, ChoiceBox, title=_("Select view"), list=menu, selection=selection)

	def onNextEntry(self):
		printl("", self)
		if self.FAST_STILLPIC is False:
			self.refresh()

	def onNextEntryQuick(self):
		printl("", self)
		if self.APILevel == 1:
			self["listview"].down()
		elif self.APILevel >= 2:
			self["listview"].selectNext()
		if self.FAST_STILLPIC is False:
			self.refresh(False)
		else:
			self.refresh()

	def onPreviousEntry(self):
		printl("", self)
		if self.FAST_STILLPIC is False:
			self.refresh()

	def onPreviousEntryQuick(self):
		printl("", self)
		if self.APILevel == 1:
			self["listview"].up()
		elif self.APILevel >= 2:
			self["listview"].selectPrevious()
		if self.FAST_STILLPIC is False:
			self.refresh(False)
		else:
			self.refresh()

	def onNextPage(self):
		printl("", self)
		if self.APILevel == 1:
			self["listview"].pageDown()
		elif self.APILevel >= 2:
			itemsPerPage = int(self["listview_itemsperpage"].getData())
			itemsTotal = self["listview"].count()
			index = self["listview"].getIndex() + itemsPerPage
			if index >= itemsTotal:
				index = itemsTotal - 1
			self["listview"].setIndex(index)
		self.refresh()

	def onPreviousPage(self):
		printl("", self)
		if self.APILevel == 1:
			self["listview"].pageUp()
		elif self.APILevel >= 2:
			itemsPerPage = int(self["listview_itemsperpage"].getData())
			itemsTotal = self["listview"].count()
			index = self["listview"].getIndex() - itemsPerPage
			if index < 0:
				index = 0
			self["listview"].setIndex(index)
		self.refresh()

	onEnterPrimaryKeys = None
	onLeavePrimaryKeyValuePair = None
	onLeaveSelectKeyValuePair = None
	currentKeyValuePair = None

	def onEnter(self):
		printl("", self, "D")
		selection = self["listview"].getCurrent()
		if selection is not None:
			print "selection", selection
			primaryKeyValuePair = None
			if self.onEnterPrimaryKeys is not None:
				if "play" in self.onEnterPrimaryKeys:
					printl("playEntry ->", self, "D")
					self.playEntry(selection[1])
					printl("playEntry <-", self, "D")
					return
				else:
					primaryKeyValuePair = {}
					for key in self.onEnterPrimaryKeys:
						primaryKeyValuePair[key] = selection[1][key]
			self._load(primaryKeyValuePair)
			#self["listview"].setIndex(0)
		self.refresh()

	def onLeave(self):
		selectKeyValuePair = self.onLeaveSelectKeyValuePair
		print selectKeyValuePair
		if selectKeyValuePair is None:
			self.close()
			return
		
		self._load(self.onLeavePrimaryKeyValuePair)
		for i in range(len(self.listViewList)):
			entry = self.listViewList[i][1]
			print i, entry
			isIndex = True
			
			for key in selectKeyValuePair.keys():
				if entry[key] != selectKeyValuePair[key]:
					isIndex = False
					break
			if isIndex:
				self["listview"].setIndex(i)
				break
		self.refresh()

	def _load(self, primaryKeys=None, ignoreSort=False, ignoreFilter=False):
		print "primaryKeys", primaryKeys
		self.currentKeyValuePair = primaryKeys
		library = self.loadLibrary(primaryKeys)
		self.listViewList = library[0]
		#print self.listViewList
		self.onEnterPrimaryKeys = library[1]
		self.onLeavePrimaryKeyValuePair = library[2]
		self.onLeaveSelectKeyValuePair = library[3]
		self.onSortKeyValuePair = library[4]
		self.onFilterKeyValuePair = library[5]
		
		print "onEnterPrimaryKeys", self.onEnterPrimaryKeys
		print "onLeavePrimaryKeyValuePair", self.onLeavePrimaryKeyValuePair
		print "onLeaveSelectKeyValuePair", self.onLeaveSelectKeyValuePair
		
		if ignoreSort is False:
			# After changing the lsit always return to the default sort
			self.activeSort = self.onSortKeyValuePair[0]
		
		if ignoreFilter is False:
			# After changing the lsit always return to the default filter
			x = self.onFilterKeyValuePair[0]
			self.activeFilter = (x[0], x[1], x[2][0], )
		
		self.sort()
		self.filter()

	def sort(self):
		self._sort()

	def _sort(self):
		if self.activeSort[1] is None:
			self.listViewList.sort(key=lambda x: x[2], reverse=self.activeSort[2])
		else:
			self.listViewList.sort(key=lambda x: x[1][self.activeSort[1]], reverse=self.activeSort[2])

	def filter(self):
		self._filter()

	def _filter(self):
		print self.activeFilter
		listViewList = []
		if self.activeFilter[1][0] is None:
			listViewList = self.listViewList
		else:
			
			if self.activeFilter[1][1]:
				listViewList = [x for x in self.listViewList if self.activeFilter[2] in x[1][self.activeFilter[1][0]]]
			else:
				listViewList = [x for x in self.listViewList if x[1][self.activeFilter[1][0]]  == self.activeFilter[2]]
		
		self["listview"].setList(listViewList)
		self["listview"].setIndex(0)

	def setText(self, name, value, ignore=False, what=None):
		try:
			if self[name]:
				if len(value) > 0:
					self[name].setText(value)
				elif ignore is False:
					if what is None:
						self[name].setText(_("Not available"))
					else:
						self[name].setText(what + ' ' + _("not available"))
				else:
					self[name].setText(" ")
		except Exception, ex:
			printl("Exception: " + str(ex), self)

	def refresh(self, changeBackdrop=True):
		selection = self["listview"].getCurrent()
		if selection is not None:
			self._refresh(selection, changeBackdrop)

	def _refresh(self, selection, changeBackdrop):
		pass

	def playEntry(self, entry):
		if self._playEntry(entry) is False:
			title = _("Not found!\n")
			text = entry["Path"] + _("\n\nPlease make sure that your drive is connected/mounted.")
			self.session.open(MessageBox, title + text, type = MessageBox.TYPE_ERROR)

	def displayPluginsMenu(self):
		pluginList = []
		plugins = getPlugins(where=Plugin.MENU_MOVIES_PLUGINS)
		for plugin in plugins:
			pluginList.append((plugin.name, plugin.start, ))
		
		if len(pluginList) == 0:
			pluginList.append((_("No plugins available"), None, ))
		
		self.session.openWithCallback(self.displayPluginsMenuCallback, ChoiceBox, \
			title=_("Plugins"), list=pluginList)

	def displayPluginsMenuCallback(self, choice):
		if choice is None or choice[1] is None:
			return
		
		selection = self["listview"].getCurrent()
		if selection is not None:
			self.session.open(choice[1], selection[1])

#registerPlugin(Plugin(name=_("Set view as default"), fnc=setViewAsDefault, where=Plugin.MENU_MOVIES_PLUGINS))
#registerPlugin(Plugin(name=_("Bookmark view"), fnc=bookmarkView, where=Plugin.MENU_MOVIES_PLUGINS))