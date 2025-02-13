from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt

def create_scrollable_area(widget: QWidget) -> QScrollArea:
    """
    Cria uma área rolável para um widget.

    Args:
        widget: O widget a ser colocado dentro da área rolável.

    Returns:
        Um QScrollArea contendo o widget fornecido.
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

    Args:
        widget: O widget ao qual o layout será aplicado.

    Returns:
        Um QVBoxLayout que foi aplicado ao widget fornecido.
    """
    layout = QVBoxLayout()
    widget.setLayout(layout)
    return layout

# ATUALIZAÇÃO NECESSÁRIA no navigation.py para incluir as novas abas
def load_telefonia_tabs(self):
    from codigos_sip import CodigosSIPWidget
    from telefonia import TelefoniaWidget
    from coleta_logs_telefonia import ColetaDeLogsWidget # Importe a classe aqui

    # Adiciona aba Códigos SIP
    codigos_sip_widget = CodigosSIPWidget()
    self.tab_widget.addTab(codigos_sip_widget, "Códigos SIP")

    # Adiciona aba Telefonia
    telefonia_widget = TelefoniaWidget()
    self.tab_widget.addTab(telefonia_widget, "Telefonia")