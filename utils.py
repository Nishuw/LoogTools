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

def zoom_in(pdf_view):
    """Zooms in the PDF view."""
    current_zoom = pdf_view.zoomFactor()
    pdf_view.setZoomFactor(current_zoom + 0.1)

def zoom_out(pdf_view):
    """Zooms out the PDF view."""
    current_zoom = pdf_view.zoomFactor()
    pdf_view.setZoomFactor(current_zoom - 0.1)