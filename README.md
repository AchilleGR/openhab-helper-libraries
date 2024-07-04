# OpenHAB Helper Libraries

This is a fork of tamtam1111's fork of Ivan's Helper Libraries. The directory watcher has been repaired, so at least my jsr223 scripts are now hot-reloading again.

Included in this repo is a community library that allows one to define devices as groups of properties and behaviors, and have it translated to a set of item names. If the items exist, the implementation kicks in automatically.

This library is mostly included as it constitutes the majority of my openhab configuration, so this makes it easy to keep defined in code.

The original community libraries, script examples, and docs are included, but are not being maintained at the moment.

## Install

```bash
wget 'https://github.com/MiningMarsh/openhab-helper-libraries/archive/main.zip'
unzip main.zip
cp -r main/* /etc/openhab/conf/
```
