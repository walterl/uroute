import gi
import logging

gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk, GdkPixbuf, Gtk, Notify, Pango  # noqa E402

log = logging.getLogger(__name__)


def notify(title, msg, icon='info', timeout=Notify.EXPIRES_DEFAULT):
    if not Notify.is_initted():
        Notify.init('uroute')

    notification = Notify.Notification.new(title, msg, icon=icon)
    notification.set_timeout(timeout)
    notification.show()


class UrouteGui(Gtk.Window):
    def __init__(self, uroute):
        super(UrouteGui, self).__init__()
        self.uroute = uroute
        self.command = None
        self._build_ui()

    def run(self):
        self.show_all()
        self._check_default_browser()

        Notify.init('uroute')
        Gtk.main()

        if Notify.is_initted():
            Notify.uninit()

        return self.command

    def _check_default_browser(self):
        try:
            ask = self.uroute.config['main'].getboolean(
                'ask_default_browser', fallback=True,
            )
        except ValueError:
            self.uroute.config['main']['ask_default_browser'] = 'yes'
            ask = True

        if ask:
            if AskDefaultBrowserDialog(self).run() == Gtk.ResponseType.YES:
                log.debug('Set as default browser')
                if self.uroute.set_as_default_browser():
                    notify(
                        'Default browser set',
                        'Uroute is now configured as your default browser.',
                    )
                else:
                    notify(
                        'Unable to configure Uroute as your default browser',
                        'Please see the application logs for more '
                        'information.',
                        icon='error',
                    )
            else:
                log.debug("Don't set as default browser")

            # Either way, don't ask again
            self.uroute.config['main']['ask_default_browser'] = 'no'
            self.uroute.config.save()

    def _build_ui(self):
        # Init main window
        self.set_title('Uroute - Link Dispatcher')
        self.set_border_width(10)
        self.set_default_size(860, 600)
        self.connect('destroy', self._on_cancel_clicked)
        self.connect('key-press-event', self._on_key_pressed)

        vbox = Gtk.VBox(spacing=6)
        self.add(vbox)

        mono = Pango.FontDescription('monospace')
        self.url_entry = Gtk.Entry()
        self.url_entry.set_text(self.uroute.url or '')
        self.url_entry.modify_font(mono)
        self.command_entry = Gtk.Entry()
        self.command_entry.modify_font(mono)

        vbox.pack_start(self.url_entry, False, False, 0)
        vbox.pack_start(self._build_browser_buttons(), True, True, 0)
        vbox.pack_start(self.command_entry, False, False, 0)
        vbox.pack_start(self._build_button_toolbar(), False, False, 0)

    def _build_browser_buttons(self):
        self.browser_store = Gtk.ListStore(GdkPixbuf.Pixbuf, str, str, object)
        iconview = Gtk.IconView.new()
        iconview.set_model(self.browser_store)
        iconview.set_pixbuf_column(0)
        iconview.set_text_column(1)
        iconview.connect('item-activated', self._on_browser_icon_activated)
        iconview.connect('selection-changed', self._on_browser_icon_selected)

        default_itr = None
        default_program = self.uroute.get_program()

        for i, program in enumerate(self.uroute.programs.values()):
            itr = self.browser_store.append([
                self._load_program_icon(program), program.name,
                program.command, program,
            ])
            if program is default_program:
                log.debug(
                    'Selecting default program: %r',
                    self.browser_store.get_value(itr, 2),
                )
                default_itr = itr

        if default_itr:
            iconview.select_path(self.browser_store.get_path(default_itr))
            self._on_browser_icon_selected(iconview)

        scroll = Gtk.ScrolledWindow()
        scroll.add(iconview)
        return scroll

    def _load_program_icon(self, program):
        icon = None
        if program.icon:
            icon = Gtk.Image.new_from_file(program.icon).get_pixbuf()
            if icon.get_width() > 64 or icon.get_height() > 64:
                icon = icon.scale_simple(
                    64, 64, GdkPixbuf.InterpType.BILINEAR,
                )
            if icon is None:
                log.warn('Unable to load icon from %s', program.icon)

        if icon is None:
            icon = Gtk.IconTheme.get_default().load_icon(
                'help-about', 64, 0,
            )
        return icon

    def _build_button_toolbar(self):
        hbox = Gtk.Box(spacing=6)

        button = Gtk.Button.new_with_mnemonic('Run')
        button.connect('clicked', self._on_run_clicked)
        hbox.pack_end(button, False, False, 0)

        button = Gtk.Button.new_with_label('Cancel')
        button.connect('clicked', self._on_cancel_clicked)
        hbox.pack_end(button, False, False, 0)

        return hbox

    def _on_browser_icon_activated(self, iconview, path):
        self._on_run_clicked(None)

    def _on_browser_icon_selected(self, iconview):
        model = iconview.get_model()
        paths = iconview.get_selected_items()
        if not paths:
            log.debug('No browser selected.')
            return
        sel_iter = model.get_iter(paths[0])

        self.command_entry.set_text(model.get_value(sel_iter, 2))

    def _on_cancel_clicked(self, _button):
        self.command = None
        self.hide()
        Gtk.main_quit()

    def _on_run_clicked(self, _button):
        self.command = self.command_entry.get_text()
        self.uroute.url = self.url_entry.get_text()

        log.debug('Command: %r, URL: %r', self.command, self.uroute.url)

        self.hide()
        Gtk.main_quit()

    def _on_key_pressed(self, wnd, event):
        if event.keyval == Gdk.KEY_Escape:
            self._on_cancel_clicked(None)
        if event.keyval == Gdk.KEY_Return:
            self._on_run_clicked(None)


class AskDefaultBrowserDialog(Gtk.Dialog):
    def __init__(self, parent):
        super(AskDefaultBrowserDialog, self).__init__(
            'Default browser', parent, 0, (
                Gtk.STOCK_NO, Gtk.ResponseType.NO,
                Gtk.STOCK_YES, Gtk.ResponseType.YES,
            )
        )

        self.set_default_size(150, 100)

        self.get_content_area().add(Gtk.Label(
            'Do you want to set Uroute as your default browser?',
        ))

    def run(self):
        self.show_all()
        response = super(AskDefaultBrowserDialog, self).run()
        self.hide()
        self.destroy()
        return response
