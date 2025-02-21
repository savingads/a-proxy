sudo apt update && sudo apt install openvpn -y

mkdir -p ~/nordvpn && cd ~/nordvpn
wget https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip
unzip ovpn.zip


mkdir -p ~/nordvpn/ovpn_udp
mv ovpn_udp/* ~/nordvpn/ovpn_udp/

