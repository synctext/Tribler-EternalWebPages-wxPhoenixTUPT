# Tribler - TUPT fork

Tribler uses submodules, any ```git clone``` will have to use a ```--recursive``` flag.

## Dependencies

### Debian/Ubuntu/Mint
sudo apt-get install scons build-essential libevent-dev python-libtorrent python-apsw python-wxgtk2.8 python-netifaces python-m2crypto vlc python-yapsy python-imdbpy python-bs4

####wxPython 2.9.4.0
You will also need to install the development build of wxPython (2.9.4.0).
This, you will have to build yourself.

First download the wxPython 2.9.4.0 development build sources from http://www.wxPython.org/
(http://sourceforge.net/projects/wxpython/files/wxPython/2.9.4.0/wxPython-src-2.9.4.0.tar.bz2).

Now navigate to the top folder and execute ```.configure```.
You are likely to miss some packages, read the output and install 
any packages you may be missing (otherwise you will not get through
the next steps).

Still in the top folder: execute ```sudo make```.

Navigate to the ```./build``` folder and run ```sudo make install```.

Go back up to the top folder and navigate to ```./wxPython``` then execute:
```bash
sudo python2.7 build-wxpython.py --build_dir=../bld --wxpy_installdir=/usr --installdir=/usr 
```

## Running Tribler from this repository
### Unix
First clone the repository:

```bash
git clone --recursive  git@github.com:norberhuis/tribler.git
```

Then build swift and copy the binary where Tribler expects it to be:

```bash
cd  tribler/Tribler/SwiftEngine
scons #or scons -j8 if you have 8 cores on your machine.
cp swift ../..
cd ../..
```

Done!
Now you can run tribler by setting the wxPython path and executing the tribler.sh script on the root of the tree:
(Where ```./wxPython-src-2.9.4.0``` is your wxPython top folder)

```bash
PYTHONPATH=./wxPython-src-2.9.4.0/wxPython:"$PYTHONPATH"
export PYTHONPATH
LD_LIBRARY_PATH=/usr/local/lib:"$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH
./tribler.sh
```
