from krita import Krita, Extension
from .docker import RestNoteDockerFactory


class RestNoteExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)
        self.rest_note_docker_factory = None

    def setup(self):
        """Setup the extension and register docker factories"""
        self.rest_note_docker_factory = RestNoteDockerFactory()
        Krita.instance().addDockWidgetFactory(self.rest_note_docker_factory)

    def createActions(self, window):
        """Called after Krita window is initialized"""
        # This method can be used for additional initialization if needed
        pass


app = Krita.instance()
app.addExtension(RestNoteExtension(app))
