Install docker
- remove old versions
sudo apt-get remove docker docker-engine docker.io containerd runc

- setup repository
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg lsb-release

-add docker GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu   $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
-install docker
 sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
-verify that docker is installed correctly
 sudo docker run hello-world
Docker as a non-root user
-add group
 sudo groupadd docker
 sudo usermod -aG docker $USER
-reload group configs
 newgrp docker 
-verify command without sudo
 docker run hello-world
-setup on boot
 sudo systemctl enable docker.service
 sudo systemctl enable containerd.service
- disable setup on boot
 sudo systemctl disable docker.service
 sudo systemctl disable containerd.service



