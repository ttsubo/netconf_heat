# Copyright (c) 2016 ttsubo
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php

import uuid

from heat.engine import attributes
from heat.engine import constraints
from heat.engine import properties
from heat.common.i18n import _
from ncclient.xml_ import *
from oslo_log import log as logging
from netconf import Netconf

LOG = logging.getLogger(__name__)

class PolicyOptionsResource(Netconf):

    PROPERTIES = (
        ROUTER_IPADDR, USERNAME, PASSWORD, PORT, POLICY_NAME
    ) = (
        'router_ipaddr', 'username', 'password', 'port', 'policy_name'
    )

    ATTRIBUTES = (
        CONFIG_POLICY_OPTIONS
    ) = (
        'config_policy_options'
    )

    properties_schema = {
        ROUTER_IPADDR: properties.Schema(
            properties.Schema.STRING,
            _('Ip address of the router.'),
            required=True,
        ),
        USERNAME: properties.Schema(
            properties.Schema.STRING,
            _('User name to log on to device.'),
            required=True,
            update_allowed=True
        ),
        PASSWORD: properties.Schema(
            properties.Schema.STRING,
            _('Users password.'),
            required=True,
            update_allowed=True
        ),
        PORT: properties.Schema(
            properties.Schema.INTEGER,
            _('Port of the ssh connection.'),
            default=830,
            update_allowed=True
        ),
        POLICY_NAME: properties.Schema(
            properties.Schema.STRING,
            _('policy_name.'),
            required=True,
            update_allowed=True
        ),
    }

    attributes_schema = {
        CONFIG_POLICY_OPTIONS: attributes.Schema(
            _("config_policy_options attributes."),
            type=attributes.Schema.MAP
        ),
    }

    def config_policy_options(self):
        policy_name = self.properties[self.POLICY_NAME]

        policy_options = """
        policy-options {
            policy-statement %s {
                term 1 {
                    from protocol static;
                    then accept;
                }
            }
        }
        """ % (policy_name)
        return policy_options

    def delete_policy_options(self):
        policy_name = self.properties[self.POLICY_NAME]

        policy_options = """
        <edit-config>
          <target>
            <candidate/>
          </target>
          <default-operation>none</default-operation>
          <config>
            <configuration>
              <policy-options>
                <policy-statement operation="delete">
                  <name>%s</name>
                </policy-statement>
              </policy-options>
            </configuration>
          </config>
        </edit-config>
        """ % (policy_name.encode('utf-8'))
        return policy_options

    def handle_create(self):
        config = self.config_policy_options()
        conn = self.connect()
        self.execute_netconf(conn, config, "create", "policy_options")
        self.resource_id_set(str(uuid.uuid4()))

    def handle_delete(self):
        config = self.delete_policy_options()
        conn = self.connect()
        self.execute_netconf(conn, config, "delete", "policy_options")

    def _show_resource(self):
        result = {}
        conn = self.connect()

        config_filter = new_ele('configuration')
        sub_ele(config_filter, 'policy-options')
        response = conn.get_configuration(format='text', filter=config_filter)
        response.xpath('configuration-text')[0].text
        LOG.info("response=[%s]"% response.xpath('configuration-text')[0].text)
        result["config_routing_options"] = response.xpath('configuration-text')[0].text
        return result

def resource_mapping():
    return {
        'OS::Netconf::PolicyOptionsResource': PolicyOptionsResource,
    }
