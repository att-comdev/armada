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

import mock
import pytest

from armada.handlers.tiller import Tiller
from armada import errors as ex


def test_install_release(mocker):
    # instantiate Tiller object
    mock_ip = mocker.patch.object(Tiller, '_get_tiller_ip')
    mock_grpc = mocker.patch('armada.handlers.tiller.grpc')
    mock_config = mocker.patch('armada.handlers.tiller.Config')
    mock_install_request = mocker.patch(
        'armada.handlers.tiller.InstallReleaseRequest')
    mock_stub = mocker.patch('armada.handlers.tiller.ReleaseServiceStub')
    mock_grpc.insecure_channel.return_value = None
    mock_ip.return_value = '0.0.0.0'
    tiller = Tiller()
    assert tiller._get_tiller_ip() == '0.0.0.0'

    # set params
    chart = mock.Mock()
    dry_run = False
    name = None
    namespace = None
    initial_values = None
    updated_values = mock_config(raw=initial_values)
    wait = False
    timeout = 3600

    tiller.install_release(chart, name, namespace,
                           dry_run=dry_run, values=initial_values,
                           wait=wait, timeout=timeout)

    mock_stub.assert_called_with(tiller.channel)
    release_request = mock_install_request(
        chart=chart,
        dry_run=dry_run,
        values=updated_values,
        release=name,
        namespace=namespace,
        wait=wait,
        timeout=timeout
    )
    (mock_stub(tiller.channel).InstallRelease
     .assert_called_with(release_request,
                         tiller.timeout,
                         metadata=tiller.metadata))

    initial_values = {'a': 'b'}
    release_request = mock_install_request(
        chart=chart,
        dry_run=dry_run,
        values=updated_values,
        release=name,
        namespace=namespace,
        wait=wait,
        timeout=timeout
    )
    (mock_stub(tiller.channel).InstallRelease
     .assert_called_with(release_request,
                         tiller.timeout,
                         metadata=tiller.metadata))


def test_tiller_get_channel(mocker):
    mock_ip = mocker.patch.object(Tiller, '_get_tiller_ip')
    mock_ip.return_value = '1.1.1.1'

    resp = Tiller().get_channel()
    assert resp is not None


def test_tiller_get_tiller_ip(mocker):
    mock_tiller = mocker.patch.object(Tiller, '_get_tiller_pod')
    pod = mock.Mock(pod_ip='0.0.0.0')
    status = mock.Mock(status=pod)
    mock_tiller.return_value = status

    tiller = Tiller()

    assert tiller._get_tiller_ip() == '0.0.0.0'

    tiller = Tiller(tiller_host='1.1.1.1')
    assert tiller._get_tiller_ip() == '1.1.1.1'


def test_tiller_get_tiller_pod(mocker):
    mock_k8s = mocker.patch('armada.handlers.tiller.K8s.get_namespace_pod')
    mock_tiller = mocker.patch.object(Tiller, 'get_channel')
    mock_tiller.return_value = None

    status = mock.Mock(pod_ip='0.0.0.0')
    metadata = mock.Mock(name='tiller-deploy-1898392')
    item = mock.Mock(metadata=metadata, status=status)
    items = mock.Mock(items=[item])

    mock_k8s.get_namespace_pod.return_value = items

    tiller = Tiller()

    err_message = 'Tiller Service : Could not find service '
    '(Check if service is up)'

    with pytest.raises(ex.HandlerError, match=err_message):
        assert tiller._get_tiller_ip()


def test_tiller_get_tiller_status(mocker):
    mock_tiller = mocker.patch.object(Tiller, '_get_tiller_pod')
    pod = mock.Mock(pod_ip='0.0.0.0')
    status = mock.Mock(status=pod)
    mock_tiller.return_value = status

    tiller = Tiller()

    assert tiller.tiller_status() is True
