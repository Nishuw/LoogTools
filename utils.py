from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt

def create_scrollable_area(widget: QWidget) -> QScrollArea:
    """
    Cria uma área rolável para um widget.
    """
    scroll = QScrollArea()
    scroll.setWidget(widget)
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    return scroll

def setup_widget_layout(widget: QWidget) -> QVBoxLayout:
    """
    Configura um layout vertical básico para um widget.
    """
    layout = QVBoxLayout()
    widget.setLayout(layout)
    return layout

# Atualização necessária no navigation.py para incluir as novas abas
def load_telefonia_tabs(self):
    from codigos_sip import CodigosSIPWidget
    from telefonia import TelefoniaWidget
    
    # Adiciona aba Códigos SIP
    codigos_sip_widget = CodigosSIPWidget()
    self.tab_widget.addTab(codigos_sip_widget, "Códigos SIP")
    
    # Adiciona aba Telefonia
    telefonia_widget = TelefoniaWidget()
    self.tab_widget.addTab(telefonia_widget, "Telefonia")