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

class RoutingOptionsResource(Netconf):

    PROPERTIES = (
        ROUTER_IPADDR, USERNAME, PASSWORD, PORT, STATIC_ROUTE, NEXT_HOP, ROUTER_ID, MY_AS
    ) = (
        'router_ipaddr', 'username', 'password', 'port', 'static_route', 'next_hop', 'router_id', 'my_as'
    )

    ATTRIBUTES = (
        CONFIG_ROUTING_OPTIONS
    ) = (
        'config_routing_options'
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
        STATIC_ROUTE: properties.Schema(
            properties.Schema.STRING,
            _('prefix for static route.'),
            default=830,
            update_allowed=True
        ),
        NEXT_HOP: properties.Schema(
            properties.Schema.STRING,
            _('nexthop address.'),
            default=830,
            update_allowed=True
        ),
        ROUTER_ID: properties.Schema(
            properties.Schema.STRING,
            _('router id.'),
            required=True,
            update_allowed=True
        ),
        MY_AS: properties.Schema(
            properties.Schema.STRING,
            _('AS number for myself.'),
            required=True,
            update_allowed=True
        ),
    }

    attributes_schema = {
        CONFIG_ROUTING_OPTIONS: attributes.Schema(
            _("config_routing_options attributes."),
            type=attributes.Schema.MAP
        ),
    }

    def config_routing_options(self):
        static_route = self.properties[self.STATIC_ROUTE]
        next_hop = self.properties[self.NEXT_HOP]
        router_id = self.properties[self.ROUTER_ID]
        my_as = self.properties[self.MY_AS]

        routing_options = """
        routing-options {
            static {
                route %s next-hop %s;
            }
            router-id %s;
            autonomous-system %s;
        }
        """ % (static_route, next_hop, router_id, my_as)
        return routing_options

    def delete_routing_options(self):
        routing_options = """
        <edit-config>
          <target>
            <candidate/>
          </target>
          <default-operation>none</default-operation>
          <config>
            <configuration>
              <routing-options operation="delete"/>
            </configuration>
          </config>
        </edit-config>
        """
        return routing_options

    def handle_create(self):
        config = self.config_routing_options()
        conn = self.connect()
        self.execute_netconf(conn, config, "create", "routing_options")
        self.resource_id_set(str(uuid.uuid4()))

    def handle_delete(self):
        config = self.delete_routing_options()
        conn = self.connect()
        self.execute_netconf(conn, config, "delete", "routing_options")

    def _show_resource(self):
        result = {}
        conn = self.connect()

        config_filter = new_ele('configuration')
        sub_ele(config_filter, 'routing-options')
        response = conn.get_configuration(format='text', filter=config_filter)
        response.xpath('configuration-text')[0].text
        LOG.info("response=[%s]"% response.xpath('configuration-text')[0].text)
        result["config_routing_options"] = response.xpath('configuration-text')[0].text
        return result

def resource_mapping():
    return {
        'OS::Netconf::RoutingOptionsResource': RoutingOptionsResource,
    }
