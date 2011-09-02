##############################################################################
# THIS FILE HAS ALL CLASSES AND FUNCTION THAT ARE NEEDED FOR THE WEBIF
# TO PROVIDE CLICKABLE MAIN-ACTIONS
##############################################################################

from urllib import urlencode
from Components.config import config
from twisted.web.resource import Resource

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.DMC_Global import Update
from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_WebInterfaceExtras.core.WebData import WebData
from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_WebInterfaceExtras.core.WebHelper import WebHelper
#------------------------------------------------------------------------------------------

# +++ LAZY IMPORTS +++
Manager = None
MediaInfo = None
utf8ToLatin = None
MediaInfo = None
MobileImdbComProvider = None
# --- LAZY IMPORTS ---

##########################
# CLASS:
##########################
class Home(Resource):

	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global utf8ToLatin
		global Manager
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
		if Manager is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Manager import Manager
			
		finalOutput = WebHelper().getHtmlCore("Home")
		
		currentVersion = Update().getInstalledRevision()
		movieCount = str(Manager().getMoviesCount())
		tvShowCount = str(Manager().getSeriesCount())
		episodeCount = str(Manager().getEpisodesCount())
		
		updateType = Update().getCurrentUpdateType()
		latestStable = Update().getLatestRevisionByType("release")
		latestNightly = Update().getLatestRevisionByType("nightly")
		
		finalOutput = finalOutput.replace("<!-- MOVIE_COUNT -->", movieCount)
		finalOutput = finalOutput.replace("<!-- TVSHOW_COUNT -->", tvShowCount)
		finalOutput = finalOutput.replace("<!-- EPISODE_COUNT -->", episodeCount)
		
		revisionText = """	<br>
							Your update type => %s.<br>
							The latest stable release => %s.<br>
							The latest nightly release => %s. <br>		
		""" % (updateType, latestStable, latestNightly)

		finalOutput = finalOutput.replace("<!-- CURRENT_VERSION -->", "Your installed revision => " + currentVersion)
		finalOutput = finalOutput.replace("<!-- LATEST_VERSION -->", revisionText)
		
		return utf8ToLatin(finalOutput)

