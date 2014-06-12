from pyramid.config import Configurator
from pyramid.renderers import JSON


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_renderer('prettyjson', JSON(indent=4))
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('api', '/api')
    config.add_route('machine_api', '/api/{machine}')
    config.add_route('machine_view', '/{machine}/{machine_name}')
    config.add_route('mount_do',
            '/{machine}/{machine_name}/{point_id}/{volume_ids}')
    config.add_route('dismount_do', '/{machine}/{machine_name}/dismount')
    config.add_view('aamm.views.notfound',
            renderer='aamm:templates/404.pt',
            context='pyramid.exceptions.NotFound')
    config.scan()
    return config.make_wsgi_app()
