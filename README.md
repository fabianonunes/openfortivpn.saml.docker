# FortiClient VPN no Linux com autenticação de dois fatores

## Requisitos

- Docker
- Caso sua distribuição não utilize o Gnome, instale os seguintes pacotes:

    ```bash
    sudo apt install gir1.2-vte-2.91 gir1.2-webkit2-4.0
    ```

## Instalação

- Copie o arquivo `svpn` para algum local em disco (ou simplesmente clone este repositório).
- Crie o arquivo `~/.local/share/applications/vpn.desktop` com o seguinte conteúdo:
    > 🔴 Não se esqueça de ajustar o campo `Exec`

    ```ini
    # Ajuste o campo `Exec` abaixo com o caminho do arquivo svpn e com o host correto da VPN
    [Desktop Entry]
    Type=Application
    Name=openfortivpn
    Icon=network-vpn
    SingleMainWindow=true
    StartupWMClass=svpn
    Exec=/path/para/o/arquivo/svpn --host host_do_servidor_da_vpn.com.br
    ```

Depois de salvar o arquivo `.desktop`, o lançador aparecerá automaticamente no menu do Gnome, na guia Atividades e no dash de aplicativos.

E só! 🤓

## FAQ

<!-- markdownlint-disable no-inline-html -->
<details>
<summary>Por que utilizar uma imagem Docker?</summary>

O openfortivpn possui suporte à autenticação com cookies, mas ainda não
é possível passá-lo via linha de comando. A imagem Docker deste repositório
nada mais é do que a versão 1.17.3 com o patch que permite a passagem
do cookie de autenticação como parâmetro.
</details>

<details>
<summary>Por que utilizar --network=host?</summary>

Para a VPN funcionar, o `openfortivpn` cria uma interface `ppp` e adiciona
rotas IP estáticas à tabela de roteamento do kernel. Por exemplo, ele pode
rotear todas as conexões com destino a 172.16.0.0/12 para a interface `ppp0`.

Se não utilizássemos `--network=host`, essas rotas só funcionariam dentro do
próprio container.
</details>

<details>
<summary>
Por que o container precisa da capacidade <code>NET_ADMIN</code>?
</summary>

A _capability_ `NET_ADMIN` é um [requisito do driver `ppp`](https://git.io/Jys2R)
(é por esse motivo que o openfortivpn exige o `sudo` pra rodar fora do container).
</details>

<details>
<summary>Por que preciso montar o /etc/resolv.conf dentro do container?</summary>

Além de criar uma interface `ppp` e adicionar rotas IP, o `openfortivpn`
também precisa configurar o DNS para que o cliente possa acessar os domínios
da rede sob a VPN.
</details>

<details>
<summary>Como utilizar minha própria imagem?</summary>

Clone este repositório e construa a imagem:

```bash
docker build -t localhost/saml-vpn:latest .
```

No arquivo `.desktop` de inicialização, ajuste o campo `Exec` passando
o parâmetro `--image=localhost/saml-vpn:latest`.

</details>

<details>
<summary>
Como faço para executar um script antes e após a conexão ser estabelecida?
</summary>

Como o `pppd` está rodando dentro do container, os scripts em `/etc/pppd`
não serão executados no host. Uma alternativa é utilizar regras do `udev`:

```text
# /etc/udev/rules.d/99-meus-scripts-up-down.rules
ACTION=="add", SUBSYSTEM=="net", KERNEL=="ppp0", RUN+="/bin/touch /var/log/openfortivpn.start"
ACTION=="remove", SUBSYSTEM=="net", KERNEL=="ppp0", RUN+="/bin/touch /var/log/openfortivpn.end"
```

</details>