##########################
# CLASS:
##########################		
class Movies(Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global MediaInfo
		global utf8ToLatin
		if MediaInfo is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.MediaInfo import MediaInfo
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
				
		finalOutput = WebHelper().getHtmlCore("Movies", True)
			
		tableHeader = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/Movies/Header.tpl")
		tableBody = u""
		
		entries = WebData().getData("movies")
		finalOutput = finalOutput.replace("<!-- CUSTOM_TITLE -->", " - Movies")
		
		for entry in entries:
			evtEdit = self._editMovie(entry, "isMovie")
			evtDelete = self._deleteMovie(entry, "isMovie")
			
			tableBody += u"""   <tr>
							<td><img src=\"/media/%s_poster_195x267.png\" width="78" height="107" alt="n/a"></img></td>
							<td>%s</td>
							<td>%s</td>
							<td><a href=http://www.imdb.com/title/%s/ target="_blank">%s</a></td>
							<td>%s</td>
							<td>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/edit-grey.png" alt="edit" title="edit" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/delete-grey.png" alt="delete" title="delete" /></a>
							</td>
						  </tr>
					""" % (entry.ImdbId, entry.Title, entry.Year, entry.ImdbId, entry.ImdbId, entry.Filename + u"." + entry.Extension, evtEdit, evtDelete)
		
		finalOutput = finalOutput.replace("<!-- CUSTOM_THEAD -->", tableHeader)
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY -->", tableBody)
	
		return utf8ToLatin(finalOutput)
		
	############################################
	def _editMovie (self, entry, type):
		onclick  = "javascript:window.open('/mediaForm?"
		onclick  += urlencode({'type':type}) + "&"
		onclick  += urlencode({'mode':"showEditForm"}) + "&"		
		onclick  += urlencode({'Id':entry.Id})  
		onclick  += "', '_self');"
		
		return onclick
	############################################
	def _deleteMovie (self, entry, type):
		onclick = "javascript:if (confirm('Are you sure to delete the selected record?'))"
		onclick += "{window.open('/action?type="
		onclick += str(type) + "&"
		onclick += "mode=deleteMediaFromDb&"
		onclick += "Id=" + str(entry.Id) + "&"
		onclick += "ParentId=" + str(entry.ParentId)
		onclick += "', '_self')} else { return};"
		
		return onclick

##########################
# CLASS:
##########################
class TvShows(Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global MediaInfo
		global utf8ToLatin
		if MediaInfo is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.MediaInfo import MediaInfo
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
	
		finalOutput = WebHelper().getHtmlCore("TvShows", True)
			
		tableHeader = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/TvShows/Header.tpl")
		tableBody = u""
		
		entries = WebData().getData("tvshows")
		finalOutput = finalOutput.replace("<!-- CUSTOM_TITLE -->", " - Series")

		for entry in entries:
			evtShowEpisodes = self._getEpisodesOfTvShow(entry.Id)
			evtEdit = self._editTvShow(entry, "isTvShow")
			evtAddEpisode = self._addEpisode(entry, "isEpisode")
			evtDelete = self._deleteTvShow(entry, "isTvShow") 
			
			tableBody += u"""   <tr>
							<td><img src=\"/media/%s_poster_195x267.png\" width="78" height="107" alt="n/a"></img></td>
							<td>%s</td>
							<td>%s</td>
							<td>%s</td>
							<td><a href=http://thetvdb.com/index.php?tab=series&id=%s target="_blank">%s</a></td>
							<td>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/showEpisodes.png" alt="show Episodes" title="show Episodes" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/edit-grey.png" alt="edit" title="edit" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/add.png" alt="add" title="add" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/delete-grey.png" alt="delete" title="delete" /></a>						
							</td>
						    </tr>
			""" % (entry.TheTvDbId, entry.Title, entry.Year, entry.ImdbId, entry.TheTvDbId, entry.TheTvDbId, evtShowEpisodes, evtEdit, evtAddEpisode, evtDelete)
		
		finalOutput = finalOutput.replace("<!-- CUSTOM_THEAD -->", tableHeader)
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY -->", tableBody)
	
		return utf8ToLatin(finalOutput)
		
	#############################################
	def _getEpisodesOfTvShow (self, parentId):
		onclick = "javascript:window.open('/episodes?ParentId=" + str(parentId) + "', '_self');"
		
		return onclick
	#############################################
	def _editTvShow (self, entry, type):
		onclick  = "javascript:window.open('/mediaForm?"
		onclick  += urlencode({'type':type}) + "&"
		onclick  += urlencode({'mode':"showEditForm"}) + "&"		
		onclick  += urlencode({'Id':entry.Id})  
		onclick  += "', '_self');"
		
		return onclick
	#############################################
	def _addEpisode	(self, entry, type):
		onclick  = "javascript:window.open('/addRecord?"
		onclick  += urlencode({'type':type}) + "&"
		onclick  += urlencode({'ParentId':entry.Id}) # + "&"
		onclick  += "', '_self');"
		
		return onclick	
	#############################################
	def _deleteTvShow (self, entry, type):
		onclick = "javascript:if (confirm('Are you sure to delete the selected record?'))"
		onclick += "{window.open('/action?type="
		onclick += str(type) + "&"
		onclick += "mode=deleteMediaFromDb&"
		onclick += "Id=" + str(entry.Id) + "&"
		onclick += "ParentId=" + str(entry.ParentId)
		onclick += "', '_self')} else { return};"
		
		return onclick
		
##########################
# CLASS:
##########################
class Episodes(Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global MediaInfo
		global utf8ToLatin
		if MediaInfo is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.MediaInfo import MediaInfo
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
		
		finalOutput = WebHelper().getHtmlCore("Episodes", True)
		finalOutput = finalOutput.replace("<!-- CUSTOM_TITLE -->", " - Episodes")

		tableHeader = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/Episodes/Header.tpl")
		tableBody = u""
		
		# get episodes of serie (parentid)
		ParentId = request.args["ParentId"][0]		
		entries = WebData().getData("EpisodesOfSerie", ParentId)
		
		for entry in entries:
			evtEdit = self._editEpisode(entry, "isEpisode")
			evtDelete = self._deleteEpisode(entry, "isEpisode")
			
			tableBody += u"""   <tr>
							<td><img src=\"/media/%s_poster_195x267.png\" width="78" height="107" alt="n/a"></img></td>
							<td>%s</td>
							<td>%s</td>
							<td>%s</td>
							<td>%s</td>
							<td>%s</td>
							<td>%s</td>
							<td>%s</td>
							<td>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/edit-grey.png" alt="edit" title="edit" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/delete-grey.png" alt="delete" title="delete" /></a>
							</td>
						    </tr>
			""" % (entry.TheTvDbId, entry.Title, entry.Season, entry.Episode, entry.Year, entry.ImdbId, entry.TheTvDbId, entry.Filename + u"." + entry.Extension, evtEdit, evtDelete)
		
		finalOutput = finalOutput.replace("<!-- CUSTOM_THEAD -->", tableHeader)
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY -->", tableBody)
	
		return utf8ToLatin(finalOutput)

	########################################
	def _editEpisode (self, entry, type):
		onclick  = "javascript:window.open('/mediaForm?"
		onclick  += urlencode({'type':type}) + "&"
		onclick  += urlencode({'mode':"showEditForm"}) + "&"		
		onclick  += urlencode({'Id':entry.Id})  
		onclick  += "', '_self');"
		
		return onclick
	########################################
	def _deleteEpisode (self, entry, type):
		onclick = "javascript:if (confirm('Are you sure to delete the selected record?')) {window.open('/action?type="
		onclick  += str(type) + "&"
		onclick  += "mode=deleteMediaFromDb&"
		onclick  += "Id=" + str(entry.Id) + "&"
		onclick  += "ParentId=" + str(entry.ParentId)
		onclick  += "', '_self')} else { return};"
		
		return onclick
	
##########################
# CLASS:
##########################
class Failed(Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global MediaInfo
		global utf8ToLatin
		if MediaInfo is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.MediaInfo import MediaInfo
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
				
		finalOutput = WebHelper().getHtmlCore("Failed", True)

		tableHeader = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/Failed/Header.tpl")
		tableBody = u""
		
		entries = WebData().getData("failed")
		
		for entry in entries:
			##
			# Todo should be escaped not changed ;-)
			# leads to a javascript error if ' or " is in the string
			##
			if type(entry) == MediaInfo:
				entry.Plot = WebData().cleanStrings(entry.Plot)
				entry.Tag = WebData().cleanStrings(entry.Tag)

			tableBody += u"""   <tr>
								<td>%s</td>
								<td>%s</td>
								<td>%s</td>
							    </tr>
						""" % (entry.Path + u"/" + entry.Filename + u"." + entry.Extension, entry.CauseStr, entry.Description)
				
		finalOutput = finalOutput.replace("<!-- CUSTOM_THEAD -->", tableHeader)
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY -->", tableBody)
	
		return utf8ToLatin(finalOutput)


		
##########################
# CLASS:
##########################		
class Options (Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
		
		finalOutput = WebHelper().getHtmlCore("Options")
				
		return utf8ToLatin(finalOutput)

##########################
# CLASS:
##########################		
class GlobalSetting (Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
				
		finalOutput = WebHelper().getHtmlCore("Options" , True, "Global")
		
		tableBody = self.buildTableGlobal("options.global")
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY_GLOBAL -->", tableBody)
	
		return utf8ToLatin(finalOutput)	
	
	def buildTableGlobal(self, section):
		tableBody = u""
		entries = WebData().getData(section)
		for entry in entries:
			value = entry[1].value
			
			configType, tag = WebHelper().prepareTable(value, entry[1])
			
			tableBody += u"""
							<form id="saveSetting" action="/action" method="get">
								<input type="hidden" name="mode" value="options.saveconfig"></input>
								<input type="hidden" name="what" value="settings_global"></input>
								<input type="hidden" name="type" value="%s"></input>
								<tr id="tr_entry">
									<td width="550px">%s:</td>
									<td width="0px"><input id="name" name="name" type="hidden" size="50" value="%s"></input></td>
									<td width="200px">%s</td>
									<td width="70px"><input type="submit" value="save"></input></td>
								</tr>
							</form>
					""" % (configType, entry[0], entry[0], tag)
		
		return tableBody

##########################
# CLASS:
##########################		
class SyncSettings (Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
		
		finalOutput = WebHelper().getHtmlCore("Options" , True, "Sync")
						
		tableBody = self.buildTableSyncFileTypes("options.sync")
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY_SYNC_FILETYPES -->", tableBody)
		
		tableBody = self.buildTableSyncPath("options.sync")
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY_SYNC_PATH -->", tableBody)
	
		return utf8ToLatin(finalOutput)

	def buildTableSyncFileTypes(self, section):
		tableBody = u""
		pathsConfig = WebData().getData(section)
		
		name = u"FileTypes"
		value = '|'.join(pathsConfig.getFileTypes())
		configType, tag = WebHelper().prepareTable(value, None)
		
		tableBody += u"""
						<table align="left" id="settings_sync">
								<form id="saveSetting" action="/action" method="get">
									<input type="hidden" name="mode" value="options.saveconfig"></input>
									<input type="hidden" name="what" value="settings_sync"></input>
									<input type="hidden" name="section" value="filetypes"></input>
									<input type="hidden" name="type" value="%s"></input>
									<tr id="tr_entry">
										<td width="100px">%s:</td>
										<td width="0px"><input id="name" name="name" type="hidden" size="50" value="%s"></input></td>
										<td width="700px">%s</td>
										<td width="70px"><input type="submit" value="save"></input></td>
									</tr>
								</form>
							</table>
				""" % (configType, name, name, tag)
		
		return tableBody
		
	def buildTableSyncPath(self, section):
		tableBody = u""
		pathsConfig = WebData().getData(section)
		
		tableBody += u"""<table align="left" id="settings_sync_sub">"""
		tableBody += u"""<tr>
							<td width="100px">Enabled</td>
							<td width="5100px">Directory</td>
							<td width="50px">Type</td>
							<td width="50px">UseFolder</td>
							<td width="70px"></td>
						</tr>"""
		
		for path in pathsConfig.getPaths():
			name = u"Directory"
			value = path["directory"]
			id = path["directory"]
			
			configType, tag = WebHelper().prepareTable(value, None)
			
			types = (path["type"], pathsConfig.getPathsChoices()["type"], )
			
			
			tableBody += u"""
							<form id="saveSetting" action="/action" method="get">
								<input type="hidden" name="mode" value="options.saveconfig"></input>
								<input type="hidden" name="what" value="settings_sync"></input>
								<input type="hidden" name="section" value="paths"></input>
								<input type="hidden" name="Id" value="%s"></input>
								<tr id="tr_entry">
									<td width="50px">%s</td>
									<td width="200px">%s</td>
									<td width="50px">%s</td>
									<td width="50px">%s</td>
									<td width="70px"><input type="submit" value="save"></input></td>
								</tr>
							</form>
					""" % (id, WebHelper().prepareTable(path["enabled"], None, "enabled")[1], WebHelper().prepareTable(path["directory"], None, "directory")[1], 
									WebHelper().prepareTable(types, None, "type")[1], WebHelper().prepareTable(path["usefolder"], None, "usefolder")[1])
		
		tableBody += u"""</table>"""
		
		return tableBody

##########################
# CLASS:
##########################		
class Logs (Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
		
		finalOutput = WebHelper().getHtmlCore("Logs")
	
		return utf8ToLatin(finalOutput)	

##########################
# CLASS:
##########################		
class Valerie (Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
		
		finalOutput = WebHelper().getHtmlCore("Logs" , False, "Valerie")
	
		return utf8ToLatin(finalOutput)	

##########################
# CLASS:
##########################		
class Enigma (Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
				
		finalOutput = WebHelper().getHtmlCore("Logs" , False, "Enigma")
	
		return utf8ToLatin(finalOutput)		

##########################
# CLASS:
##########################		
class Extras (Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
		
		finalOutput = WebHelper().getHtmlCore("Extras")
	
		return utf8ToLatin(finalOutput)
		
##########################
# CLASS:
##########################		
class Backup (Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
				
		finalOutput = WebHelper().getHtmlCore("Extras" , True, "Backup")
	
		return utf8ToLatin(finalOutput)	

##########################
# CLASS:
##########################		
class Restore (Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
		
		finalOutput = WebHelper().getHtmlCore("Extras" , True, "Restore")
	
		return utf8ToLatin(finalOutput)
		