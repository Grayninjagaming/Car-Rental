Requirements
Python version 3.9.4
additional requirements in requirements.txt


starting the project
step one you should enter the virtual environment source env/bin/activate in command line
step two you should run python3 app.py
from there all functions of the program are reachable on localhost:5000 from the browser


functionality at localhost:5000

This is the locations manager. In order for the program to work you will need at least 1 location.
To add a location type the name into the box next to the button. Note that it can not be blank or longer than 50 characters.
After it is added you should see it there along with the options to update, list cars, and delete

Update will take you to a page where you can put a new name for the location in case the business has moved. The original location will be in the box.
Delete will simply delete the location. In case you had several locations and one had to close. Note you can't delete a location that still has valid cars.
List cars will take you to http://localhost:5000/carList/#id which is a specialized version of the cars list that only shows cars for that location.
On this page you can do all the functionality of the normal cars page I will discuss below but after they submit it will take you to the main cars page.


functionality at localhost:5000/cars

This is the Cars Manager. It shares much of the design and function with the location manager but with more fields and everything is about making and listing cars.
To add a cae you must enter make, model, and the id of the location in that order in the boxes left to right top to bottom.
Make and model can not be blank and must be 50 characters or shorter and the location id must exist.

Update will take you to a another page with a form that is autofilled in case you made a mistake putting the car into the system.
Delete will remove the car in the case that it is no longer used by the business. You need to delete all rental records tied to the car before deleting it to not strand records.
List Rentals will take you to http://localhost:5000/cars/rentalList/#id which is a specialized version of the Rental Record manager that only lists rentals tied to the car.
Same functionality as the below page and will redirect to the main manager after you create, edit or delete a record.

functionality at localhost:5000/rentals

This is the Rental Record manager. It also is mainly the same as the other 2 managers.
The inputs are start date in the format YYYY-MM-DD, a duration in whole number days (Example 5 for 5 days), and then the ID of the car you want to use. 
If you have no preference of car you can put the id 0 in and it will find the first available car for that span of time.
If the car you choose has an overlap in its rentals it will give you an error message. If you picked 0 and all cars are unavailable it will tell you that no cars are available.
Edit will take you to a page that tells you the start date has a blank space for the new duration and the ID of the car it is using listed. Again 0 for wildcard pick of car.
This still checks to make sure that it is valid. If you pick a car and it can't fill the request there is an error and if you picked 0 and no cars are available it will also.
Delete will remove the rental record. In case you have a cancelation or are cleaning records that are too old for your business. Records don't rely on anything else being deleted.