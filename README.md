in the project directory create a virtual environment (recommended) and 
then run "pip install -r requirements.txt"
after that only run the app.py to run the app

optional checks:
* weapon scraping contains the script used to acquire teh dataset and then was labeled and preprocessed on roboflow, you can edit the names of the weapon 
  you want to scrape by editing the list of names
* rough work contains the notebook that was used before i was acquainted with git (I was living uder a rock), in this file i used to create a new cell every time i made a change.
* model file was used to train the model on colab by uploading the dataset on google drive
* app.ipynb is nothing but the same as app.py but in notebook where i did my early work
* best.pt these are all the models that were trained you can use any but i recommend use best4.pt with conf>0.7 for live detection for decent performance, in the last commit
  I only enabled alarm for pistol, revolver and assault rifle, you can edit that to your liking

the app was developed on mac throughout but was tested on windows in the middle stages, though the last version was not tested on windows but should work.
  lastly if you have any issue running the project on your device i would be happy to help
  
