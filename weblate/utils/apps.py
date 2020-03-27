#
# Copyright © 2012 - 2020 Michal Čihař <michal@cihar.com>
#
# This file is part of Weblate <https://weblate.org/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from django.apps import AppConfig
from django.conf import settings
from django.contrib.postgres.lookups import SearchLookup
from django.core.checks import register
from django.db.models import CharField, TextField

from weblate.utils.checks import (
    check_cache,
    check_celery,
    check_data_writable,
    check_database,
    check_errors,
    check_mail_connection,
    check_perms,
    check_settings,
    check_site,
    check_templates,
)
from weblate.utils.django_hacks import monkey_patch_translate
from weblate.utils.errors import init_error_collection
from weblate.utils.version import check_version

from .db import (
    MySQLSearchLookup,
    MySQLStringLookup,
    MySQLSubstringLookup,
    PostgreSQLStringLookup,
    PostgreSQLSubstringLookup,
)


class UtilsConfig(AppConfig):
    name = "weblate.utils"
    label = "utils"
    verbose_name = "Utils"

    def ready(self):
        super().ready()
        register(check_data_writable)
        register(check_mail_connection, deploy=True)
        register(check_celery, deploy=True)
        register(check_database, deploy=True)
        register(check_cache, deploy=True)
        register(check_settings, deploy=True)
        register(check_templates, deploy=True)
        register(check_site, deploy=True)
        register(check_perms, deploy=True)
        register(check_errors, deploy=True)
        register(check_version)

        monkey_patch_translate()

        init_error_collection()

        engine = settings.DATABASES["default"]["ENGINE"]
        if engine == "django.db.backends.postgresql":
            CharField.register_lookup(SearchLookup)
            TextField.register_lookup(SearchLookup)
            CharField.register_lookup(PostgreSQLSubstringLookup)
            TextField.register_lookup(PostgreSQLSubstringLookup)
            CharField.register_lookup(PostgreSQLStringLookup)
            TextField.register_lookup(PostgreSQLStringLookup)
        elif engine == "django.db.backends.mysql":
            CharField.register_lookup(MySQLSearchLookup)
            TextField.register_lookup(MySQLSearchLookup)
            CharField.register_lookup(MySQLSubstringLookup)
            TextField.register_lookup(MySQLSubstringLookup)
            CharField.register_lookup(MySQLStringLookup)
            TextField.register_lookup(MySQLStringLookup)
        else:
            raise Exception("Unsupported database: {}".format(engine))
