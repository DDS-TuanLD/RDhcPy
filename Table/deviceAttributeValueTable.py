from sqlalchemy import Column, Integer, String
from sqlalchemy import DateTime
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

class deviceAttributeValueTable():
    def __init__(self, metadata: MetaData):
        self.deviceAttributeValueTable = Table('DeviceAttributeValue', metadata,
                        Column('DeviceId', String, primary_key=True, nullable=False),
                        Column('DeviceUnicastId', Integer, primary_key=True, nullable=False),
                        Column('DeviceAttributeId', Integer),
                        Column('Value', Integer),
                        Column('UpdateDay', Integer),
                        Column('UpdateTime', Integer),
                        ) 