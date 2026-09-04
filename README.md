IP Radar Scanner 📡
Este projeto é um monitor de rede local que utiliza uma interface inspirada em radares militares para identificar dispositivos conectados e classificar o nível de segurança da rede.

📋 Funcionalidades
Varredura em Tempo Real: Identifica todos os dispositivos (IPs) conectados à rede local.

White List (IPs Permitidos): Permite configurar uma lista de dispositivos conhecidos.

Interface de Radar: Exibição visual circular onde:

🟢 Verde: Dispositivos autorizados (White List).

🔴 Vermelho: Dispositivos desconhecidos/potenciais intrusos.

Alerta Visual: Identificação imediata de quem está "sugando" ou invadindo sua internet.

🛠️ Tecnologias
Python / Java (Ajuste conforme sua escolha).

Bibliotecas de Redes: Scapy ou bibliotecas de Socket.

Interface Gráfica: Pygame ou Tkinter para a renderização do radar.

🚀 Como usar
Edite o arquivo accepted_ips.txt com os endereços da sua casa.

Execute o script principal:

Bash
python radar_app.py
