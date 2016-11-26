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

class ProtocolsResource(Netconf):

    PROPERTIES = (
        ROUTER_IPADDR, USERNAME, PASSWORD, PORT, GROUP_NAME, BGP_TYPE, POLICY_SRATEMENT, NEUGHBOR, PEER_AS
    ) = (
        'router_ipaddr', 'username', 'password', 'port', 'group_name', 'bgp_type', 'policy_statement', 'neighbor', 'peer_as'
    )

    ATTRIBUTES = (
        CONFIG_PROTOCOLS
    ) = (
        'config_protocols'
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
        GROUP_NAME: properties.Schema(
            properties.Schema.STRING,
            _('config name.'),
            required=True,
            update_allowed=True
        ),
        BGP_TYPE: properties.Schema(
            properties.Schema.STRING,
            _('Type of bgp peering.'),
            required=True,
            update_allowed=True
        ),
        POLICY_SRATEMENT: properties.Schema(
            properties.Schema.STRING,
            _('name of policy statement.'),
            required=True,
            update_allowed=True
        ),
        NEUGHBOR: properties.Schema(
            properties.Schema.STRING,
            _('neighbor address for peering.'),
            required=True,
            update_allowed=True
        ),
        PEER_AS: properties.Schema(
            properties.Schema.STRING,
            _('AS number for peering.'),
            required=True,
            update_allowed=True
        ),
    }

    attributes_schema = {
        CONFIG_PROTOCOLS: attributes.Schema(
            _("config_protocols attributes."),
            type=attributes.Schema.MAP
        ),
    }

    def config_protocols(self):
        group_name = self.properties[self.GROUP_NAME]
        bgp_type = self.properties[self.BGP_TYPE]
        policy_statement = self.properties[self.POLICY_SRATEMENT]
        neighbor = self.properties[self.NEUGHBOR]
        peer_as = self.properties[self.PEER_AS]

        protocols = """
        protocols {
            bgp {
                group %s {
                    type %s;
                    export %s;
                    neighbor %s {
                        peer-as %s;
                    }
                }
            }
        }
        """ % (group_name, bgp_type, policy_statement, neighbor, peer_as)
        return protocols

    def delete_protocols(self):
        group_name = self.properties[self.GROUP_NAME]

        protocols = """
        <edit-config>
          <target>
            <candidate/>
          </target>
          <default-operation>none</default-operation>
          <config>
            <configuration>
              <protocols>
                <bgp>
                  <group operation="delete">
                    <name>%s</name>
                  </group>
                </bgp>
              </protocols>
            </configuration>
          </config>
        </edit-config>
        """ % (group_name.encode('utf-8'))
        return protocols

    def handle_create(self):
        config = self.config_protocols()
        conn = self.connect()
        self.execute_netconf(conn, config, "create", "protocols")
        self.resource_id_set(str(uuid.uuid4()))

    def handle_delete(self):
        config = self.delete_protocols()
        conn = self.connect()
        self.execute_netconf(conn, config, "delete", "protocols")

    def _show_resource(self):
        result = {}
        conn = self.connect()

        config_filter = new_ele('configuration')
        sub_ele(config_filter, 'protocols')
        response = conn.get_configuration(format='text', filter=config_filter)
        response.xpath('configuration-text')[0].text
        LOG.info("response=[%s]"% response.xpath('configuration-text')[0].text)
        result["config_protocols"] = response.xpath('configuration-text')[0].text
        return result

def resource_mapping():
    return {
        'OS::Netconf::ProtocolsResource': ProtocolsResource,
    }
