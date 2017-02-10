from logutil import LOG
from kubernetes import client, config

class K8s(object):


    def __init__(self):
        '''
        Initialize connection to Kubernetes
        '''
        config.load_kube_config()
        self.client = client.CoreV1Api()
