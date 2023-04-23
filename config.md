# Configuring the Raspbery Pi to be a Retro Terminal

This is actually a fun use of the Pi whether you run RetroFeed on it or not. After following these instructions, you'll wind up with a Pi that...

* Boots directly to a full-screen command line
* Displays that command line in a simplied, lo-res, "retro" style
* Uses, ideally, the composite video output connected to a CRT display. You're free, of course, to use a flatscreen monitor that has composite input, or--if you skip the composite steps--use the HDMI output with or without a VGA convertor, etc.

This is not an exact science. Be prepared to do a **lot** of fiddling and tweaking in order to get things looking right on your own CRT.

## Imaging the SD Card
 
You'll be making a lot of tweaks to the base Rasperry Pi OS, so I'd recommend doing this with a fresh install on a dedicated SD card that you can swap out with the card containing your regular, day-to-day OS install.

Launch **Raspberry Pi Imager** and write to a new card with these options (most are behind the button with a "gear" icon that shows up once you pick an OS):

* Operating System: Raspberry Pi OS (other) -> **Raspberry Pi OS Lite** (32-bit)
    * Really just about any Rasperry Pi OS will do, but since we won't be using the windowing system, we might as well leave it out and go with "Lite"
    * The 64-bit version might work too, but we don't really need it
* Set a hostname. You'll use this hostname to log onto the Pi remotely via SSH later.
* Enable SSH with password authentication
    * If you're familiar with public-key authentication and want to use that instead, be my guest.
* Select "Set username and password" and fill those in. You'll be using these along with the hostname to log on remotely, so remember what you pick.
* Configure the wireless LAN with your local wi-fi network name and password.  Set the country to your country code.
* Set your locale settings appropriately

Click "Save", make sure your CD card is selected under "Storage", then choose "Write" and wait.

When it's ready, pop it into your Pi and boot it up. The first boot may take awhile, and you might not see anything on a connected monitor when it's done.

## Connecting via SSH

