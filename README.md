# Talky Trader
![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=100&size=13&pause=1000&color=027CF9&multiline=true&repeat=false&width=500&height=70&lines=CEX+%26+DEX+integration+with+multi+messaging+platform+support.;Place+order+for+CEFI+or+DEFI+exchanges+and+query+balance.;Deploy+it+via+docker+on+selfhosted+platform+or+PaaS.)

[![Docker Pulls](https://badgen.net/docker/pulls/mraniki/tt)](https://hub.docker.com/r/mraniki/tt)

[![Logo](https://i.imgur.io/Q7iDDyB_d.webp?maxwidth=640&shape=thumb&fidelity=medium)](https://github.com/mraniki/tt)
 </tr>
<details>
<summary><h2>Let's Start !</h2></summary>


 <h3>Install</h3>

1) Create your channel/room and your platform bot

    - Telegram via [Telegram @BotFather](https://core.telegram.org/bots/tutorial) and [create an API key](https://docs.telethon.dev/en/stable/basic/signing-in.html) 
    - Discord via [Discord Dev portal](https://discord.com/developers/docs/intro)
    - Matrix via [Matrix.org](https://turt2live.github.io/matrix-bot-sdk/index.html)

2) Get your

    - CEX API Keys supported by [CCXT](https://github.com/ccxt/ccxt) or
    - DEX wallet address and private key

3) Create your config [/app/settings.toml](src/example_settings.toml)

4) Deploy via:
    - docker `docker push mraniki/tt:latest` or `docker pull ghcr.io/mraniki/tt:latest`
    - locally `git clone https://github.com/mraniki/tt:main` && `pip install -r requirements.txt`

5) Start your container or if deployed locally use `python3 bot.py` to start

6) More details in [Wiki](https://github.com/mraniki/tt/wiki)


 <h3>Build status</h3>

[![✨Flow](https://github.com/mraniki/tt/actions/workflows/%E2%9C%A8Flow.yml/badge.svg)](https://github.com/mraniki/tt/actions/workflows/%E2%9C%A8Flow.yml)

![Alt](https://repobeats.axiom.co/api/embed/a2d03eaf66dab33c82d52170d8ebfb0c479590a9.svg "Repobeats analytics image")

 
<h3> Libraries </h3>

[![telethon](https://badgen.net/badge/icon/telethon?icon=telegram&label)](https://github.com/LonamiWebs/Telethon)
[![pycord](https://badgen.net/badge/icon/pycord/purple?icon=discord&label)](https://github.com/Pycord-Development/pycord)
[![simplematrixbotlib](https://badgen.net/badge/icon/simplematrixbotlib/grey?icon=medium&label)](https://codeberg.org/imbev/simplematrixbotlib)

[![python3.10](https://badgen.net/badge/icon/3.10/black?icon=pypi&label)](https://www.python.org/downloads/release/python-3100/)
[![ccxt](https://badgen.net/badge/icon/ccxt/black?icon=libraries&label)](https://github.com/ccxt/ccxt)
[![dxsp](https://badgen.net/badge/icon/dxsp?icon=pypi&label)](https://pypi.org/project/dxsp/)
[![findmyorder](https://badgen.net/badge/icon/findmyorder?icon=pypi&label)](https://pypi.org/project/findmyorder/)

[![apprise](https://badgen.net/badge/icon/apprise/black?icon=libraries&label)](https://github.com/caronc/apprise) [![FastAPI](https://badgen.net/badge/icon/fastapi/black?icon=libraries&label)](https://github.com/tiangolo/fastapi)
</details> 

<h3><a href="https://github.com/mraniki/tt/wiki/Screenshots">📷 More Screenshots</a></h3>
<a href="https://github.com/mraniki/tt/wiki/Screenshots">
<picture>
  <img alt="screenshot" src="https://user-images.githubusercontent.com/8766259/222953459-0aaf024b-4d7b-4a57-b31b-7cab08f3c0d3.png" width=194>
</picture></a>

<picture>
  <source srcset="https://user-images.githubusercontent.com/8766259/222953459-0aaf024b-4d7b-4a57-b31b-7cab08f3c0d3.png" media="(min-width: 194px)" />
</picture>

