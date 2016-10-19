from __future__ import print_function

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
        make_option('--url',
                    action='store', dest='url', type="string",
                    help='Set the server url. e.g. yourdomain.com'),
        make_option('--nginx',
                    action='store', dest='nginx', type="string",
                    help='Set the NGINX folder. default: /etc/nginx',
                    default='/etc/nginx'),
        make_option('--sitename',
                    action='store', dest='sitename', type='string',
                    help='the nginx file name base'),
    )
    help = "Creates the NGINX file over the site-available folder"
    args = "--env --url [--nginx]"

    def handle(self, *args, **options):
        """ """
        BASE_DIR = settings.BASE_DIR
        REPO_DIR = str(BASE_DIR)
        PROJECT_NAME = basename(BASE_DIR)

        environment = options.get('env', '')
        server_url = options.get('url', '')
        sitename = options.get('sitename', '')

        if not sitename:
            sitename = server_url

        NGINX_TARGET_FOLDER = options.get('nginx', '/etc/nginx')

        if not environment or not server_url:
            self.stdout.write('---> ERROR: You must set the --env and --url parameters.\n')
            self.stdout.write('./manage.py nginxentry --env=staging --url=mydomain.com\n')
            self.stdout.write('./manage.py nginxentry --help\n')
            return

        DATA = {
            'environment': environment,
            'project_name': PROJECT_NAME,
            'server_url': server_url,
            'project_repo_folder': REPO_DIR,
        }

        NGINX_CONF_SOURCE = "{0}/nginx.{1}" \
            .format(join(REPO_DIR, 'config/nginx'), environment)
        NGINX_FILE = "{0}/sites-available/{1}_{2}_{3}" \
            .format(NGINX_TARGET_FOLDER, PROJECT_NAME, sitename, environment)

        try:
            content = open(NGINX_CONF_SOURCE, 'r')
            template = Template(content.read())
            content.close()
        except:
            self.stdout.write('---> ERROR: Invalid {0} file.\n'
                              .format(NGINX_CONF_SOURCE))
            return

        try:
            content = open(NGINX_FILE, 'w+')
            content.write(template.render(Context(DATA)))
            content.close()
        except:
            self.stdout.write('---> ERROR: Invalid target {0} file.\n'
                              .format(NGINX_FILE))
            return

        self.stdout.write('--> {0}\n'.format(NGINX_FILE))
        self.stdout.write('[OK] nginx sites-available successfuly created\n')
