import sublime, sublime_plugin
import threading 

from . import common


class GotoBookmarkCommand(sublime_plugin.WindowCommand, common.BaseBookmarkCommand):
	def __init__(self, window):
		self.thread = None
		common.BaseBookmarkCommand.__init__(self, window)


	def run(self):
		if self.thread is not None:
			self.thread.join()

		self._load()

		if len(self.bookmarks) == 0:
			sublime.status_message("no bookmarks to goto!")
			return 0
			
		self.thread = GotoBookmarkHandler(self.window, self)
		self.thread.start()


class GotoBookmarkHandler(threading.Thread):
	def __init__(self, window, BookmarkCommand):
		self.window = window
		
		self.bookmarks = common.get_bookmarks() 
		#keep a reference to the original file if the user cancels
		self.originalFile = common.Bookmark(window, "originalFile")

		threading.Thread.__init__(self)  


	def run(self):
		view = self.window.active_view()

		bookmarkItems = common.create_bookmarks_panel_items(self.window, self.bookmarks)
		self.window.show_quick_panel(bookmarkItems, self._done, 0, -1, self._highlighted)
		

	def _done(self, index):

		if index == -1:
			#if cancelled, go back to original file
			self.originalFile.goto(self.window, False)
			common.gLog("Cancelled goto")

		else:
			self._goto_bookmark(index)
			common.gLog("Done with goto")


	def _highlighted(self, index):
		self._goto_bookmark(index)


	def _goto_bookmark(self, index):
		selectedBookmark = self.bookmarks[index]
		selectedBookmark.goto(self.window, False)