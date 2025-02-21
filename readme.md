sudo apt update && sudo apt install openvpn -y

mkdir -p ~/nordvpn && cd ~/nordvpn
wget https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip
unzip ovpn.zip


mkdir -p ~/nordvpn/ovpn_udp
mv ovpn_udp/* ~/nordvpn/ovpn_udp/

# Create auth.txt for credentials
echo "2CngcjSFLNPCZ9KoSQwWbz9a" > ~/nordvpn/auth.txt
echo "zksgyu4T4NvFx1MA5D59Ye1L" >> ~/nordvpn/auth.txt

