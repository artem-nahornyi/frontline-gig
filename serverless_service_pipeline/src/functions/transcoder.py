import requests
import inspect
import logging
import pandas
import boto3
import geopy
import json
import time
import sys
import os

from io import BytesIO
from datetime import datetime, timedelta
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Float, create_engine

# Setup logger to work with both AWS CloudWatch and locally
if len(logging.getLogger().handlers) > 0:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

DB_ENGINE_STRING  = os.environ['DB_ENGINE_STRING']
DB_ENDPOINT       = os.environ['DB_ENDPOINT']
DB_PORT           = os.environ['DB_PORT']
DB_NAME           = os.environ['DB_NAME']
DB_USER           = os.environ['DB_USER']
DB_PWD            = os.environ['DB_PWD']

CONNECTION_STRING = f"{DB_ENGINE_STRING}://{DB_USER}:{DB_PWD}@{DB_ENDPOINT}:{DB_PORT}/{DB_NAME}" # /compose

SOURCE_TABLE_COLUMNS = [
    'service_request_number',
    'service_request_category',
    'service_request_type',
    'source',
    'status',
    'address',
    'creation_date',
    'modification_date',
]

RESOLVED_COLUMNS = [
    'hours_delta',
    'resolved_address',
    'resolved_postcode',
    'resolved_longitude',
    'resolved_latitude'
]

DATABASE_COLUMNS = SOURCE_TABLE_COLUMNS + RESOLVED_COLUMNS

CATEGORY_SELECTION = {
    'Environmental Services',
    'Neighborhood Quality',
    'Parks & Urban Forestry',
    'Permits and Inspections',
    'Stormwater',
    'VDOT',
    'Vector Control Division',
    'Waste Management'
}

TYPE_SELECTION = {
    'Bike Trail Concerns',
    'Boat Ramps/Kayak Launches/Fishing Piers',
    'Bulky Item Pick Up Request',
    'City Branches / Limbs Over Street',
    'City Tree / Limb Down',
    'City Tree Planting Requests',
    'City Tree Pruning / Removal',
    'Collection Complaint',
    'Container On Beach',
    'Container Storage',
    'Containers',
    'Debris at Curb',
    'Deceased Animal',
    'Delayed Containers',
    'Ditch Cleaning',
    'Dog Park Concerns',
    'Dumping',
    'Dumpster Issues',
    'Erosion and Sediment Control',
    'Illegal Cutting of City Tree Report',
    'Illicit Discharge',
    'Litter',
    'Median Maintenance',
    'Mishandling of Collection',
    'More Than 3 CY of Bulk Waste Request',
    'Multi-Family Recycling',
    'Open P&UF Building',
    'Recy 90 Enforcement',
    'Refuse Hrubs Billing Concerns',
    'Request for Stump Removal - Tree Already Cut',
    'Retention Pond Maintenance',
    'Stinging Insects on City Property',
    'Tall Weeds and Grass',
    'Trash Receptacle Request',
    'Trash and Debris',
    'Wetland /Waterway Concern',
    'Working Without Permit'    
}


Base = declarative_base()

class ServiceEvent(Base):
    '''Table Entry Schema'''
    __tablename__ = 'service_events'
    
    service_request_number   = Column(String(64), primary_key=True)
    service_request_category = Column(String(64))
    service_request_type     = Column(String(64))
    source                   = Column(String(64))
    status                   = Column(String(32))
    address                  = Column(String(255))
    creation_date            = Column(String(19))
    modification_date        = Column(String(19))
    hours_delta              = Column(Float(precision=10, decimal_return_scale=None))
    resolved_address         = Column(String(255))
    resolved_postcode        = Column(String(5))
    resolved_longitude       = Column(Float(precision=10, decimal_return_scale=None))
    resolved_latitude        = Column(Float(precision=10, decimal_return_scale=None))

def write_data_to_db(data):
    '''
    Writes data to Frontline GIG Postgress

    param:data - Pandas DataFrame
    '''
    engine = create_engine(CONNECTION_STRING, echo=False)

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)

    session = Session()

    existing_service_request_numbers = session.query(
                                            ServiceEvent
                                        ).filter(
                                            ServiceEvent.service_request_number.in_(
                                                data.service_request_number.unique()
                                            )
                                        ).with_entities(
                                            ServiceEvent.service_request_number
                                        ).all()
    existing_service_request_numbers = set([each[0] 
                                            for each 
                                            in existing_service_request_numbers])

    update_data = data[ data.service_request_number.isin(existing_service_request_numbers)]
    insert_data = data[~data.service_request_number.isin(existing_service_request_numbers)]

    for i, row in update_data.iterrows():
        session.merge(ServiceEvent(**row.to_dict()))

    for i, row in insert_data.iterrows():
        session.add(ServiceEvent(**row.to_dict()))

    session.commit()

    session.close()

def valid_message(msg):
    if not all([field in msg for field in SOURCE_TABLE_COLUMNS]):
        raise ValueError(f"{msg} doesn't match expected fields {SOURCE_TABLE_COLUMNS}")
    else:
        return True

    
