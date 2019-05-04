from gi.repository import Gtk, GObject, GLib
from gettext import gettext as _

class Notification(Gtk.Revealer):

    show_close_btn = GObject.Property(type=bool, default=False)
    show_undo_btn = GObject.Property(type=bool, default=False)

    timeout = GObject.Property(type=int, default=3)

    def __init__(self):
        Gtk.Revealer.__init__(self)
        self._message = ""
        self.__build_widget()
        self.__bind_signals()

    @property
    def notification_message(self):
        return self._message

    @notification_message.setter
    def notification_message(self, new_message):
        self._message = new_message
        self._notification_lbl.set_text(new_message)

    def __build_widget(self):
        self.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.set_transition_duration(600)
        self.set_reveal_child(False)

        notification_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self._close_btn = Gtk.Button()
        self._close_btn.connect("clicked", self.__on_close_btn_clicked)
        close_img = Gtk.Image.new_from_icon_name("window-close-symbolic", Gtk.IconSize.BUTTON)
        self._close_btn.get_style_context().add_class("flat")
        self._close_btn.set_tooltip_text(_("Close the notification"))
        self._close_btn.props.image = close_img
        self._close_btn.props_always_show_image = True


        self._undo_btn = Gtk.Button()
        self._undo_btn.set_label(_("Undo"))
        self._undo_btn.connect("clicked", self.__on_undo_btn_clicked)
        

        self._notification_lbl = Gtk.Label()
        self._notification_lbl.set_text(self.notification_message)
    
        notification_container.pack_start(self._notification_lbl, False, False, 6)
        notification_container.pack_end(self._close_btn, False, False, 6)
        notification_container.pack_end(self._undo_btn, False, False, 6)

        self.add(notification_container)

    def send(self, message):
        self.message = message
        self.set_reveal_child(True)
        GLib.timeout_add_seconds(self.timeout, self.__delete_notification, None)
    
    def __delete_notification(self, *args):
        self.set_reveal_child(False)
        self.message = ""

    def __on_undo_btn_clicked(self, *args):
        pass
    
    def __on_close_btn_clicked(self, *args):
        pass

    def __bind_signals(self):
        self._close_btn.bind_property("visible", self, "show-close-btn", GObject.BindingFlags.DEFAULT)
        self._undo_btn.bind_property("visible", self, "show-undo-btn", GObject.BindingFlags.DEFAULT)
