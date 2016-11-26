# Copyright (c) 2016 ttsubo
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php

from heat.engine import attributes
from heat.engine import properties
from heat.engine import resource
from heat.common.i18n import _
from oslo_log import log as logging
from ncclient import manager

LOG = logging.getLogger(__name__)

class Netconf(resource.Resource):

    def connect(self):
        host = self.properties[self.ROUTER_IPADDR]
        port = self.properties[self.PORT]
        username = self.properties[self.USERNAME]
        password = self.properties[self.PASSWORD]

        conn = manager.connect(host=host,
                port=port,
                username=username,
                password=password,
                timeout=30,
                device_params = {'name':'junos'},
                hostkey_verify=False)
        return conn

    def execute_netconf(self, conn, config, operation, config_type):
        LOG.info("--------------------------------------------")
        LOG.info("1. conn.lock (%s)"% config_type)
        LOG.info("--------------------------------------------")
        try:
            lock = conn.lock('candidate')
            LOG.info("return:[%s]"% lock.tostring)
        except Exception as e:
            LOG.info("Error: type=[%s], message=[%s]"%(type(e), e.message))
            raise
                     

        LOG.info("--------------------------------------------------------")
        LOG.info("2. conn.load_configuration / conn.rpc (%s)"% config_type)
        LOG.info("--------------------------------------------------------")
        if operation == "create":
            try:
                load_conf = conn.load_configuration(target="candidate",
                                                  config=config, format='text')
                LOG.info("return:[%s]"% load_conf.tostring)
            except Exception as e:
                LOG.info("Error: type=[%s], message=[%s]"%(type(e), e.message))
                raise
        elif operation == "delete":
            try:
                rpc_conf = conn.rpc(config)
                LOG.info("return:[%s]"% rpc_conf.tostring)
            except Exception as e:
                LOG.info("Error: type=[%s], message=[%s]"%(type(e), e.message))
                raise


        LOG.info("--------------------------------------------")
        LOG.info("3. conn.validate (%s)"% config_type)
        LOG.info("--------------------------------------------")
        try:
            validate = conn.validate()
            LOG.info("return:[%s]"% validate.tostring)
        except Exception as e:
            LOG.info("Error: type=[%s], message=[%s]"%(type(e), e.message))
            raise


        LOG.info("--------------------------------------------")
        LOG.info("4. conn.compare_configuration (%s)"% config_type)
        LOG.info("--------------------------------------------")
        try:
            compare = conn.compare_configuration()
            LOG.info("return:[%s]"% compare.tostring)
        except Exception as e:
            LOG.info("Error: type=[%s], message=[%s]"%(type(e), e.message))
            raise
 

        LOG.info("--------------------------------------------")
        LOG.info("5. conn.commit (%s)"% config_type)
        LOG.info("--------------------------------------------")
        try:
            commit = conn.commit()
            LOG.info("return:[%s]"% commit.tostring)
        except Exception as e:
            LOG.info("Error: type=[%s], message=[%s]"%(type(e), e.message))
            raise

        LOG.info("--------------------------------------------")
        LOG.info("6. conn.unlock (%s)"% config_type)
        LOG.info("--------------------------------------------")
        try:
            unlock = conn.unlock()
            LOG.info("return:[%s]"% unlock.tostring)
        except Exception as e:
            LOG.info("Error: type=[%s], message=[%s]"%(type(e), e.message))
            raise

    def _resolve_attribute(self, name):
        attributes = self._show_resource()
        return attributes
