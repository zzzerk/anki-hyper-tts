import sys
import json

# pyqt
import PyQt5
import logging

# anki imports
import aqt.qt
import aqt.editor
import aqt.gui_hooks
import aqt.sound
import aqt.utils
import anki.hooks

# addon imports
constants = __import__('constants', globals(), locals(), [], sys._addon_import_level_base)
component_batch = __import__('component_batch', globals(), locals(), [], sys._addon_import_level_base)


class BatchDialog(PyQt5.QtWidgets.QDialog):
    def __init__(self, hypertts, note_id_list):
        super(PyQt5.QtWidgets.QDialog, self).__init__()
        self.hypertts = hypertts
        self.note_id_list = note_id_list
        self.batch_component = component_batch.ComponentBatch(self.hypertts, self.note_id_list)

    def setupUi(self):
        self.main_layout = PyQt5.QtWidgets.QVBoxLayout(self)
        self.batch_component.draw(self.main_layout)

def launch_batch_dialog(hypertts, note_id_list):
    logging.info('launch_batch_dialog')
    dialog = BatchDialog(hypertts, note_id_list)
    dialog.setupUi()
    dialog.exec_()


def configure_editor(editor: aqt.editor.Editor, batch_name_list):
    js_command = f"configureEditorHyperTTS({json.dumps(batch_name_list)})"
    print(js_command)
    editor.web.eval(js_command)    

def init(hypertts):
    aqt.mw.addonManager.setWebExports(__name__, r".*(css|js)")

    def browerMenusInit(browser: aqt.browser.Browser):
        menu = aqt.qt.QMenu(constants.ADDON_NAME, browser.form.menubar)
        browser.form.menubar.addMenu(menu)

        action = aqt.qt.QAction(f'HyperTTS Batch...', browser)
        action.triggered.connect(lambda: launch_batch_dialog(hypertts, browser.selectedNotes()))
        menu.addAction(action)

    def shortcut_test(cuts, editor):
        logging.info('editor shortcuts setup')
        cuts.append(("Ctrl+l", lambda: aqt.utils.tooltip("test")))


    def on_webview_will_set_content(web_content: aqt.webview.WebContent, context):
        if not isinstance(context, aqt.editor.Editor):
            return
        addon_package = aqt.mw.addonManager.addonFromModule(__name__)
        javascript_path = [
            f"/_addons/{addon_package}/hypertts.js",
        ]
        css_path =  [
            f"/_addons/{addon_package}/hypertts.css",
        ]
        web_content.js.extend(javascript_path)
        web_content.css.extend(css_path)

    def loadNote(editor: aqt.editor.Editor):
        batch_name_list = hypertts.get_batch_config_list()
        configure_editor(editor, batch_name_list)

    def onBridge(handled, str, editor):
        # logging.debug(f'bridge str: {str}')

        # return handled # don't do anything for now
        if not isinstance(editor, aqt.editor.Editor):
            return handled

        if str.startswith("hypertts:addaudio:"):
            logging.info(f'received message: {str}')
            # editor_manager.process_command(editor, str)
            logging.info(f'note: {editor.note}')
            hypertts.editor_add_audio(str, editor.note, editor.addMode)
            editor.set_note(editor.note)
            return True, None

        return handled

    # browser menus
    aqt.gui_hooks.browser_menus_did_init.append(browerMenusInit)
    # shortcuts
    aqt.gui_hooks.editor_did_init_shortcuts.append(shortcut_test)

    # editor setup
    aqt.gui_hooks.editor_did_load_note.append(loadNote)
    aqt.gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
    aqt.gui_hooks.webview_did_receive_js_message.append(onBridge)