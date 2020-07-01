# Capstone 2020

authors:
- Jake Lee
- Frank Lu
- Jacky Ho

## Navigating this repository

The `libs/` folder houses additional packages that can be installed onto your workstation.
 
<s>The `utils/` folder houses materials in the public safety domain that aim to provide you with additional context<s>
 Removed due to data confidentiality

## Note on data governance

A friendly reminder to not push raw SOP documents or identifying information to this repo. Feel free to edit the `.gitignore` file to further guard ourselves from accidentally doing so.


# Repository Structure

```
├── README.md         
├── app.py      # Web App (better interface)
├── app_obsolete.py   # Web App
├── src          # Where all the scripts are included
├── data         # Where all processed and created data are stored 
│  └── interim   # Where all processed and created data are stored
├── img          # Main image folder; flowchart images stored for web app 
├── doc          # Final Report & Presentation Slides
├── notebook     # ipynb files for EDA, Attempts, Approaches that have been conducted
│  └── entity_train  
│  └── model
├── libs         # Additional packages to install on remote Desktop
├── assets       # Javascript & css for front-end support
└── utils        # Materials from Ecomm team
```



# Reproducible data pipeline and user interface

In the root directory of the project:
- Run `python src/master_script.py` to:
  - parse SOP documents
  - preprocess sentences
  - cluster SOPs across event types and across situations
  - save results of clustering on disk

- Run `python app.py` to:
  - bring up the app at http://127.0.0.1:8686/
  - in order to have a smoother user experience, the app will do some heavy-lifting in the begining, so the deployment takes about 7 minutes





