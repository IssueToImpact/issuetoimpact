# issuetoimpact

### Setting up and using virtual environments and requirements.txt

#### Virtual environments

1. install 'virtualenv'

`pip3 install virtualenv`

2. set up a virtual environment

Inside the project, run:\
`python3 -m venv issuetoimpact_venv`

3. then to work inside the environment, run:

`source issuetoimpact_venv/bin/activate`

#### Installing packages within the virtual environment

Make sure you are inside the virtualenv\
(prompt should be something like:
`(issuetoimpact_venv) <computer_name>:issuetoimpact <username>$`)

And then just install packages as usual\
e.g. `pip3 install pandas`

#### requirements.txt file

To install all packages listed in requirements.txt:

`pip3 install -r requirements.txt`

To update the requirements file when you've installed new packages:

`pip3 freeze > requirement.txt`
