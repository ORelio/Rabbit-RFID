![Rabbit RFID](images/rabbit-rfid-logo.png)

_This tool is an example of how the [Rabbit Home](http://github.com/ORelio/Rabbit-Home) framework can be reused to make other projects. It's not maintained actively, but contributions are welcome._

Rabbit RFID is a custom service for [nabaztag](https://en.wikipedia.org/wiki/Nabaztag) rabbits retrofitted with a [tag:tag:tag](https://www.tagtagtag.fr/) board running [pynab](https://github.com/nabaztag2018/pynab). It implement tag support for newer tags such as Mifare Classic (Vigik) using the [new NFC reader](https://www.journaldulapin.com/2022/06/30/nabaztag-nfc/), without touching pynab's source code.

Each tag can be associated with an action or webhook set in configuration.

## Installing

These instructions are for advanced users with sufficient knowledge of Linux command-line.

1. Enable SSH on your tag:tag:tag board:
    * Remove the SD card and insert it on your computer
    * Create a blank file named `ssh` without file extension
    * Reinsert the SD card into your rabbit, and power it on
    * You can now access using `ssh pi@rab.bit.ip.addr` with password `raspberry`
    * Change password with the `passwd` command (recommended)
2. Upload the `rabbit-rfid` folder to your home directory:
    * `/home/pi/rabbit-rfid` should contain `rabbit-rfid.py`
4. Enable lingering services for the pi account:
    * `sudo loginctl enable-linger pi`
5. Create the `rabbitrfid` service: 
    * `mkdir -p ~/.config/systemd/user`
    * `editor ~/.config/systemd/user/rabbitrfid.service`
    * Paste the following:
```ini
[Unit]
Description=Rabbit RFID
After=local-fs.target network.target systemd-tmpfiles-setup.service

[Service]
ExecStart=/usr/bin/env python3 /home/pi/rabbit-rfid/rabbit-rfid.py
Restart=always
Type=simple

[Install]
WantedBy=default.target
```

6. Start service:
```
systemctl --user unmask rabbitrfid
systemctl --user enable rabbitrfid
systemctl --user restart rabbitrfid
systemctl --user status rabbitrfid
```

## Configuring

Go to `config` folder and edit `rfid.ini` to map actions to your tags.

After changing configuration files, restart the service to apply your changes:
```
systemctl --user restart rabbitrfid
```

## Enrolling more rabbits

You can skip installing the service on your other rabbits by enrolling the other rabbits instead:

1. Edit `config/rabbits.ini` and add the additional rabbit
2. Add direct SSH access from the rabbit running the service to the other rabbit:

```bash
NABAZTAGIP=192.168.1.XXX # Set your other rabbit IP here. The rabbit must have a static IP, see your router settings.
if [ ! -f ~/.ssh/id_rsa.pub ]; then ssh-keygen -b 4096; fi
PUBKEY=$(cat ~/.ssh/id_rsa.pub)
ssh pi@${NABAZTAGIP} "if [ ! -d ~/.ssh ]; then mkdir ~/.ssh; fi; echo '${PUBKEY}' >> ~/.ssh/authorized_keys; echo added ssh key."
ssh pi@${NABAZTAGIP} # Should get a shell on your rabbit without typing a password
```

When doing so, scanning the tag on the other rabbit will run the same action as configured on your main rabbit. If you prefer having different action for different rabbits, install the service independently on each rabbit.

## License

The [Rabbit Home](http://github.com/ORelio/Rabbit-Home) framework, including this example project, is provided under [CDDL-1.0](http://opensource.org/licenses/CDDL-1.0) ([Why?](http://qstuff.blogspot.fr/2007/04/why-cddl.html)).

Basically, you can use it or its source for any project, free or commercial, but if you improve it or fix issues,
the license requires you to contribute back by submitting a pull request with your improved version of the code.
Also, credit must be given to the original project, and license notices may not be removed from the code.
