from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carRental.db'
db = SQLAlchemy(app)

#this class mainly exists in case I take on the extra part
class location(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    city = db.Column(db.String(50), nullable=False)
    addresses = db.relationship('car', backref='location', lazy=True)

    def __repr__(self):
        return '<Location %r>' % self.id


#class defined for a car 
class car(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    addresses = db.relationship('record', backref='car', lazy=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'),
        nullable=False)
    
    def testConflict(self,startDate, endDate):
        conflict = False
        counter = 0;

        while counter < len(self.addresses) and not conflict:
            entry = self.addresses[counter]
            if((entry.startDT <= startDate and entry.endDT > startDate) or (entry.startDT > startDate and entry.startDT < endDate)):
                conflict = True #the above logic means that the dates overlap for the records
            counter += 1
        return conflict #if we exit the loop without the if statement going there won't be a conflict.
    def __repr__(self):
        return '<Car C%r>' % self.id

#class defined for a rental record
class record(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    startDT = db.Column(db.DateTime, default = datetime.now(timezone.utc))
    endDT = db.Column(db.DateTime, default = datetime.now(timezone.utc))
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'),
        nullable=False)
    def __repr__(self):
        return '<Rental Record %r>' % self.id
    






#locations main page
@app.route('/', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        if request.form['location'] == "":
            return "Location name must not be blank"
        location_name = request.form['location']
        new_location = location(city = location_name)

        try:
            db.session.add(new_location)
            db.session.commit()
            return redirect('/')
        except:
            return 'An error has occured with adding the location'
    else:
        locations = location.query.order_by(location.id).all()
        return render_template('index.html', locations = locations)

#locations delete
@app.route('/delete/<int:id>')
def locDelete(id):
    delete_location = location.query.get_or_404(id)
    
    try:
        db.session.delete(delete_location)
        db.session.commit()
        return redirect('/')
    except:
        return 'An error ocurred deleting that location.'

#location update functionality
@app.route('/update/<int:id>', methods=['POST', 'GET'])
def locUpdate(id):
    edit_location = location.query.get_or_404(id) 
    if request.method == 'POST':
        if request.form['location'] == "":
            return "Location name must not be blank"
        edit_location.city = request.form['location']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'Error updating location'
    else:
        return render_template('locUpdate.html', location = edit_location)   

#location list all cars
@app.route('/carList/<int:id>', methods=['GET']) 
def locCarList(id):
    cars_location = location.query.get_or_404(id)
    return render_template('cars.html', cars = cars_location.addresses)  







#main page for all cars
@app.route('/cars', methods=['POST','GET'])
def cars():
    if request.method == 'POST':
        location1 = db.session.get(location,request.form['location'])
        if(request.form['make'] == ""):
            return "Make must not be an empty string."
        if(request.form['model'] == ""):
            return "Model must not be an empty string"
        
        if location1 == None:
            return "Invalid location no location with that ID"
        
        car_make = request.form['make']
        car_model = request.form['model']
        car_location = request.form['location']
        new_car = car(make = car_make, model=car_model, location_id = car_location)

        try:
            db.session.add(new_car)
            db.session.commit()
            return redirect('/cars')
        except:
            return 'An error has occured with adding the location'
    else:
        cars = car.query.order_by(car.id).all()
        return render_template('cars.html', cars = cars)


#car delete
@app.route('/cars/delete/<int:id>')
def carDelete(id):
    delete_car = car.query.get_or_404(id)
    
    try:
        db.session.delete(delete_car)
        db.session.commit()
        return redirect('/cars')
    except:
        return 'An error ocurred deleting that car. Likely you need to remove related rental records.'
    
#car update functionality
@app.route('/cars/update/<int:id>', methods=['POST', 'GET'])
def carUpdate(id):
    edit_car = car.query.get_or_404(id) 
    if request.method == 'POST':
        if(request.form['make'] == ""):
            return "Make must not be an empty string."
        if(request.form['model'] == ""):
            return "Model must not be an empty string"
        location1 = db.session.get(location,request.form['location'])
        if location1 == None:
            return "Invalid location no location with that ID"
        edit_car.make = request.form['make']
        edit_car.model = request.form['model']
        edit_car.location_id = request.form['location']
        try:
            db.session.commit()
            return redirect('/cars')
        except:
            return 'Error updating car'
    else:
        return render_template('carUpdate.html', car = edit_car) 

#List all rental records for a car
@app.route('/cars/rentalList/<int:id>', methods=['GET']) 
def carRentList(id):
    records_car = car.query.get_or_404(id)
    return render_template('rentals.html', rentals = records_car.addresses)  





#main page for all rental records
@app.route('/rentals', methods=['POST','GET'])
def rentals():
    if request.method == 'POST':
        date_format = '%Y-%m-%d'
        rental_start = datetime.strptime(request.form['startDate'],date_format) #if the format is wrong this will error on its own on the page
        
        if(int(request.form['duration']) <= 0): #make sure the duration is a postive int
            return "Duration must be 1 or more"
        else:
            rental_end = rental_start +timedelta(days=int(request.form['duration']))


        
        thatCar = db.session.get(car,request.form['car'] ) #grabs the car to make sure it exists

        
        if int(request.form['car']) == 0: #this is the case that you don't want to rent a specific car and instead want any car
            cars = car.query.order_by(car.id).all()
            counter = 0;
            conflict = True;
            while counter < len(cars) and conflict:
                conflict = cars[counter].testConflict(rental_start,rental_end)
                if(not conflict):
                    rental_car = cars[counter].id
                counter += 1;
            if conflict:
                return "No cars available for this rental. You may need to buy more cars to fill demand"

        elif thatCar == None: #this case you wanted a specifc car but it doesn't exist
            return "Car ID not registered in the system."
        

        else: #this case you want a specifc car and it does exist
            if thatCar.testConflict(rental_start, rental_end):
                return "There is an overlap in dates with another record. This car can't fill the demand."
            else:    
                rental_car = request.form['car']


        new_record = record(startDT = rental_start, endDT=rental_end, car_id = rental_car)

        try:
            db.session.add(new_record)
            db.session.commit()
            return redirect('/rentals')
        except:
            return 'An error has occured with adding the rental record'
    else:
        rentals = record.query.order_by(record.id).all()
        return render_template('rentals.html', rentals = rentals)


#record delete
@app.route('/rentals/delete/<int:id>')
def rentalDelete(id):
    delete_rental = record.query.get_or_404(id)
    
    try:
        db.session.delete(delete_rental)
        db.session.commit()
        return redirect('/rentals')
    except:
        return 'An error ocurred deleting that rental.'
    

#car update functionality
@app.route('/rentals/update/<int:id>', methods=['POST', 'GET'])
def rentalUpdate(id):
    edit_rental = record.query.get_or_404(id) 
    if request.method == 'POST':
        date_format = '%Y-%m-%d'
        rental_start = datetime.strptime(request.form['startDate'],date_format) #if the format is wrong this will error on its own on the page
        
        if(int(request.form['duration']) <= 0): #make sure the duration is a postive int
            return "Duration must be 1 or more"
        else:
            rental_end = rental_start +timedelta(days=int(request.form['duration']))


        
        thatCar = db.session.get(car,request.form['car'] ) #grabs the car to make sure it exists

        
        if int(request.form['car']) == 0: #this is the case that you don't want to rent a specific car and instead want any car
            cars = car.query.order_by(car.id).all()
            counter = 0;
            conflict = True;
            while counter < len(cars) and conflict:
                conflict = cars[counter].testConflict(rental_start,rental_end)
                if(not conflict):
                    edit_rental.car_id = cars[counter].id
                counter += 1;
            if conflict:
                return "No cars available for this rental. You may need to buy more cars to fill demand"

        elif thatCar == None: #this case you wanted a specifc car but it doesn't exist
            return "Car ID not registered in the system."
        

        else: #this case you want a specifc car and it does exist
            if thatCar.testConflict(rental_start, rental_end):
                return "There is an overlap in dates with another record. This car can't fill the demand."
            else:    
                edit_rental.car_id = request.form['car']

        edit_rental.startDT = rental_start #these updates only happen if the request is valid
        edit_rental.endDT = rental_end
        try:
            db.session.commit()
            return redirect('/rentals')
        except:
            return 'Error updating rental'
    else:
        return render_template('rentalUpdate.html', rental = edit_rental)
    

if __name__ == "__main__":
    app.run(debug=True)
