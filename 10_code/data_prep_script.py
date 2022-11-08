#!/usr/bin/env python

"""This script is used to prepare the data for the analysis. Comment out the areas you do not want to execute at the bottom."""

################################
# Initial set up
################################

# import pacakges
import pandas as pd
import numpy as np
import os

# set path to the files
wapo = "/Users/andrewkroening/Desktop/720_Data/arcos_all_washpost.tsv.gz"
nick_path = "/Users/andrewkroening/Desktop/720_Data/US_VitalStatistics"
# census =
# fips =

#################################
# Ingest the mortality files
#################################


## Have an issue with null FIPS codes


def text_reader(path):
    """Function to read a series of txt files in a directory and return a single df

    Args:
        path: path to the directory containing the txt files

    Returns:
        nick_df: a single df containing all the data from the txt files"""

    # initialize the empty df
    nick_df = pd.DataFrame()

    print("Ingesting text files...")

    # set a loop to iterate through the files in the folder
    for file in os.listdir(path):
        if file.endswith(".txt"):
            txt_table = pd.read_table(os.path.join(path, file), sep="\t")
            nick_df = pd.concat([nick_df, txt_table], axis=0)

    # subset to the columns we want
    vital_df = nick_df[
        [
            "County",
            "County Code",
            "Year",
            "Drug/Alcohol Induced Cause",
            "Drug/Alcohol Induced Cause Code",
            "Deaths",
        ]
    ].copy()

    print("Transforming vitality data...")

    # change the year column to a date time object with a year only
    vital_df["Year"] = pd.to_datetime(vital_df["Year"], format="%Y")

    # change the County Code column to an integer
    # vital_df["County Code"] = vital_df["County Code"].astype(int)

    # convert NaN deaths to 0
    vital_df["Deaths"] = vital_df["Deaths"].fillna(0)

    # change the county name to all caps
    vital_df["County"] = vital_df["County"].str.upper()

    # save this file as a csv called wapo_clean.csv in the current directory
    vital_df.to_csv("../20_intermediate_files/vital_clean.csv", index=False)

    print("This is a sample of the vital stats DF:")
    print(vital_df.sample(5))

    return vital_df


#################################
# Ingest the WAPO file as chunks
#################################


def wapo_reader(wapo_path):
    chunks = 500000  # Leave this, there will be 358 chunks

    chunk_counter = 0

    states = ["FL", "TX", "WA", "GA", "OK", "OR"]  # last three are control states

    wapo_df = pd.DataFrame()

    for chunk in pd.read_csv(
        wapo_path,
        sep="\t",
        compression="gzip",
        chunksize=chunks,
        usecols=[
            "BUYER_COUNTY",
            "BUYER_STATE",
            "DRUG_NAME",
            "TRANSACTION_DATE",
            "QUANTITY",
            "UNIT",
        ],
    ):
        chunk_counter += 1
        percent_chunk = round(chunk_counter / 358 * 100, 2)
        print("Reading chunk: ", chunk_counter, "of 358 (", percent_chunk, "%)")

        # filter the chunk to only include the stations in the list
        chunk = chunk[chunk["BUYER_STATE"].isin(states)]

        # concat with the base df
        wapo_df = pd.concat([wapo_df, chunk])

    print("Transforming WAPO data...")

    print("Adding county name...")
    # Do some transformations on the WAPO dataset
    wapo_df["COUNTY_NAME"] = (
        wapo_df["BUYER_COUNTY"] + " COUNTY, " + wapo_df["BUYER_STATE"]
    )

    print("Formatting transaction date...")

    wapo_df["TRANSACTION_DATE"] = pd.to_datetime(
        wapo_df["TRANSACTION_DATE"], format="%m%d%Y"
    )
    wapo_df["YEAR"] = wapo_df["TRANSACTION_DATE"].dt.year
    wapo_df["MONTH"] = wapo_df["TRANSACTION_DATE"].dt.month

    print("Grouping WAPO data...")

    wapo_df = (
        wapo_df.groupby(["COUNTY_NAME", "BUYER_STATE", "YEAR", "MONTH"])
        .agg({"QUANTITY": "sum"})
        .reset_index()
    )

    # save this file as a csv called wapo_clean.csv in the current directory
    wapo_df.to_csv("../20_intermediate_files/wapo_clean.csv", index=False)

    # print a sample to make sure you did it right
    print("This is a sample of the WAPO DF")
    print(wapo_df.sample(10))

    return wapo_df


#################################
# Ingest the census file
#################################

# need to identify the file and then read it in

#################################
# Ingest the FIPS codes
#################################

# We will have to ingest the file
# We will have to append the state FIPS???


#################################
#################################
# Script Runners
#################################
#################################

# run the wapo reader
wapo_df = wapo_reader(wapo)

# run the vitality reader
mortality_df = text_reader(nick_path)
