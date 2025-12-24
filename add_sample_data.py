from app import app, db
from models import Theater, Show, Person, Production, Credit

def add_sample_data():
    with app.app_context():
        print("Adding sample data...")
        
        theaters = [
            Theater(name="THE ARGYLE THEATRE", joomla_id=101, latitude="40.7128", longitude="-74.0060", city="New York", state="NY"),
            Theater(name="The Gateway", joomla_id=102, latitude="40.7589", longitude="-73.9851", city="New York", state="NY"),
            Theater(name="John W. Engeman Theater", joomla_id=103, latitude="40.7614", longitude="-73.9776", city="New York", state="NY"),
            Theater(name="Broadway Theater", joomla_id=104, latitude="40.7614", longitude="-73.9840", city="New York", state="NY"),
        ]
        
        for theater in theaters:
            existing = Theater.query.filter_by(name=theater.name).first()
            if not existing:
                db.session.add(theater)
            else:
                existing.latitude = theater.latitude
                existing.longitude = theater.longitude
                existing.city = theater.city
                existing.state = theater.state
        
        shows = [
            Show(title="The Phantom of the Opera"),
            Show(title="A Christmas Carol"),
            Show(title="Grease"),
            Show(title="Hamilton"),
            Show(title="Wicked"),
        ]
        
        for show in shows:
            existing = Show.query.filter_by(title=show.title).first()
            if not existing:
                db.session.add(show)
        
        db.session.flush()
        
        people = [
            Person(name="John Smith", disciplines="Actor, Director"),
            Person(name="Sarah Johnson", disciplines="Actor"),
            Person(name="Michael Brown", disciplines="Actor, Choreographer"),
            Person(name="Emily Davis", disciplines="Actor"),
            Person(name="David Wilson", disciplines="Director"),
            Person(name="Lisa Anderson", disciplines="Actor"),
            Person(name="Robert Taylor", disciplines="Actor"),
            Person(name="Jennifer Martinez", disciplines="Actor, Director"),
        ]
        
        for person in people:
            existing = Person.query.filter_by(name=person.name).first()
            if not existing:
                db.session.add(person)
        
        db.session.flush()
        
        theaters_list = Theater.query.all()
        shows_list = Show.query.all()
        people_list = Person.query.all()
        
        if theaters_list and shows_list and people_list:
            productions = [
                Production(
                    theater_id=theaters_list[0].id,
                    show_id=shows_list[0].id,
                    year=2024,
                    start_date="2024-01-15",
                    end_date="2024-03-15",
                    preview_image="previews/Phantom_preview.jpg"
                ),
                Production(
                    theater_id=theaters_list[1].id,
                    show_id=shows_list[1].id,
                    year=2024,
                    start_date="2024-11-20",
                    end_date="2024-12-30",
                    preview_image="previews/Christmas_preview.jpg"
                ),
                Production(
                    theater_id=theaters_list[2].id,
                    show_id=shows_list[2].id,
                    year=2023,
                    start_date="2023-06-01",
                    end_date="2023-08-31",
                ),
                Production(
                    theater_id=theaters_list[0].id,
                    show_id=shows_list[3].id,
                    year=2024,
                    start_date="2024-05-01",
                    end_date="2024-07-31",
                ),
            ]
            
            for prod in productions:
                existing = Production.query.filter_by(
                    theater_id=prod.theater_id,
                    show_id=prod.show_id,
                    year=prod.year
                ).first()
                if not existing:
                    db.session.add(prod)
            
            db.session.flush()
            
            productions_list = Production.query.all()
            
            if productions_list and people_list:
                credits_data = [
                    (productions_list[0], people_list[0], "Phantom", "Cast", True),
                    (productions_list[0], people_list[1], "Christine", "Cast", True),
                    (productions_list[0], people_list[2], "Raoul", "Cast", False),
                    (productions_list[0], people_list[4], "Director", "Creative", True),
                    (productions_list[0], people_list[2], "Choreographer", "Creative", False),
                    
                    (productions_list[1], people_list[1], "Scrooge", "Cast", True),
                    (productions_list[1], people_list[3], "Ghost of Christmas Past", "Cast", True),
                    (productions_list[1], people_list[5], "Bob Cratchit", "Cast", False),
                    (productions_list[1], people_list[4], "Director", "Creative", True),
                    
                    (productions_list[2], people_list[0], "Danny Zuko", "Cast", True),
                    (productions_list[2], people_list[3], "Sandy", "Cast", True),
                    (productions_list[2], people_list[6], "Rizzo", "Cast", False),
                    (productions_list[2], people_list[7], "Director", "Creative", True),
                    
                    (productions_list[3], people_list[0], "Alexander Hamilton", "Cast", True),
                    (productions_list[3], people_list[1], "Eliza Hamilton", "Cast", True),
                    (productions_list[3], people_list[6], "Aaron Burr", "Cast", True),
                    (productions_list[3], people_list[4], "Director", "Creative", True),
                ]
                
                for prod, person, role, category, is_equity in credits_data:
                    existing = Credit.query.filter_by(
                        production_id=prod.id,
                        person_id=person.id,
                        role=role
                    ).first()
                    if not existing:
                        credit = Credit(
                            production_id=prod.id,
                            person_id=person.id,
                            role=role,
                            category=category,
                            is_equity=is_equity
                        )
                        db.session.add(credit)
                
                ensemble_credits = [
                    (productions_list[0], people_list[5], "Ensemble", True),
                    (productions_list[0], people_list[6], "Ensemble", False),
                    (productions_list[1], people_list[7], "Ensemble", True),
                    (productions_list[2], people_list[2], "Ensemble", False),
                ]
                
                for prod, person, role, is_equity in ensemble_credits:
                    existing = Credit.query.filter_by(
                        production_id=prod.id,
                        person_id=person.id,
                        role=role
                    ).first()
                    if not existing:
                        credit = Credit(
                            production_id=prod.id,
                            person_id=person.id,
                            role=role,
                            category="Ensemble",
                            is_equity=is_equity
                        )
                        db.session.add(credit)
        
        db.session.commit()
        print("Sample data added successfully!")
        print("\nYou can now test:")
        print("- http://localhost:5000/dashboard")
        print("- http://localhost:5000/public/actor/1")
        print("- http://localhost:5000/public/show/1")
        print("- http://localhost:5000/public/theater/1")
        print("- http://localhost:5000/public/search")

if __name__ == "__main__":
    add_sample_data()

