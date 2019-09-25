## Azure IaaS Scripts

### az-k8s
This is a utility script for quickly creating or modifying a Kubernetes cluster with some of
the more popular options you might want included.  This has been tested in Azure
Government.

#### Examples

For instance running the following command will produce an AKS cluster that
includes Tiller, Prometheus, Nginx Ingress and Cert-Manager.  (Note: an email
address is needed by Let's Encrypt for the certificates issued).

az-k8s -i admin@azurepatterns.com -p -b

You can also customize the number and size of nodes for the node pool by using
-c ans -s.  The following customizes the size and number of nodes and installs
Prometheus and configures the Kubernetes Dashboard

az-k8s -c 4 -s Standard_D16_v3 -p -b

Using the -f option allows you to pass in a yaml file that will be applied after
the cluster has been configured.  For instance the following will install the
hello-world application included in the yaml directory.

az-k8s -f ./yaml/hello-world.yaml

   Usage:
     [-g <group>] Optional: Resource group to use.  Default is supplied if not provided.
     [-l <region>] Optional:  Region to use.  Default is eastus
     [-s <vm-size-by-type>] Optional: Azure VM size. Standard_DS2_v2 is default
     [-i <email address>] Optional: Add Ingress and Cert-Manager to cluster.  Email required for Let's Encrypt
     [-n <k8s name>] Optional: Name for the Kubernetes cluster.  Defaults are supplied if not provided
     [-d <dns name>] Optional: DNS name for the ingress controller.  Defaults are used if not provided.
     [-c <count>] Optional:  Number of nodes in cluster.  Default is 2.
     [-v <kubernetes version> Optional: Version to install of Kubernetes.  Default provided
     [-f <yaml file>] Optional: Yaml file to apply after cluster creation. You can use
                                in your Yaml file and it will be replaced when the script is applied
     [-p ] Optional: Add Prometheus to cluster
     [-b ] Optional: Add Kubenetes Dashboard credentials.  This can be insecure in certain circumstances.
     NOTE:  This program requires az, helm and kubectl to execute


### az-vm

This script is a utility script for quickly creating Azure VMs.  It can be used
to create either Windows or Linux VMs (although the Windows creation process has
not been throughly tested).

This script has been tested in Azure Government.

#### Examples
To quickly spin up a VM use:

./az-vm 

If you want to name the VM and RG then use:

./az-vm -n myVM -g myRG

If you want to create several VMs at once you can use something like:

./az-vm -n myVM -g myRG -c 4 -s Standard_D16_v3

You can also apply cloud-init scripts to supported VMs by using the -d option

./az-vm -d ./cloud-init.yaml

   Usage:
     [-w] create a Windows VM.  Ubuntu is the default
     [-c <num>] how many VMs to create
     [-g <group>] resource group to use
     [-r <region>] region to use
     [-s <vm-size-by-type>] Azure VM size. Standard_DS2_v2 is default
     [-i <image name>] Azure image to base VM off of
     [-d <custom data>] cloud-init script to execute
     [-n <vm name>] name for the VM.  Defaults are supplied if not provided
     [-u <username>] username created on the VM. Defaults are supplied if not provided
     [-a <storage acct>] storage account for VM analytics.  No analytics are reported if not provided.