def geocode(geocoder, address, addressdetails=True, retries=2, retry=1):
    '''
    Geocodes string address into locaiton object

    param:geocoder       - geopy geocoder object
    param:address        - string, service request address
    param:addressdetails - bool, indicates wether to parse resolved adress
    param:retries        - int, optional, number of retries if geocoder fails
    param:retry          - int, recursive retry counter, breaks execution if retry > retries
    '''
    if retries > 5:
        raise ValueError(
            "Geocoding retries > 5 are not allowed due runtime limits"
        )
    if retry > retries:
        return None
    try:
        if "addressdetails" in inspect.signature(geocoder.geocode).parameters:
            # OpenStreetMap service
            event_location = geocoder.geocode(
                address, addressdetails=addressdetails
            )
        else:
            # GeoFarm Service
            # or any non OSM Service
            # Free can return non-respose
            # if experiences high load
            event_location = geocoder.geocode(
                address
            )
            # if non-response
            # need to retry in couple of secs
            if not event_location:
                return geocode(geocoder, 
                               address, 
                               addressdetails=addressdetails, 
                               retries=retries, 
                               retry=retry+1)
        return event_location
    
    except:
        time.sleep(2)
        return geocode(geocoder, 
                       address, 
                       addressdetails=addressdetails, 
                       retries=retries, 
                       retry=retry+1)

def chain_geocode(geocoders, address, retries=5):
    '''
    Helper, chain applies list of selected geocoders
    until one is able to resolve an address

    returns None if non of geocoders was able to resolve address

    param:geocoders - list of geocoders
    param:address   - string, human redable address as a text
    param:retries   - int, number of retries each geocoder can undertake
    '''
    for geocoder in geocoders:
        geocoded_location = geocode(geocoder, address, retries=retries)
        if geocoded_location:
            return geocoded_location
    
def get_resolved_address(geocoded_location):
    '''
    Returns resolved location address from geocoded object
    '''

    if 'display_name' in geocoded_location.raw:
        return geocoded_location.raw['display_name']
    elif 'formatted_address' in geocoded_location.raw:
        return geocoded_location.raw['formatted_address']
    else:
        return ''
    
def get_resolved_postcode(geocoded_location):
    '''
    Returns resolved postcode from geocoded object
    '''
    if 'address' in geocoded_location.raw:
        return geocoded_location.raw['address'].get('postcode', '')
    elif 'ADDRESS' in geocoded_location.raw:
        return geocoded_location.raw['ADDRESS'].get('postal_code', '')
    else:
        return ''
    
def termination_condition(dataframe):
    '''
    Checks if dataframe is empty
    '''
    if dataframe.empty: 
        logger.info(f'No data or data filtered out during filtering, terminating')
        return True
    else:
        return False


def transcode(sqs_event, context):
    '''
    Processes sqs service request messages,
    geocodes observations and stores data 
    into Frontline GIG database
    '''

    logger.info('Total of {} messages'.format(len(sqs_event['Records'])))
    
    data = pandas.DataFrame([json.loads(msg['body']) 
                             for msg 
                             in sqs_event['Records']
                             if valid_message(json.loads(msg['body']))])

    data = data[SOURCE_TABLE_COLUMNS]
    
    if termination_condition(data): 
        return
        
        
    # filter out entries that do not have address
    data = data[(pandas.notna(data.address))
                &
                (data.address != '')].copy()
    
    if termination_condition(data): 
        return
    
    # force strings for predictable behaviour
    data.address = data.address.astype(str)
    
    # narrow down to categories/types of interest
    data = data[data['service_request_category'].isin(CATEGORY_SELECTION) 
                & 
                data['service_request_type'].isin(TYPE_SELECTION)].copy()
    
    if termination_condition(data): 
        return
    
    # convert string date into datetime
    data['creation_date']     = pandas.to_datetime(data['creation_date'])
    data['modification_date'] = pandas.to_datetime(data['modification_date'])
    
    if termination_condition(data): 
        return
    
    # difference between modification and creation date
    data['hours_delta']        = data['modification_date'] - data['creation_date']
    # format creation and modificaiton dates
    # as string to store into database
    data['creation_date']     = data['creation_date'].dt.strftime("%Y-%m-%d %H:%M:%S")
    data['modification_date'] = data['modification_date'].dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # format time delta as number of hours (float)
    data['hours_delta'] = data['hours_delta'].dt.total_seconds() / (60 * 60)
    
    # define geocoders
    osm_geocoder = geopy.Nominatim(user_agent="OSMGeocoder", timeout=10)
    gfg_geocoder = geopy.GeocodeFarm(user_agent='GFGeocoder', timeout=10)

    # new geocoders can be added here
    # order matters, keep most accurate first
    geocoders = [osm_geocoder, gfg_geocoder]

    for event_place in data.address.unique():
        event_place_address = event_place

        # add address details to increase geocoder accuracy
        if 'NORFOLK' not in event_place_address.upper():
            event_place_address += ', NORFOLK'
        event_place_address = event_place + ', United States'

        # geocode, retry recursively if api returns non-response
        geocoded_location  = chain_geocode(geocoders, event_place_address, retries=2)

        # if geocoded, add meta to data
        if geocoded_location:
            resolved_address   = get_resolved_address(geocoded_location)
            resolved_postcode  = get_resolved_postcode(geocoded_location)
            resolved_latitude  = geocoded_location.latitude
            resolved_longitude = geocoded_location.longitude

            # set resolved values where address matches
            # the resolved event_place
            data.loc[
                data.address == event_place, 
                ['resolved_address', 'resolved_postcode', 'resolved_longitude', 'resolved_latitude']
            ] = resolved_address, resolved_postcode, resolved_longitude, resolved_latitude

        else:
            # geocoders did not resolve location address
            # rows with NaNs will be filtered out further
            pass


    if not all([column in data.columns 
                for column
                in RESOLVED_COLUMNS]):
        return

    # filted data that was not geocoded
    data = data[~data[RESOLVED_COLUMNS].isna().any(axis=1)].copy()
    
    if termination_condition(data): 
        return

    # preserve only the postcodes that start with "23" -> 23001
    data = data[data.resolved_postcode.str.startswith('23')].copy()
    
    if termination_condition(data): 
        return

    shape = data.shape[0]
    logger.info(f'Finalized with {shape} entries')

    write_data_to_db(data)

    return 
