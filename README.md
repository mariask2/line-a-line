# line-a-line

Since there are submodules, after you have done git clone, you need to run:
git submodule update --init --recursive

Code for word alignment 

The following dependencies have to be installed:

(Given the existence of a Miniconda installation https://conda.io/en/latest/miniconda.html, it can be done as follows),

conda create --name aligner

source activate aligner

---

conda install python=3.8.1

conda install nltk

conda install flask

pip install -U flask-cors

conda install numpy
conda install setuptools
conda install Cython
conda install -c anaconda gcc

conda install -c anaconda mongodb
conda install -c anaconda pymongo
conda install -c anaconda setuptools

To get the efmaral installation to work on mac with Mojave, you need to do:
open /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg

(The "/usr/include" folder does not seem to be there by default, so that's why. See more in:
https://www.howtobuildsoftware.com/index.php/how-do/cPv/xcode-osx-gcc-fatal-error-limitsh-no-such-file-or-directory
https://developpaper.com/how-to-solve-pip-install-twisted-error-limits-h-no-such-file-or-directory/
https://stackoverflow.com/questions/52509602/cant-compile-c-program-on-a-mac-after-upgrade-to-mojave
)

To get the efmaral code to work, you need to go to the efmaral folder and write:
python setup.py install

To run the code you need a mongdodb server to be running.

To achieve that, create the directory where the data is to be saved, e.g., “databasedata/db
Then start the server giving that directory as a parameter:
mongod --dbpath databasedata/db/
(mongodb listenes as default on port 27017. Currently that port is assumed to be the one used)

You also need a file with the approved keys in the folder, named 'approved_keys.txt'

Aligned fasttext spaces can be found at:
https://github.com/facebookresearch/MUSE

Current workflow:

1) Use the 'run_extract_and_convert' function from 'extract_tmx_to_fastalign_format.py' to extract data from tmx-format files, and produce pre-alignments
That is, a Python file specific for the tmx file has to be written. (The plan is to simplify this in the future.)
See, for instance, the script 'run_extract_data_labour_market_social_security_de_sv_fastalign_format.py' for an example of how it is done.

2) Run the server by python annotate_align_api.py 5000
Cut and paste 'http://127.0.0.1:5000/line-a-line/' into the web browser

( 3) For debugging, the server code can be tested by running 'python test_annotate_align_api.py 5000')




