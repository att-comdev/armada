from kubernetes import client, config
from kubernetes.client.rest import ApiException

from logutil import LOG

class K8s(object):
    '''
    Object to obtain the local kube config file
    '''
    def __init__(self):
        '''
        Initialize connection to Kubernetes
        '''
        config.load_kube_config()
        self.client = client.CoreV1Api()
        self.api_client = client.BatchV1Api()

    def delete_job_action(self, name, namespace="default"):
        '''
        :params name - name of the job
        :params namespace - name of pod that job
        '''
        try:
            body = client.V1DeleteOptions()
            self.api_client.delete_namespaced_job(name=name,
                                                  namespace=namespace,
                                                  body=body)
        except ApiException as e:
            LOG.error("Exception when deleting a job: %s", e)

    def create_job_action(self, name, namespace="default"):
        '''
        :params name - name of the job
        :params namespace - name of pod that job
        '''
        LOG.debug(" %s in namespace: %s", name, namespace)

    def get_namespace_pod(self, namespace="default"):
        '''
        :params - namespace - pod namespace

        This will return a list of objects req namespace
        '''

        return self.client.list_namespaced_pod(namespace)
