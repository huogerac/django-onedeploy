from os import pardir
from os.path import abspath, basename, dirname, join

from optparse import make_option

from django.template import Context, Template
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--env',
                    action='store', dest='env', type="string",
                    help='Set environment. e.g. staging or production'),
        make_option('--user',
                    action='store', dest='user', type="string",
                    help='Set the unix user that has permission to run gunicorn'),
        make_option('--url',
                    action='store', dest='url', type="string",
                    help='Set the server url. e.g. yourdomain.com'),
        make_option('--site',
                    action='store', dest='site', type="string",
                    help='Set the Django SITE_ID'),
    )
    help = "Creates the Gunicorn conf file"
    args = "--env --user --url --site"

    def handle(self, *args, **options):
        """ """
        ROOT_DIR = str(settings.ROOT_DIR)
        PROJECT_DIR = str(settings.PROJECT_DIR)
        PROJECT_NAME = basename(settings.ROOT_DIR)
        VIRTUALENV_DIR = abspath(join(settings.ROOT_DIR, pardir))

        environment = options.get('env', '')
        user = options.get('user', '')
        server_url = options.get('url', '')
        site_id = options.get('site', '')

        if not environment or \
           not user or not server_url or \
           not site_id:
            self.stdout.write('---> ERROR: You must set all the parameters.\n')
            self.stdout.write('./manage.py gunicornentry --help\n')
            return

        DATA = {
            'environment': environment,
            'project_name': PROJECT_NAME,
            'project_name_upper': PROJECT_NAME.upper(),
            'user': str(user),
            'site_id': site_id,
            'server_url': server_url,
            'root_dir': ROOT_DIR,
            'virtualenv_folder': VIRTUALENV_DIR,
        }

        GUNICORN_CONF_SOURCE = "{0}/gunicorn.{1}".format(
            join(ROOT_DIR, 'config/nginx'), environment)
        GUNICORN_FILE = "/etc/init/gunicorn-{0}_{1}_{2}.conf".format(
            PROJECT_NAME, server_url, environment)

        try:
            content = open(GUNICORN_CONF_SOURCE, 'r')
            template = Template(content.read())
            content.close()
        except:
            self.stdout.write('---> ERROR: Invalid {0} source file.\n'
                              .format(GUNICORN_CONF_SOURCE))
            return

        try:
            content = open(GUNICORN_FILE, 'w+')
            content.write(template.render(Context(DATA)))
            content.close()
        except:
            self.stdout.write('---> ERROR: Invalid {0} target file.\n'
                              .format(GUNICORN_FILE))
            return

        self.stdout.write('--> {0}\n'.format(GUNICORN_FILE))
        self.stdout.write('[OK] gunicorn file successfuly created\n')
