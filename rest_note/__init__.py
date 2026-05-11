from krita import Krita, DockWidgetFactory, DockWidgetFactoryBase
from .docker import RestNoteDocker

Krita.instance().addDockWidgetFactory(
    DockWidgetFactory(
        "restNoteDocker",
        DockWidgetFactoryBase.DockRight,
        RestNoteDocker
    )
)
