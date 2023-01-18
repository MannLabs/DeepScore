import hashlib

from alphabase.peptide.fragment import create_fragment_mz_dataframe_by_sort_precursor, get_charged_frag_types
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

from scipy.ndimage import gaussian_filter


import alphatims
import alphatims.bruker
import os
import alphabase

import streamlit as st

from alphabase.io.psm_reader.psm_reader import (
    psm_reader_provider, psm_reader_yaml
)


def sha256sum(filename):
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()

class RawResults():

    def __init__(self, raw_file, results_file, tol_rt = 30, tol_mz_ppm = 10, tol_mob = 0.05):
        self.raw_file = raw_file
        self.results_file = results_file
        self.raw_file_short = os.path.splitext(os.path.split(raw_file)[1])[0]

        self.tol_rt = tol_rt
        self.tol_mz_ppm = tol_mz_ppm
        self.tol_mob = tol_mob

        self.metadata = {}

        self.metadata['ver_alphabase'] = alphabase.__version__
        self.metadata['ver_alphatims'] = alphatims.__version__
        self.metadata['tol_rt'] = tol_rt
        self.metadata['tol_mz_ppm'] = tol_mz_ppm
        self.metadata['tol_mob'] = tol_mob

        self.metadata['file_raw'] = raw_file
        self.metadata['file_results'] = results_file

        self.read_raw_file()
        self.read_results_file()
        self.create_fragments()
        self.filter_results()

    def read_raw_file(self):
        self.dia_data = alphatims.bruker.TimsTOF(self.raw_file)

        self.metadata['hash_raw'] = sha256sum(os.path.join(self.raw_file, 'analysis.tdf_bin'))
    
    def read_results_file(self):
        diann_reader = psm_reader_provider.get_reader_by_yaml(psm_reader_yaml['diann'])
        self.ref = diann_reader.import_file(self.results_file)
        self.metadata['hash_results'] = sha256sum(self.results_file)

    def create_fragments(self):
        self.fragment_mz_df = create_fragment_mz_dataframe_by_sort_precursor(
        self.ref,
        get_charged_frag_types(['b','y'],3)
        )

    def filter_results(self):
        self.ref_filtered = self.ref[self.ref['raw_name'] == self.raw_file_short]
        #self.ref_filtered = self.ref_filtered[self.ref_filtered['score'] > 0.99]

    
    def get_slices(self, precursor_rt, precursor_mobility, precursor_mz):

        rt_slice = slice(
            precursor_rt - self.tol_rt,
            precursor_rt + self.tol_rt
        )
        im_slice = slice(
            precursor_mobility - self.tol_mob,
            precursor_mobility + self.tol_mob
        )
        precursor_mz_slice = slice(
            precursor_mz / (1 + self.tol_mz_ppm / 10**6),
            precursor_mz * (1 +  self.tol_mz_ppm / 10**6)
        )

        return rt_slice, im_slice, precursor_mz_slice


    def raw_df_from_index(self, index):
        
        raw_data = []

        peptide = self.ref_filtered.iloc[index].copy()

        precursor_rt = peptide["rt"]*60
        precursor_mz = peptide["precursor_mz"]
        precursor_mobility = peptide["mobility"]
        
        rt_slice, im_slice, precursor_mz_slice = self.get_slices(precursor_rt, precursor_mobility, precursor_mz)

        precursor_indices = self.dia_data[
        rt_slice,
        im_slice,
        0, #index 0 means that the quadrupole is not used
        precursor_mz_slice,
        "raw"
        ]

        precursor_df = self.dia_data.as_dataframe(precursor_indices)
        precursor_df['type'] = 'prec'
        raw_data.append(precursor_df)

        start, end = peptide['frag_start_idx'], peptide['frag_stop_idx']

        fragments = self.fragment_mz_df.iloc[start:end]

        for fragment_idx in range(len(fragments)):        
            for ion in ['b','y']:
                frag = fragments.iloc[fragment_idx]

                ion_type = ion+f"_z1"

                frag = frag[ion_type]
                
                fragment_mz_slice = slice(
                    frag / (1 + self.tol_mz_ppm / 10**6),
                    frag * (1 + self.tol_mz_ppm / 10**6)
                )

                fragment_indices = self.dia_data[
                rt_slice,
                im_slice,
                precursor_mz_slice,
                fragment_mz_slice,
                "raw"]
                
                precursor_df = self.dia_data.as_dataframe(fragment_indices)
                precursor_df['type'] = ion_type+f'_{fragment_idx+1}'
                raw_data.append(precursor_df)

        return pd.concat(raw_data) 


    def lineplot_from_index(self, index, delta_rt = 2):
        sub = self.raw_df_from_index(index)
        peptide = self.ref_filtered.iloc[index].copy()

        precursor_rt = peptide["rt"]*60
        precursor_mz = peptide["precursor_mz"]
        precursor_mobility = peptide["mobility"]
        peptide_seq = peptide['sequence']

        gene = peptide['genes']

        fig = plt.figure(figsize=(10,5))

        for _ in sub['type'].unique().tolist():
            subsub = sub[sub['type'] ==_]

            min_rt = subsub['rt_values'].min()
            max_rt = subsub['rt_values'].max()

            bins = np.arange(min_rt, max_rt, delta_rt)

            cnt, rts = np.histogram(subsub['rt_values'], weights = subsub['corrected_intensity_values'], bins=bins)

            if _ == 'prec':
                plt.plot(rts[:-1]+0.5*delta_rt, cnt, label=_.replace('_z1',''), color='k', linestyle=":")
            else:
                plt.plot(rts[:-1]+0.5*delta_rt, cnt, label=_.replace('_z1',''))

        plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')

        plt.title(f"{peptide_seq} {gene}")
        plt.xlabel('Rt')
        plt.ylabel('Int')

        return fig

    def img_from_index(self, index, im_size=128):

        sub = self.raw_df_from_index(index)
        peptide = self.ref_filtered.iloc[index].copy()

        precursor_rt = peptide["rt"]*60
        precursor_mz = peptide["precursor_mz"]
        precursor_mobility = peptide["mobility"]
        peptide_seq = peptide['sequence']

        x_edges = np.linspace(precursor_rt - self.tol_rt, precursor_rt + self.tol_rt, im_size+1)
        y_edges = np.linspace(precursor_mobility - self.tol_mob, precursor_mobility + self.tol_mob, im_size+1)

        img_dict = {}

        for _ in sub['type'].unique().tolist():

            subsub = sub[sub['type'] ==_]

            H, xedges, yedges = np.histogram2d(subsub['rt_values'], subsub['mobility_values'], weights = subsub['intensity_values'], bins=(x_edges, y_edges))

            d = subsub[['rt_values', 'corrected_intensity_values']].groupby('rt_values').sum().reset_index()

            label = _.replace('_z1','')
            img_dict[f'{label} {peptide_seq}'] = gaussian_filter(H, sigma=2)


        return img_dict

        


def create_user():
    # check if user is there
    pass

