PicoScope 7 Stable
Installation

PicoScope is distributed via our online repositories. For operating system-specific instructions, please choose your distribution.
Ubuntu 24.04 LTS and Ubuntu 22.04 LTS

    Import public key (only once, no need to repeat)

    sudo bash -c 'wget -O- https://labs.picotech.com/Release.gpg.key | gpg --dearmor > /usr/share/keyrings/picotech-archive-keyring.gpg'

    Configure your system repository

    sudo bash -c 'echo "deb [signed-by=/usr/share/keyrings/picotech-archive-keyring.gpg] https://labs.picotech.com/picoscope7/debian/ picoscope main" >/etc/apt/sources.list.d/picoscope7.list'

    Update package manager cache

    sudo apt-get update

    Install PicoScope

    sudo apt-get install picoscope


