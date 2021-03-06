# -*- coding: utf-8 -*-
#
# Copyright: (c) 2019, F5 Networks Inc.
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json
import pytest
import sys

if sys.version_info < (2, 7):
    pytestmark = pytest.mark.skip("F5 Ansible modules require Python >= 2.7")

from ansible.module_utils.basic import AnsibleModule

try:
    from library.modules.bigip_interface import ApiParameters
    from library.modules.bigip_interface import ModuleParameters
    from library.modules.bigip_interface import ModuleManager
    from library.modules.bigip_interface import ArgumentSpec

    # In Ansible 2.8, Ansible changed import paths.
    from test.units.compat import unittest
    from test.units.compat.mock import Mock
    from test.units.compat.mock import patch

    from test.units.modules.utils import set_module_args
except ImportError:
    from ansible_collections.f5networks.f5_modules.plugins.modules.bigip_interface import ApiParameters
    from ansible_collections.f5networks.f5_modules.plugins.modules.bigip_interface import ModuleParameters
    from ansible_collections.f5networks.f5_modules.plugins.modules.bigip_interface import ModuleManager
    from ansible_collections.f5networks.f5_modules.plugins.modules.bigip_interface import ArgumentSpec

    # Ansible 2.8 imports
    from units.compat import unittest
    from units.compat.mock import Mock
    from units.compat.mock import patch

    from units.modules.utils import set_module_args


fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')
fixture_data = {}


def load_fixture(name):
    path = os.path.join(fixture_path, name)

    if path in fixture_data:
        return fixture_data[path]

    with open(path) as f:
        data = f.read()

    try:
        data = json.loads(data)
    except Exception:
        pass

    fixture_data[path] = data
    return data


class TestParameters(unittest.TestCase):
    def test_module_parameters(self):
        args = dict(
            description='my description',
            enabled=False,
            bundle='enabled',
            bundle_speed='40G',
            force_gigabit_fiber=False,
            prefer_port='sfp',
            media_fixed='40000-FD',
            media_sfp='40000-FD',
            flow_control='tx-rx',
            forward_error_correction='auto',
            port_fwd_mode='l3',
            lldp_tlvmap=136,
            lldp_admin='txonly',
            stp=True,
            stp_auto_edge_port=False,
            stp_edge_port=True,
            stp_link_type='p2p',
            sflow=dict(
                poll_interval=10,
                poll_interval_global=False
            )
        )

        p = ModuleParameters(params=args)
        assert p.description == 'my description'
        assert p.disabled is True
        assert p.enabled is None
        assert p.bundle == 'enabled'
        assert p.bundle_speed == '40G'
        assert p.force_gigabit_fiber == 'disabled'
        assert p.prefer_port == 'sfp'
        assert p.media_fixed == '40000-FD'
        assert p.media_sfp == '40000-FD'
        assert p.flow_control == 'tx-rx'
        assert p.forward_error_correction == 'auto'
        assert p.port_fwd_mode == 'l3'
        assert p.lldp_tlvmap == 136
        assert p.lldp_admin == 'txonly'
        assert p.stp == 'enabled'
        assert p.stp_auto_edge_port == 'disabled'
        assert p.stp_edge_port == 'true'
        assert p.stp_link_type == 'p2p'
        assert p.sflow_interval == 10
        assert p.sflow_global == 'no'

    def test_api_parameters(self):
        args = load_fixture('load_interface.json')

        p = ApiParameters(params=args)
        assert p.sflow_global == 'no'
        assert p.sflow_interval == 0


class TestManager(unittest.TestCase):
    def setUp(self):
        self.spec = ArgumentSpec()

    def test_update_interface(self, *args):
        set_module_args(dict(
            name='1.1',
            description='my description',
            enabled=False,
            bundle='enabled',
            bundle_speed='40G',
            prefer_port='fixed',
            media_fixed='40000-FD',
            media_sfp='40000-FD',
            forward_error_correction='auto',
            lldp_tlvmap=136,
            lldp_admin='txrx',
            stp_auto_edge_port=False,
            stp_link_type='p2p',
            sflow=dict(
                poll_interval=10,
            ),
            provider=dict(
                server='localhost',
                password='password',
                user='admin'
            )
        ))

        # Configure the parameters that would be returned by querying the
        # remote device

        module = AnsibleModule(
            argument_spec=self.spec.argument_spec,
            supports_check_mode=self.spec.supports_check_mode,
        )
        mm = ModuleManager(module=module)

        # Override methods to force specific logic in the module to happen
        mm.exists = Mock(return_value=True)
        mm.update_on_device = Mock(return_value=True)
        mm.read_current_from_device = Mock(return_value=ApiParameters(params=load_fixture('load_interface.json')))

        results = mm.exec_module()

        assert results['changed'] is True
        assert results['description'] == 'my description'
        assert results['enabled'] == 'no'
        assert results['bundle'] == 'enabled'
        assert results['bundle_speed'] == '40G'
        assert results['prefer_port'] == 'fixed'
        assert results['media_fixed'] == '40000-FD'
        assert results['media_sfp'] == '40000-FD'
        assert results['forward_error_correction'] == 'auto'
        assert results['lldp_tlvmap'] == 136
        assert results['lldp_admin'] == 'txrx'
        assert results['stp_auto_edge_port'] == 'no'
        assert results['stp_link_type'] == 'p2p'
        assert results['sflow']['poll_interval'] == 10
