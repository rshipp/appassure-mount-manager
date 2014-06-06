from pyramid.exceptions import NotFound
from pyramid.renderers import get_renderer
from pyramid.view import view_config

from aamm import Manager
import config

class AAMMViews(object):
    def __init__(self, request):
        self.request = request
        renderer = get_renderer("templates/layout.pt")
        self.layout = renderer.implementation().macros['layout']
        self.aamm = Manager(config.server, config.port,
                config.username, config.password, config.tz_offset)

    @view_config(route_name='home', renderer='templates/index.pt')
    def home(self):
        return dict(title='Protected Machines',
                machines=self.aamm.get_machines())

    @view_config(route_name='machine_view', renderer='templates/machine_view.pt')
    def machine_view(self):
        machine = self.request.matchdict['machine']
        try:
            machine_name, recovery_points = self.aamm.get_recovery_points(machine)
            return dict(title=machine_name, recovery_points=recovery_points)
        except KeyError:
            raise NotFound

def notfound(request):
    request.response.status = 404
    return dict(title='No Such Machine')
