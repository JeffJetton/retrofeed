# CONFIGURING YOUR PI

## Initial Steps
 
Set up your Pi with both ssh and wi-fi on and configured. You'll be making a lot of tweaks, so I'd recommend doing this with a fresh install on a new SD card. You can use the "gear" button (or type ctrl-shift-X) in Raspberry Pi Imager to pre-configure a lot of this at imaging time.

While having the full desktop is nice, you can get away with just installing the "Lite" version of the OS without it.

>Note that the changes outlined below generally won't take effect until your next restart (`sudo shutdown -r now` or `sudo reboot`).

### Composite Video

Your Pi will need to send video using the composite output. On most modern Pis, this uses the so-called "audio" port and requires a special cable or adapter. Pretty much any commercially-available cable with a tip-ring-ring-sleeve 1/8" (3.5mm) plug on one end and three 1/4" RCA plugs on the other should do the job. These can be found for under 10USD. If you get the kind that is designed for camcorders, they'll do the job, although they're wired a bit differently: The Pi's video signal will actually come out the "audio right" plug (which is usually red).
  
To switch on composite output, launch Raspi-Config from the command line:

`sudo raspi-config`

You can use an HDMI monitor to initially see the command line in order to do this, or `ssh` into your Pi to do it remotely.
  
Go to "Display Options" and enable composite there. Your Pi will not be able to do *both* composite and HDMI and will probably require any HDMI cables to be unplugged before you'll get anything out of the composite output.

### Boot to Command Line

If you installed the "Lite" version of the OS, you should already be booting to the command line. If not, go back into Raspi-Config, choose "System Option", then "Boot / Auto Login" to adjust things.

## Adjusting How the Terminal Looks

Your Pi should now correctly boot to a GUI-free command line, and you should (more or less) see it on your CRT. But it still looks like the stock Raspberry OS terminal, although perhaps in black and white (or amber, or green...) for those of us with monochrome monitors. Plus, it's very likely that the size is all wrong, with some sides cut off.

So a few more tweaks are in order. If the current screen display makes it difficult/impossible to make these changes directly on the Pi, you'll need to `ssh` into it from another computer.

>*Consider making a backup copy of these configuration files prior to modifying them!*

### Modify console-setup

Edit `/etc/default/console-setup` and assign one of the following sets of values to `FONTFACE` and `FONTSIZE`
 
* `VGA` (sizes  8x8,  8x14,  8x16,  16x28  and 16x32)
* `Terminus`  (sizes  6x12, 8x14, 8x16, 10x20, 12x24, 14x28
              and 16x32)
* `TerminusBold` (sizes 8x14, 8x16, 10x20, 12x24,  14x28 and  16x32)
* `TerminusBoldVGA`  (sizes  8x14 and 8x16)
* `Fixed` (sizes  8x13,  8x14,  8x15,  8x16   and   8x18). 
              
I think `Fixed` at `8x8` looks the most appropriately retro, but feel free to try the others.

To view your font changes without rebooting the entire system, use:

`sudo /etc/init.d/console-setup.sh restart`


### Modify config.txt

Edit `/boot/config.txt` and add the lines below somewhere in it.

* The values for overscan_left/right/etc are just what worked for me. You'll probably wind up using different values, depending on your monitor. It can take a bit of experimentation. Positive numbers increase the size of the black border on the corresponding side, while negative numbers reduce it.
* For PAL monitors, change the value for `sdtv_mode` to 2
* For color monitors (if you want to use color), omit `sdtv_disable_colorburst=1` or set it to 0

```
overscan_left=34
overscan_right=30
overscan_top=-24
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

You can also play around with specifying particular framebuffer values, for example:

```
framebuffer_height=192
framebuffer_width=320
```
Setting them very low, as above, will force the default terminal to display fewer lines and fewer characters per line, for a nice, retro look!

### Modify cmdline.txt

Edit `/boot/cmdline.txt` and add `logo.nologo` on the **end**. This will disable the "four raspberries" graphic at the top of the screen.

The existing contents of your `cmdline.txt` may differ, but here's what mine looked like after the edit, as an example:

```
console=serial0,115200 console=tty1 root=PARTUUID=daaff45b-02 rootfstype=ext4 fsck.repair=yes rootwait logo.nologo
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


## Getting RetroFeed to Run at Boot

### Transferring Files

If you've downloaded the Python files directly from your Pi, you won't need this step. But if they're on your main computer, transfer them over using `scp`. Here's an example that assumes:

* Your Pi's hostname is the default `raspberrypi`
* You have a directory in your user directory called `retrofeed`
* You're in the retrofeed directory on the computer you're transferring from, with all the `.py` python files in it

`scp  *.py  pi@raspberrypi.local:~/retrofeed`

Obviously, you'll need to adjust accordingly if your situation is different.  The `.local` may or may not be necessary, depending on how you have it set up.

### Modify init.d

>There are several ways to get something to launch at boot, and this is just one. Feel free to use a different method if you have a favorite.


**TODO:** *Finish this part*



