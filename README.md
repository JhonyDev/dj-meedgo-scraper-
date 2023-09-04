# Main Branch is in CI/CD. DO NOT PUSH DIRECTLY TO MAIN BRANCH. 
* git clone repository_name
* open terminal in project folder
* Run the commands below

`
pip install -r requirements.txt
py manage.py makemigrations
py manage.py migrate
py manage.py runserver
`
