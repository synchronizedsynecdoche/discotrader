from typing import List, Dict, Any, NewType
from utils import *
from position import Position
from user import User
import pickle
from datetime import datetime
import time
import threading
import configparser
from databaseInterface import DatabaseInterface

def pickle2sqlite(old_f, new_f):
    with open(old_f, "rb") as f:
        temp = pickle.load(f)
        dbi = DatabaseInterface(filename=new_f)
        print(dbi.commitUsers(temp))