Once the OS is installed and booted up, you may or may not be able to execute terminal commands directly on the Pi. (Maybe if you have an HDMI monitor attached, but probably not if you've already hooked up a composite monitor.) In any case, it's useful to log in from another computer that's on the same network.

Launch your favorite terminal program on the remote computer and enter:

`ssh username@hostname.local`

With "username" and "hostname" being replaced with whatever you entered when configuring the SD card. (If this doesn't work, try it without `.local` on the end.)

When prompted for a password, use the password you picked earlier.

If asked some other questions during your first SSH connection to the Pi, answer "Y" or "Yes".

## Getting Up-to-Date

However you're getting to the command line, once you're there, make sure you're as up-to-date as you can be:

```
sudo apt update
sudo apt upgrade
```

>Note that the changes outlined below generally won't take effect until your next restart (`sudo shutdown -r now` or `sudo reboot`).

## Composite Video

Your Pi will need to send video using the composite output. On most modern Pis, this uses the so-called "audio" port and requires a special cable or adapter. Pretty much any commercially-available cable with a tip-ring-ring-sleeve 1/8" (3.5mm) plug on one end and three 1/4" RCA plugs on the other should do the job. These can be found for under 10USD. If you get the kind that is designed for camcorders, they'll do the job, although they're wired a bit differently: The Pi's video signal will actually come out the "audio right" plug (which is usually red).
  
To switch on composite output, launch Raspi-Config from the command line:

`sudo raspi-config`

Go to "Display Options" and enable composite there. Your Pi will not be able to do *both* composite and HDMI and will probably require any HDMI cables to be unplugged before you'll get anything out of the composite output.

### Boot to Command Line

If you installed the "Lite" version of the OS, you should already be booting to the command line. If not, or if you forget to set auto login, go back into Raspi-Config, choose "System Option", then "Boot / Auto Login" to adjust things.

## Adjusting How the Terminal Looks

Your Pi should now correctly boot to a GUI-free command line, and you should (more or less) see it on your CRT. But it still looks like the stock Raspberry OS terminal, although perhaps in black and white (or amber, or green...) for those of us with monochrome monitors. Plus, it's very likely that the size is all wrong, with some sides cut off.

So a few more tweaks are in order. As before, if the current screen display makes it difficult/impossible to make these changes directly on the Pi, just `ssh` into it from another computer.

>*Consider making a backup copy of these configuration files prior to modifying them*

### Modify console-setup

Using your favorite text editor to modify the console-setup file used by the terminal program. Here's an example using nano:

`sudo nano /etc/default/console-setup`

Assign one of the following sets of values to `FONTFACE` and `FONTSIZE`
 
* `VGA` (sizes  8x8,  8x14,  8x16,  16x28  and 16x32)
* `Terminus`  (sizes  6x12, 8x14, 8x16, 10x20, 12x24, 14x28
              and 16x32)
* `TerminusBold` (sizes 8x14, 8x16, 10x20, 12x24,  14x28 and  16x32)
* `TerminusBoldVGA`  (sizes  8x14 and 8x16)
* `Fixed` (sizes  8x13,  8x14,  8x15,  8x16   and   8x18). 

I think `Terminus` at `6x12` or `8x14` and `Fixed` at `8x13` look appropriately retro, but feel free to try the others. Example:

```
FONTFACE="Terminus"
FONTSIZE="8x14"
```

In nano, type ctrl+O then return to save, and ctrl+X to exit.

To view your font changes without rebooting the entire system, use:

`sudo /etc/init.d/console-setup.sh restart`

Or reboot using `sudo shutdown -r now` or `sudo reboot`

### Modify config.txt

Edit `/boot/config.txt` (don't forget to `sudo`) and add/modify/uncomment the lines below somewhere in it.

* The values for overscan_left/right/etc are just what worked for me. You'll probably wind up using different values, depending on your monitor. It can take a bit of experimentation. Positive numbers increase the size of the black border on the corresponding side, while negative numbers reduce it.
* For PAL monitors, change the value for `sdtv_mode` to 2
* For color monitors (if you want to use color), omit `sdtv_disable_colorburst=1` or set it to 0
* [Full details on this file and its various options](https://www.raspberrypi.com/documentation/computers/config_txt.html)

```
overscan_left=34
overscan_right=30
overscan_top=-48
overscan_bottom=-10

sdtv_mode=0
sdtv_aspect=1
sdtv_disable_colorburst=1
enable_tvout=1

disable_overscan=0
overscan_scale=1
```

If you find that your overscan settings only seem to work at the beginning of the boot process, and get ignored about halfway though, use a `#` to comment out the line that enables the VC4 graphics driver:

```
#dtoverlay=vc4-kms-v3d
```
(This line may have additional text after it, like `,composite` or something. Comment it out anyway.)

The **framebuffer** size determines the number of virtual "pixels" used for the overall screen image, which in turn affects how many rows and columns of characters wind up getting displayed.

To start with at least, specify a width that is the width of the font you chose above multiplied by the number of columns you want. Do the same for font height and number of rows. Here, I'm using an 8x14 font and shooting for 24 rows of 40 columns, giving me a width of 8x40 and height of 14x24:

```
framebuffer_width=320
framebuffer_height=336
```


### Modify cmdline.txt

Edit `/boot/cmdline.txt` and add `logo.nologo` on the **end**. This will disable the "raspberries" graphic at the top of the screen.

The existing contents of your `cmdline.txt` may differ, but here's what mine looked like after the edit, as an example:

```
console=serial0,115200 console=tty1 root=PARTUUID=deadbeef-42 rootfstype=ext4 fsck.repair=yes rootwait logo.nologo
```

*Everything in this file has to be on one line, so don't add any returns.*

### Modify .bashrc

Edit `~/.bashrc` to adjust your shell environment.

Since there are so few characters per line now, you might prefer a shorter default prompt. Either find the line that sets the `PS1` environment variable and edit it, or just add a new line near the end of the file that reassigns it to whatever you like.

For example, this will just show the path and not the username and host. It also changes the `$` at the end to a more retro `>`

`PS1='\w> '`


If your monitor is monochrome...

* Add a line to let the shell know
 * `TERM=xterm-mono`
 * This should go near the top of the file, before any existing part of the script checks the `$TERM` variable
* If this line is in the file, ***comment it out:***
 * `force_color_prompt=yes`
* Find the section that checks for color support and aliases `ls` and `grep` to always use color. Either comment those lines out, or explicitly set the color to "none" like so:
 * `alias ls='ls --color=none'`


## Running RetroFeed

### Transferring Files

If you've downloaded the Python files directly onto your Pi, from the Pi, you won't need this step. But if they're on your main computer, transfer them over using `scp`. Here's an example that assumes:

* Your Pi's hostname is the default `raspberrypi`
* You have a directory in your user directory called `retrofeed`
* You're in the retrofeed directory on the computer you're transferring from, with all the `.py` python files in it

`scp  *.py  pi@raspberrypi.local:~/retrofeed`

Obviously, you'll need to adjust accordingly if your situation is different.  The `.local` may or may not be necessary, depending on how you have it set up.

### Install Required Package

On the Pi, either directly or via ssh (skip the first two lines if you've just done them in the earlier steps above):

```
sudo apt update
sudo apt upgrade
sudo apt install python3-pip

pip install beautifulsoup4
```

### Run it!

Assuming you're in the same directory as `retrofeed.py`:

```
python retrofeed.py
```
>If you're trying out the program on a Mac, you'll probably need to use `python3` instead of `python`.




