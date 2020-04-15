# swaylock-ecb
Swaylock with multi monitor support and ecb image encryption

## General
Code stolen and merged from i3lock-fancy-multimonitor and swaylock-fancy.

- For every connected monitor, a screenshot is taken using grim.
- The screenshot is then encrypted using python
- The resulting encrypted image is pixelated using imagemagick and a lock icon is added

## Dependencies
- Python3
- grim 
- imagemagick
- jq


## Installation

- clone
- place anywhere
- assign hotkey via sway config file