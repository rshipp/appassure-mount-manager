from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPNotFound


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('machine_view', '/{machine}')
    config.add_route('mount_do',
            '/{machine_id}/{machine_name}/{point_id}/{point_time}/{volume_ids}')
    config.add_view('aamm.views.notfound',
            renderer='aamm:templates/404.pt',
            context='pyramid.exceptions.NotFound')
    config.scan()
    return config.make_wsgi_app()
