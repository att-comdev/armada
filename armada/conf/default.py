# Copyright 2017 The Armada Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from oslo_config import cfg

default_options = [
    cfg.ListOpt(
        'armada_apply_roles',
        default=['admin'],
        help='IDs of approved API access roles.'),
    cfg.StrOpt(
        'auth_url',
        default='http://0.0.0.0/v3',
        help='The default Keystone authentication url.'),
    cfg.BoolOpt(
        'debug',
        default='false',
        help='Print debugging output (set logging level to DEBUG instead of \
        default INFO level).'),
    cfg.ListOpt(
        'default_log_levels',
        default='root=INFO, cliff=INFO, stevedore=INFO, iso8601=INFO',
        help='List of logger=LEVEL pairs.'),
    cfg.BoolOpt(
        'fatal_deprecations',
        default='true',
        help='Enables or disables fatal status of deprecations.'),
    cfg.StrOpt(
        'kubernetes_config_path',
        default='/home/user/.kube/',
        help='Path to Kubernetes configurations.'),
    cfg.StrOpt(
        'instance_format',
        default='[instance: %(uuid)s] ',
        help='The format for an instance that is passed \
        with the log message.'),
    cfg.StrOpt(
        'instance_uuid_format',
        default='[instance: %(uuid)s] ',
        help='The format for an instance UUID that is passed \
        with the log message.'),
    cfg.StrOpt(
        'log_config_append',
        default=None,
        help='The name of a logging configuration file.'),
    cfg.StrOpt(
        'log_date_format',
        default='%Y-%m-%d %H:%M:%S',
        help='Date format for log records.'),
    cfg.StrOpt(
        'log_dir',
        default=None,
        help='(Optional) The base directory used for \
        relative log file paths.'),
    cfg.StrOpt(
        'log_file', default=None, help='(Optional) Path to Armada log file.'),
    cfg.StrOpt(
        'logging_context_format_string',
        default='%(asctime)s.%(msecs)03d %(process)d %(levelname)s \
        %(name)s [%(request_id)s %(user_identity)s] \
        %(instance)s%(message)s',
        help='Format for context logging.'),
    cfg.StrOpt(
        'logging_debug_format_suffix',
        default='%(funcName)s %(pathname)s:%(lineno)d',
        help='Format string to use for log messages \
        when context is undefined.'),
    cfg.StrOpt(
        'logging_default_format_string',
        default='%(asctime)s.%(msecs)03d %(process)d \
        %(levelname)s %(name)s [-] %(instance)s%(message)s',
        help='Format string to use for log \
        messages when context is undefined.'),
    cfg.StrOpt(
        'logging_exception_prefix',
        default='%(asctime)s.%(msecs)03d %(process)d \
        ERROR %(name)s %(instance)s',
        help='Prefix each line of \
        exception output with this format.'),
    cfg.StrOpt(
        'logging_user_identity_format',
        default='%(user)s %(tenant)s %(domain)s \
        %(user_domain)s %(project_domain)s',
        help='Defines the format string for \
        %(user_identity)s that is used in logging_context_format_string.'),
    cfg.BoolOpt(
        'middleware',
        default='true',
        help='Enables or disables Keystone authentication middleware.'),
    cfg.StrOpt(
        'project_domain_name',
        default='default',
        help='The Keystone project domain name used for authentication.'),
    cfg.StrOpt(
        'project_name',
        default='admin',
        help='The Keystone project name used for authentication.'),
    cfg.BoolOpt(
        'publish_errors',
        default='true',
        help='Enables or disables publication of error events.'),
    cfg.IntOpt(
        'rate_limit_burst',
        default='0',
        help='Maximum number of logged messages per rate_limit_interval.'),
    cfg.StrOpt(
        'rate_limit_except_level',
        default='CRITICAL',
        help='Log level name used by rate limiting: \
        CRITICAL, ERROR, INFO, WARNING, DEBUG'),
    cfg.IntOpt(
        'rate_limit_interval',
        default='0',
        help='Maximum number of logged messages per rate_limit_interval.'),
    cfg.StrOpt(
        'ssh_key_path',
        default='/home/user/.ssh/',
        help='Path to SSH private key.'),
    cfg.StrOpt(
        'syslog_log_facility',
        default='LOG_USER',
        help='Syslog facility to receive log lines. \
        This option is ignored if log_config_append is set.'),
    cfg.BoolOpt(
        'use_journal',
        default='false',
        help='Enable journald for logging. (Must be a systemd environment)'),
    cfg.BoolOpt(
        'use_stderr', default='true', help='Log output to standard error.'),
    cfg.BoolOpt('use_syslog', default='true', help='Log output to syslog.'),
    cfg.ListOpt(
        'tiller_release_roles',
        default=['admin'],
        help='IDs of approved API access roles.'),
    cfg.ListOpt(
        'tiller_status_roles',
        default=['admin'],
        help='IDs of approved API access roles.'),
    cfg.BoolOpt(
        'watch_log_file',
        default='false',
        help='Enables instantaneous recreation of a \
        logging file if the file is removed.')
]


def register_opts():
    CONF = cfg.CONF
    CONF.register_opts(default_options)

    # Load config file if exists
    default_config_file = 'etc/armada/armada.conf'
    if (os.path.exists(default_config_file)):
        CONF(['--config-file', default_config_file])


def list_opts():
    return {'DEFAULT': default_options}
