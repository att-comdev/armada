sudo apt install -y virtualenv

#sudo su - ubuntu

# Virtualenv
cd ~
virtualenv venv
source venv/bin/activate

# libgit
sudo sh armada/scripts/libgit2.sh

# k8s deps
mkdir ~/.kube
touch ~/.kube/config
sudo cat /etc/kubernetes/admin.conf > ~/.kube/config
