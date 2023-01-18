import streamlit as st 
from utils import RawResults
import random
import matplotlib.pyplot as plt
import numpy as np 
import datetime
import yaml
from copy import deepcopy

#st.set_page_config(layout="wide")

RAW_FILE = 'data/20200428_Evosep_60SPD_SG06-16_MLHeLa_200ng_py8_S3-A4_1_2450.d'
RESULTS_PATH = 'data/report.tsv'
from io import BytesIO

BUFFER_SIZE = 100


def lineplot(c, sample):
    fig = c.lineplot_from_index(sample)
    buf = BytesIO()
    fig.savefig(buf, format="png")    

    return buf

def imgplot(c, sample):

    img_dict =c.img_from_index(sample)
    fig, axes = plt.subplots(nrows=2, ncols=10, figsize=(10,5))

    for ax in axes.flatten():
        ax.set_xticks([])
        ax.set_yticks([])
        ax.imshow(np.ones((2,2)), cmap='gray', vmin=0, vmax=1)


    for k, v in img_dict.items():
        try:
            col = int(k.split('_')[-1].split(' ')[0])

        except ValueError:
            col = 0
        if k.startswith('p'):
            row = 0
            t = 'precursor'
        if k.startswith('b'):
            row = 0
            t = f'b {col}'
        if k.startswith('y'):
            row = 1
            t = f'y {col}'

        if col <10:
            ax = axes[row, col]
            #fig = plt.figure(figsize=(5 ,5))
            ax.imshow(v.T, vmin=0, vmax=0.5*v.max(), cmap='hot')
            ax.set_title(t)

        #plt.xlabel('RT')
        #plt.ylabel('Mobility')
    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png")

    return buf



def write_entry(out_file, entry):
    with open(out_file, "a") as reader:
        reader.write(entry)


def add_to_buffer():

    if len(st.session_state['buffer']) < BUFFER_SIZE:
        i = random.sample(range(len(st.session_state['raw_data'].ref_filtered)), 1)[0]
        b1 = lineplot(st.session_state['raw_data'], i)
        b2 = imgplot(st.session_state['raw_data'], i)

        st.session_state['buffer'].append((i, b1, b2))

def extract_from_buffer():

    if len(st.session_state['buffer']) < 1:
        add_to_buffer()

    return st.session_state['buffer'].pop(0)

@st.cache
def file_loader(RAW_FILE, RESULTS_PATH):

    return RawResults(RAW_FILE, RESULTS_PATH)


if 'raw_data' not in st.session_state:

    st.session_state['raw_data']  = True #To block in case it is loading.

    with st.spinner('Loading file..'):
        c = file_loader(RAW_FILE, RESULTS_PATH)

        st.session_state['raw_data'] = deepcopy(c)

        with open(st.session_state['out_file_yaml'], 'w') as yaml_file:

            metadata = st.session_state['raw_data'].metadata

            metadata['annotation_file'] = st.session_state['out_file']
            yaml.dump(metadata, yaml_file, default_flow_style=False)


if 'button_pressed' not in st.session_state:
    st.session_state['button_pressed'] = 0

if 'count' not in st.session_state:
    st.session_state['count'] = 0

if 'start' not in st.session_state:
    st.session_state['start'] = datetime.datetime.now()


if 'buffer' not in st.session_state:
    st.session_state['buffer'] = []


username = st.sidebar.text_input('User','')
st.session_state["username"]  = username

if username == '':
    st.error('Please enter username in the sidebar.')
    st.stop()

if 'out_file' not in st.session_state and "username" in st.session_state:

    now = datetime.datetime.now().date()
    st.session_state['out_file'] = f"annotation_results/{st.session_state.username}_{now}_session.txt"
    st.session_state['out_file_yaml'] = f"annotation_results/{st.session_state.username}_{now}_session.yaml"

with st.form('Peptide Checker', clear_on_submit=True):
    sample, b1, b2 = extract_from_buffer()

    st.image(b1)
    st.image(b2)

    confidence = st.slider('Confidence', min_value=-1.0, max_value= 1.0, value=0.0, step=0.2) #, key=st.session_state['button_pressed'])

    submitted = st.form_submit_button("Submit")

    if submitted:

        base_entry = f'{datetime.datetime.now().isoformat()}\t {username} \t {sample}'
        entry = base_entry + f'\t {confidence}\n'
        st.success(entry)

        write_entry(st.session_state['out_file'], entry)

        st.session_state['count'] +=1


add_to_buffer()

delta = datetime.datetime.now() - st.session_state['start']
speed = st.session_state['count'] / (delta.total_seconds()/60)
st.sidebar.write(f"Count {st.session_state['count']}, Speed {speed:.2f} /minute")
st.sidebar.write(f"Logfile {st.session_state['out_file']}")
st.sidebar.write(f"Buffer {len(st.session_state['buffer'])}")

