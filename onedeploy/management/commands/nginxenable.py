from __future__ import print_function

from os import symlink
from os.path import basename, lexists

from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--env',
                    action='store', dest='env', type="string",
                    help='Set environment. e.g. staging or production'),
        make_option('--url',
                    action='store', dest='url', type="string",
                    help='Set the server url. e.g. yourdomain.com'),
        make_option('--nginx',
                    action='store', dest='nginx', type="string",
                    help='Set the NGINX folder. default: /etc/nginx',
                    default='/etc/nginx'),
    )
    help = "Enables the NGINX site file over the site-enabled folder"
    args = "--env --url [--nginx]"

    def handle(self, *args, **options):
        """ """
        ROOT_DIR = str(settings.ROOT_DIR)
        PROJECT_DIR = str(settings.PROJECT_DIR)
        PROJECT_NAME = basename(ROOT_DIR)

        environment = options.get('env', '')
        server_url = options.get('url', '')
        NGINX_TARGET_FOLDER = options.get('nginx', '/etc/nginx')

        if not environment or not server_url:
            self.stdout.write('---> ERROR: You must set the --env and --url parameters.\n')
            self.stdout.write('./manage.py nginxenable --env=staging --url=mydomain.com\n')
            self.stdout.write('./manage.py nginxenable --help\n')
            return

        user_args = {
            'nginx': NGINX_TARGET_FOLDER,
            'project_name': PROJECT_NAME,
            'domain': server_url,
            'env': environment,
        }

        NGINX_AVAILABLE = "{nginx}/sites-available/{project_name}_{domain}_{env}" \
            .format(**user_args)
        NGINX_ENABLED = "{nginx}/sites-enabled/{project_name}_{domain}_{env}" \
            .format(**user_args)

        if not lexists(NGINX_ENABLED):
            symlink(NGINX_AVAILABLE, NGINX_ENABLED)

        self.stdout.write('--> {0}\n'.format(NGINX_ENABLED))
        self.stdout.write('[OK] nginx sites-enabled successfuly\n')
