# tab_navigation.py
from PyQt6.QtWidgets import QTextEdit, QLineEdit
from PyQt6.QtCore import Qt

def setup_tab_navigation(widgets):
    """Configura a navegação por tab entre widgets"""
    for i, current in enumerate(widgets):
        next_widget = widgets[(i + 1) % len(widgets)] if widgets else None
        previous_widget = widgets[i - 1] if widgets else None
        
        if isinstance(current, QTextEdit):
            current.keyPressEvent = lambda event, w=current, next=next_widget, prev=previous_widget: \
                handle_text_edit_tab(event, w, next, prev)
        elif isinstance(current, QLineEdit):
            current.keyPressEvent = lambda event, w=current, next=next_widget, prev=previous_widget: \
                handle_line_edit_tab(event, w, next, prev)

def handle_text_edit_tab(event, widget, next_widget, previous_widget):
    """Trata o pressionamento da tecla tab no QTextEdit"""
    if event.key() == Qt.Key.Key_Tab:
        if event.modifiers() == Qt.KeyboardModifier.ShiftModifier and previous_widget:
            previous_widget.setFocus()
        elif next_widget:
            next_widget.setFocus()
    else:
        QTextEdit.keyPressEvent(widget, event)

def handle_line_edit_tab(event, widget, next_widget, previous_widget):
    """Trata o pressionamento da tecla tab no QLineEdit"""
    if event.key() == Qt.Key.Key_Tab:
        if event.modifiers() == Qt.KeyboardModifier.ShiftModifier and previous_widget:
            previous_widget.setFocus()
        elif next_widget:
            next_widget.setFocus()
    else:
        QLineEdit.keyPressEvent(widget, event)