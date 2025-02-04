# Gnu General Public License - see LICENSE.TXT

import time
import threading

import xbmc
import xbmcgui

from .simple_logging import SimpleLogging

log = SimpleLogging(__name__)


class ActionAutoClose(threading.Thread):

    last_interaction = time.time()
    parent_dialog = None
    stop_thread = False
    progress_call_back = None
    time_out = 20

    def __init__(self, parent):
        self.parent_dialog = parent
        self.stop_thread = False
        self.last_interaction = time.time()
        threading.Thread.__init__(self)
        self.time_out = 20

    def run(self):
        log.debug("ActionAutoClose Running")
        monitor = xbmc.Monitor()
        while not monitor.abortRequested() and not self.stop_thread:
            time_since_last = time.time() - self.last_interaction
            log.debug("ActionAutoClose time_since_last : {0}", time_since_last)

            if time_since_last > self.time_out:
                log.debug("ActionAutoClose Closing Parent")
                self.parent_dialog.close()
                break

            if self.progress_call_back is not None:
                percentage = (float(time_since_last) / float(self.time_out)) * 100
                self.progress_call_back.update_progress(percentage)

            monitor.waitForAbort(0.1)

        log.debug("ActionAutoClose Exited")

    def set_timeout(self, t):
        self.time_out = t

    def set_callback(self, call_back):
        self.progress_call_back = call_back

    def set_last(self):
        self.last_interaction = time.time()
        log.debug("ActionAutoClose set_last : {0}", self.last_interaction)

    def stop(self):
        log.debug("ActionAutoClose stop_thread called")
        self.stop_thread = True


class ActionMenu(xbmcgui.WindowXMLDialog):

    selected_action = None
    action_items = None
    auto_close_thread = None
    listControl = None
    action_exitkeys_id = None

    def __init__(self, *args, **kwargs):
        log.debug("ActionMenu: __init__")
        xbmcgui.WindowXML.__init__(self, *args, **kwargs)
        self.auto_close_thread = ActionAutoClose(self)
        self.auto_close_thread.start()

    def onInit(self):
        log.debug("ActionMenu: onInit")
        self.action_exitkeys_id = [10, 13]

        self.listControl = self.getControl(3000)
        self.listControl.addItems(self.action_items)
        self.setFocus(self.listControl)

        # bg_image = self.getControl(3010)
        # bg_image.setHeight(50 * len(self.action_items) + 20)

    def onFocus(self, control_id):
        pass

    def doAction(self, action_id):
        pass

    def onMessage(self, message):
        log.debug("ActionMenu: onMessage: {0}", message)

    def onAction(self, action):

        if action.getId() == 10:  # ACTION_PREVIOUS_MENU
            self.auto_close_thread.stop()
            self.close()
        elif action.getId() == 92:  # ACTION_NAV_BACK
            self.auto_close_thread.stop()
            self.close()
        else:
            self.auto_close_thread.set_last()
            log.debug("ActionMenu: onAction: {0}", action.getId())

    def onClick(self, control_id):
        if control_id == 3000:
            self.selected_action = self.listControl.getSelectedItem()
            log.debug("ActionMenu: Selected Item: {0}", self.selected_action)
            self.auto_close_thread.stop()
            self.close()

    def setActionItems(self, action_items):
        self.action_items = action_items

    def getActionItem(self):
        return self.selected_action
