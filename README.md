# DT-CMR-Tools
Data analysis tool suite for in vivo diffusion tensor cardiac MR(DT-CMR). 

# Installation instructions
## Python
1. Clone repository
2. Create venv:

``` 
# Open terminal (for M1 macs with Rosetta 2 for now)
# (Use non-homebrew python for M1 macs with Rosetta 2 for now; mine was in /usr/bin/python3) to create virtual environment
/usr/bin/python3 -m venv env

source env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

## macOS
1. Edit command ```DT-CMR_RAT_app.command``` to the correct path and copy it to the Applications folder.
2. Replace the file icon with the icon provided.