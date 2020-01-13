
## Troubleshooting 

### MAC OSX

#### PyAudio

If an error similar to `portaudio.h file not found` appears, then follow these steps:

First, install portaudio if you haven't already.

```sh
brew install portaudio
```

Then, inside the virtual environment do the following:

```sh
pip install --global-option='build_ext' --global-option='-I/usr/local/include' --global-option='-L/usr/local/lib' pyaudio
```

#### PocketSphinx 

Having started the virtual environment, go to the `build/` folder or any of your choice and follow these steps.

```sh
git clone --recursive https://github.com/bambocher/pocketsphinx-python
cd pocketsphinx-python
```

Edit `pocketsphinx-python/deps/sphinxbase/src/libsphinxad/ad_openal.c`
And change
```cpp
#include <al.h>
#include <alc.h>
```

to

```cpp
#include <OpenAL/al.h>
#include <OpenAL/alc.h>
```

Ultimately, run `python setup.py install`.

#### Pattern

Pattern has some issues when run in Python 3.7+. These are mainly due to changes made in generator behavior. From the [Python Docs](https://docs.python.org/3/whatsnew/3.7.html):
> PEP 479 is enabled for all code in Python 3.7, meaning that StopIteration exceptions raised directly or indirectly in coroutines and generators are transformed into RuntimeError exceptions. (Contributed by Yury Selivanov in bpo-32670.)

To fix this, we simply have to change all the `raise StopIteration` expressions to `return`.

Having started the virtual environment, go to the `build/` folder or any of your choice and follow these steps.

```sh

git clone https://github.com/clips/pattern.git
cd pattern

# To see files to change
grep -rnw '.' -e 'raise StopIteration'

# You can open all relevant files shown in previous step and change them manually or
# execute this script (only tested on MAC OS)
find . -type f -name '*.py' -exec sed -i '' -e 's/raise StopIteration/return/g' {} +

# for Linux
find . -type f -name '*.py' -exec sed -i 's/raise StopIteration/return/g' {} \;

```

