from kadai import db,app
from kadai.models import Company, Item 

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        if not Company.query.first():
            company = Company(company_name="Namma Kadai", cash_balance=1000.0)
            db.session.add(company)
            
            items = [
                Item(item_name="Pen", qty=0, item_price=5.0),
                Item(item_name="Pencil", qty=0,item_price=2.0),
                Item(item_name="Eraser", qty=0,item_price=1.0),
                Item(item_name="Sharpener", qty=0,item_price=2.0),
                Item(item_name="Geometry box", qty=0,item_price=10.0),
            ]
            db.session.bulk_save_objects(items)
            db.session.commit() 

    app.run(debug=True)