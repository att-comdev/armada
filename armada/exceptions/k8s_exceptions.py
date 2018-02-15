from armada.exceptions.base_exception import ArmadaBaseException as ex


class KubernetesException(ex):
    '''Base class for Kubernetes exceptions and error handling.'''

    message = 'An unknown Kubernetes error occured.'


class KubernetesUnknownStreamingEventTypeException(KubernetesException):
    '''Exception for getting an unknown event type from the Kubernetes API'''

    message = 'An unknown event type was returned from the streaming API.'


class KubernetesErrorEventException(KubernetesException):
    '''Exception for getting an error from the Kubernetes API'''

    message = 'An error event was returned from the streaming API.'
