# Setup docker storage
mkfs.xfs /dev/disk/by-path/pci-0000\:00\:14.0-scsi-0\:0\:2\:0  -f -L docker-srg
mkdir -p /var/lib/docker
echo "LABEL=docker-srg /var/lib/docker xfs defaults 0 0" >> /etc/fstab

# Setup kubelet pvc storage
mkfs.xfs /dev/disk/by-path/pci-0000\:00\:14.0-scsi-0\:0\:3\:0  -f -L kube-srg
mkdir -p /var/lib/nfs-provisioner
echo "LABEL=kube-srg /var/lib/nfs-provisioner xfs defaults 0 0" >> /etc/fstab

# Mount Storage
mount -a

# Install requirements
apt-get update
apt-get install -y \
   docker.io \
   nfs-common

# Setup kubelet lib as shared mount
mkdir -p /var/lib/kublet
mount --bind /var/lib/kublet /var/lib/kublet
mount --make-shared /var/lib/kublet

# Run AIO container
docker run \
  -dt \
  --name=kubeadm-aio \
  --net=host \
  --security-opt=seccomp:unconfined \
  --cap-add=SYS_ADMIN \
  --tmpfs=/run \
  --tmpfs=/run/lock \
  --volume=/etc/machine-id:/etc/machine-id:ro \
  --volume=/home:/home:rw \
  --volume=/etc/kubernetes:/etc/kubernetes:rw \
  --volume=/sys/fs/cgroup:/sys/fs/cgroup:ro \
  --volume=/var/run/docker.sock:/run/docker.sock \
  --env KUBE_BIND_DEV=enp0s8 \
  --env KUBELET_CONTAINER=docker.io/port/kubeadm-aio:latest \
  docker.io/port/kubeadm-aio:latest
