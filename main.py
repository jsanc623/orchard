import csv
import os
import datetime
import json
import urllib

from app.arg_parser import ArgParser

from flask import Flask, request, render_template, redirect, flash, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

app = Flask(__name__)

local_file = None
config = None
port = 9005

@app.errorhandler(500)
def internal_error(error):
    return "500 Error: " + str(error)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/load')
def load():
    f_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/out.csv")

    # If we were given a local file, or if we've downloaded the file already, don't download again
    # Ideally, we would want to check the remote last-changed date, as well as the local
    # last updated or last accessed date to check for a newer remote file.
    # For simplicity, that is not done here.
    if not local_file:
        if not os.path.isfile(f_name):
            urllib.urlretrieve(config['file_link'], f_name)
    else:
        f_name = local_file

    session = Session()
    with open(f_name, 'rb') as csvfile:
        for row in csv.reader(csvfile):
            if row[0] != "CAMIS": # we don't care for the header line
                store = get_or_create(session, Store, name=row[1], boro=row[2], building = row[3],
                                      street = row[4], zipcode = row[5], phone = row[6], cuisine = row[7])
                session.add(store)
                session.flush()
                violation = Violations(inspection_date = datetime.datetime.strptime(row[8] or '1/1/1980', '%m/%d/%Y'),
                                       record_date = datetime.datetime.strptime(row[16] or '1/1/1980', '%m/%d/%Y'),
                                       grade_date = datetime.datetime.strptime(row[15] or '1/1/1980', '%m/%d/%Y'),
                                       grade = row[14],
                                       store=store)
                session.add(violation)
                session.commit()
    return redirect('/results')

@app.route('/results')
def results():
    # Join the store and violations table on the foreign key, then eliminate any empty grades and non-Thai places.
    # After that, order by grades initially (so A through C), then sort by the grade date (we want
    # recently graded restaurants to limit the number of degrading grades). Then limit by 10.
    top_10 = 'SELECT s.name, s.boro, s.building, s.street, s.zipcode, s.phone, s.cuisine, v.grade_date,' \
             'v.grade FROM store s LEFT OUTER JOIN violations v ON s.id = v.store_id WHERE grade <> "" ' \
             'AND s.cuisine = "thai" ORDER BY grade ASC, grade_date DESC LIMIT 10'

    # Same as above, but without the Thai constraint
    top_10_all = 'SELECT s.name, s.boro, s.building, s.street, s.zipcode, s.phone, s.cuisine, v.grade_date,' \
                 'v.grade FROM store s LEFT OUTER JOIN violations v ON s.id = v.store_id WHERE grade <> "" ' \
                 'ORDER BY grade ASC, grade_date DESC LIMIT 10'

    # We won't be doing any caching, but ideally, we'd want to cache 
    # these results if they don't change often.
    result = engine.execute(top_10)
    output_top_10 = []
    for row in result:
        print row[1]
        output_top_10.append({
            'name': row[0],
            'boro': row[1],
            'building': row[2],
            'street': row[3],
            'zipcode': row[4],
            'phone': row[5],
            'cuisine': row[6],
            'grade': row[8],
            'grade_date': datetime.datetime.strftime(row[7], '%m-%d-%Y')
        })

    result = engine.execute(top_10_all)
    output_top_10_all = []
    for row in result:
        output_top_10_all.append({
            'name': row[0],
            'boro': row[1],
            'building': row[2],
            'street': row[3],
            'zipcode': row[4],
            'phone': row[5],
            'cuisine': row[6],
            'grade': row[8],
            'grade_date': datetime.datetime.strftime(row[7], '%m-%d-%Y')
        })
    return render_template("results.html", 
                           output_top_10=output_top_10, 
                           output_top_10_all=output_top_10_all)

def get_or_create(session, model, **kwargs):
    """ get_or_create()
    A rudimentary generic upsert method
    :param session:
    :param model:
    :param **kwargs::
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if not instance:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance
    return instance

if __name__ == '__main__':
    arg_parser = ArgParser()
    arg_parser.add_option('--file', 'optional file to load rather than downloading it anew')
    arg_parser.add_option('--config', 'script configuration file path')
    arg_parser.add_option('--host', '(optional) host to bind service to')
    arg_parser.add_option('--port', '(optional) port to bind service to')
    arg_parser.parse_options()
    options = arg_parser.options

    # Set the local file if --file was set
    local_file = options.file if file in options else None
    if local_file and not os.path.isfile(local_file):
        raise IOError("File given as local file could not be found.")

    # Very rudimentary JSON based configuration system
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), options.config)
    if not os.path.isfile(config_file):
        raise IOError("Config file not found.")
    config = json.load(open(config_file))

    # Define our sqlite instance, create tables and grab a session
    try:
        if 'mysql' in config:
            engine = create_engine('mysql://' + config['mysql']['user'] + ':' + config['mysql']['pass'] + '@' +
                                   config['mysql']['host'] + '/' + config['mysql']['db'], echo=False)
        else:
            engine = create_engine('sqlite:///:memory:', echo=False) # Attempt an in-memory sqlite connection

        Base = declarative_base(bind=engine)

        # Store ORM model
        class Store(Base):
            __tablename__ = 'store'

            id = Column(Integer, primary_key=True, nullable=False)
            name = Column(String(150), nullable=False)
            boro = Column(String(20), nullable=True)
            building = Column(String(10), nullable=True)
            street = Column(String(100), nullable=True)
            zipcode = Column(String(10), nullable=True)
            phone = Column(String(100), nullable=True)
            cuisine = Column(String(100), nullable=True)

            def __repr__(self):
                return "<User(name='%s', boro='%s', building='%s', street='%s', zipcode='%s', phone='%s', cuisine='%s', )>" % \
                       (self.name, self.boro, self.building, self.street, self.zipcode, self.phone, self.cuisine)

        # Violations ORM model
        class Violations(Base):
            __tablename__ = 'violations'

            id = Column(Integer, primary_key=True)
            store_id = Column(Integer, ForeignKey("store.id", onupdate="CASCADE", ondelete="SET NULL"), nullable=True)
            inspection_date = Column(Date, nullable=True)
            record_date = Column(Date, nullable=True)
            grade_date = Column(Date, nullable=True)
            grade = Column(String(2), nullable=True)

            store = relationship(Store, backref='violations')

        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
    except Exception as e:
        print RuntimeError('Sqlite database connection could not be established: ' + str(e))

    host = options.host if 'host' in options else '0.0.0.0'
    try:
        app.run(host=host, port=int(options.port))
    except Exception as e:
        print e # In production, we'd log this, not just print it

