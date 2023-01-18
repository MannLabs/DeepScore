import streamlit as st
import s3fs
import os
from boto3 import Session
import smart_open

# Create connection object.
# `anon=False` means not anonymous, i.e. it uses access keys to pull data.
fs = s3fs.S3FileSystem(anon=False)

#def load_data_from_s3_bucket():#

 #   pass


class Session3bucket:
    def __init__(self, session_state_id):
        self.session_state_id = session_state_id
        self.make_session()
        self.open_stream()
    

    def make_session(self):
        self.session = Session(
            aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"]
        ).client('s3')
  
    def open_stream(self):
        write_path = "deepscoreannotate/" + str(self.session_state_id) + ".csv"
        self.stream = smart_open.open(f"s3://{write_path}", 
            mode='wb', 
            transport_params={'client': self.session}
            )
    
    def write_to_file(self, entry):
        entry = entry.encode("ascii") 
        self.stream.write(entry)