
class EksAuth(object):
  __all__ = ['getSession','getToken','getKubernetesConfig']
  import base64 as __base64
  import boto3 as __boto3
  import time as __time
  import logging as __logging
  FORMAT = "%(asctime)-15s %(message)s"
  __logging.basicConfig(format=FORMAT,level=__logging.INFO)
  #Disable boto3 logging
  __logging.getLogger('boto3').setLevel(__logging.CRITICAL)
  #Disable botocore logging
  __logging.getLogger('botocore').setLevel(__logging.CRITICAL)
  #Disable nose logging
  __logging.getLogger('nose').setLevel(__logging.CRITICAL)
  #Disable s3transfer logging
  __logging.getLogger('s3transfer').setLevel(__logging.CRITICAL)

  from kubernetes import client as __client
  from kubernetes import config as __config
  from kubernetes.client import configuration as __configuration
  from kubernetes.client.rest import ApiException as __ApiException
  from botocore.signers import RequestSigner as __RequestSigner
  



  def __init__(self,name, region_name='us-east-1'):
    self.clusterName = name
    self.region_name = region_name
    self.roleArn = None


  def getSession(self):
    '''
    This function will return a session object used to sign
    the url, you can pass roleArn to authenticate agains
    a role
    '''
    if self.roleArn == None:
      self.__logging.debug('default')
      return self.__boto3.Session(region_name=self.region_name)
    else:
      sts = self.__boto3.client('sts')
      self.__logging.debug('role %s', self.roleArn)
      try:
        authDict=sts.assume_role(RoleArn=self.roleArn, RoleSessionName='PythonIAMAuth')['Credentials']
      except Exception as e:
        self.__logging.error("Error: " , e)
      sess = self.__boto3.Session(region_name=self.region_name,
          aws_access_key_id=authDict['AccessKeyId'],
          aws_secret_access_key=authDict['SecretAccessKey'],
          aws_session_token=authDict['SessionToken'])
      self.__logging.debug (sess)
      self.__logging.debug (authDict)
      return sess

  def getToken(self):
    """
    This function will generate the IAM EKS Role to authenticate
    against the cluster
    """
    sess = self.getSession()
    signer = self.__RequestSigner('sts', sess.region_name, 'sts', 'v4', sess.get_credentials(), sess.events)
    req_params='Action=GetCallerIdentity&Version=2011-06-15'
    params = { 'method': 'GET', 'url': 'https://sts.amazonaws.com/?' + req_params, 'body': {},'headers': {'x-k8s-aws-id': self.clusterName}, 'context': {} }
    url=signer.generate_presigned_url(params, region_name='us-east-1', operation_name='',expires_in=60)
    self.__logging.debug('URL: ' + url)
    b64url=self.__base64.urlsafe_b64encode(url)
    self.__logging.debug ('Mod of b64: %s %s' % (len(url) % 4, len(url)))
    self.__logging.debug ('F... padding '  + b64url)
    while ('=' in b64url):
      url += b'&'
      b64url=self.__base64.urlsafe_b64encode(url)
      self.__logging.debug ('F... padding '  + b64url)
      self.__time.sleep(1)
    self.__logging.debug('URL' + url)
    self.__logging.debug('Base64 encode ' + b64url)
    value = 'k8s-aws-v1.' + b64url
    self.__logging.debug('EKS Token: ' + value)
    return value

  def getContextForCluster(self):
    contexts, active_context = self.__config.list_kube_config_contexts()
    if not contexts:
      self.__logging.debug ('No Contexts')
      return
    self.__logging.debug ('CTX LIST: ' + str(contexts))
    for ctx in contexts:
      self.__logging.debug ('TEST: ' + str(ctx['context']['cluster']))
      self.__logging.debug('sample:::: ' + ctx['name'])
      if ctx['context']['cluster'] == self.clusterName:
        self.__logging.debug ("Found Context:: " + ctx['name'])
        return ctx['name']
      else:
        self.__logging.debug ("Next")

  def getKubernetesConfig(self):
    self.__config.load_kube_config(context=self.getContextForCluster())
    configuration = self.__client.Configuration()
    configuration.api_key['authorization'] = self.getToken()
    configuration.api_key_prefix['authorization'] = 'Bearer'
    #api = client.ApiClient(self.configuration)
    #cli = client.CoreV1Api(self.api)
    self.__logging.debug(configuration.api_key['authorization'])
    return configuration

