
class EksAuth(object):
  __all__ = ['getSession','getToken','getKubernetesConfig']
  import base64 as __base64
  import boto3 as __boto3
  import time as __time

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
      logging.info('default')
      return self.__boto3.Session(region_name=self.region_name)
    else:
      sts = self.__boto3.client('sts')
      logging.info('role %s', self.roleArn)
      try:
        authDict=sts.assume_role(RoleArn=self.roleArn, RoleSessionName='PythonIAMAuth')['Credentials']
      except Exception as e:
        print("Error: " , e)
      sess = self.__boto3.Session(region_name=self.region_name,
          aws_access_key_id=authDict['AccessKeyId'],
          aws_secret_access_key=authDict['SecretAccessKey'],
          aws_session_token=authDict['SessionToken'])
      print (sess)
      print (authDict)
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
    print('URL: ' + url)
    b64url=self.__base64.urlsafe_b64encode(url)
    print ('Mod of b64: %s %s' % (len(url) % 4, len(url)))
    print ('F... padding '  + b64url)
    while ('=' in b64url):
      url += b'&'
      b64url=self.__base64.urlsafe_b64encode(url)
      print ('F... padding '  + b64url)
      self.__time.sleep(1)
    print('URL' + url)
    print('Base64 encode ' + b64url)
    value = 'k8s-aws-v1.' + b64url
    print('EKS Token: ' + value)
    return value

  def getContextForCluster(self):
    contexts, active_context = self.__config.list_kube_config_contexts()
    if not contexts:
      print ('No Contexts')
      return
    print ('CTX LIST: ' + str(contexts))
    for ctx in contexts:
      print ('TEST: ' + str(ctx['context']['cluster']))
      print('sample:::: ' + ctx['name'])
      if ctx['context']['cluster'] == self.clusterName:
        print ("Found Context:: " + ctx['name'])
        return ctx['name']
      else:
        print ("Next")

  def getKubernetesConfig(self):
    self.__config.load_kube_config(context=self.getContextForCluster())
    configuration = self.__client.Configuration()
    configuration.api_key['authorization'] = self.getToken()
    configuration.api_key_prefix['authorization'] = 'Bearer'
    #api = client.ApiClient(self.configuration)
    #cli = client.CoreV1Api(self.api)
    print(configuration.api_key['authorization'])
    return configuration

import logging

FORMAT = "%(asctime)-15s %(message)s"
logging.basicConfig(format=FORMAT,level=logging.DEBUG)
def main():
  from kubernetes import client
  client2 = EksAuth('eks-sample')
  #client2.roleArn='arn:aws:iam::297286928529:role/KubernetesAdmin'

  try:
    eks = client2.getKubernetesConfig()
    print('EKS ' + str(eks))
    api = client.ApiClient(eks)
    cli = client.CoreV1Api(api)
    b=cli.list_pod_for_all_namespaces(limit=1)
    #print(b)
  except Exception as e :
    logging.info(e)

if __name__ == "__main__":
  main()
