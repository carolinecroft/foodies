# FOODIES 

Food-centered dating app that helps match people and provide them with a first date restaurant the pair will love!

## Project Setup 

These instructions were written using macOS, so you might have to adjust them as needed. 

### 1. Find the repository 

if the repository is already cloned: 
 
cd foodies 

if you have NOT cloned the repository yet:

git clone https://github.com/carolinecroft/foodies.git 
cd foodies

### 2. Create a new branch 

before making changes, make sure main is up to date and create a feature branch:

git switch main 
git pull 
git switch -c feature/your-feature-name

**See the Git Workflow section below for more information**

### 3. Create a virtual environment 

python3 -m venv .venv

### 4. Activate the virtual environment 

source .venv/bin/activate 

### 5. Install dependencies

update pip if necessary using: 

pip install --upgrade pip

then install the project dependencies:

pip install -r requirements.txt

### 6. Apply database migrations 

python manage.py migrate

### 7. Run the Django development server 

python manage.py runserver 


## Git Workflow 

### 1. DO NOT WORK DIRECTLY ON MAIN 

before starting a task always create or access your own branch:

git switch main 
git pull 
git switch -c feature/your-feature-name

ex. my working branch was called feature/django-setup

### 2. Commit work regularly 

git add . 
git commit -m "describe your changes"

### 3. Push your branch 

the first time you push your branch:

git push -u origin feature/your-feature-name

after that, you can usually use:

git push 

### 4. Open a Pull Request

On GitHub:

- Open the Foodies repository.
- Find the banner for your recently pushed branch.
- Click Compare & pull request.
- Make sure:
    - Base branch is main
    - Compare branch is your feature branch
- Add a short title describing the feature.
- Add a brief description of what you changed.
- Click Create pull request.

### 5. Request a teammate review 

On the Pull Request page:

- Find the Reviewers section on the right side.
- Select at least one teammate.
- Wait for the teammate to review the changes.

The reviewer should:

- Open the Pull Request.
- Look through the changed files.
- Click Review changes.
- Select Approve.
- Click Submit review.

### 6. Merge the Pull Request 

After the Pull Request has been approved:

- Click Merge pull request.
- Click Confirm merge.

The changes are now part of main.

### 7. Update your local main 

After pull request is merged, everyone should update their local copy:

git switch main 
git pull 

