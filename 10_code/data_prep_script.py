#!/usr/bin/env python

"""This script is used to prepare the data for the analysis"""

################################
# Initial set up
################################

# import pacakges
import pandas as pd
import numpy as np
import os

# set path to the WAPO gzip file and txt file directory (nick_path)
wapo = "/Users/andrewkroening/Desktop/720_Data/arcos_all_washpost.tsv.gz"
nick_path = "/Users/andrewkroening/Desktop/720_Data/US_VitalStatistics"
# census =
# fips =

#################################
# Ingest the mortality files
#################################


## Have an issue with null FIPS codes


def reader(path):
    """Function to read a series of txt files in a directory and return a single df

    Args:
        path: path to the directory containing the txt files

    Returns:
        nick_df: a single df containing all the data from the txt files"""

    # initialize the empty df
    nick_df = pd.DataFrame()

    # set a loop to iterate through the files in the folder
    for file in os.listdir(path):
        if file.endswith(".txt"):
            txt_table = pd.read_table(os.path.join(path, file), sep="\t")
            nick_df = pd.concat([nick_df, txt_table], axis=0)
    return nick_df


# call the function to assemble the df
mortality_df = reader(nick_path)

# subset to the columns we want
vital_df = mortality_df[
    [
        "County",
        "County Code",
        "Year",
        "Drug/Alcohol Induced Cause",
        "Drug/Alcohol Induced Cause Code",
        "Deaths",
    ]
].copy()

# change the year column to a date time object with a year only
vital_df["Year"] = pd.to_datetime(vital_df["Year"], format="%Y")

# change the County Code column to an integer
# vital_df["County Code"] = vital_df["County Code"].astype(int)

# convert NaN deaths to 0
vital_df["Deaths"] = vital_df["Deaths"].fillna(0)

# change the county name to all caps
vital_df["County"] = vital_df["County"].str.upper()

print("This is a sample of the vital stats DF")
print(vital_df.sample(10))

#################################
# Ingest the WAPO file as chunks
#################################

chunks = 500000  # Leave this, there will be 358 chunks

chunk_counter = 0

states = ["FL", "TX", "WA", "GA", "OK", "OR"]  # last three are control states

wapo_df = pd.DataFrame()

for chunk in pd.read_csv(
    wapo,
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
    if chunk["BUYER_STATE"].isin(states).any():
        chunk["COUNTY_NAME"] = (
            chunk["BUYER_COUNTY"] + " COUNTY, " + chunk["BUYER_STATE"]
        )
        chunk["TRANSACTION_DATE"] = pd.to_datetime(
            chunk["TRANSACTION_DATE"], format="%m%d%Y"
        )
        chunk["YEAR"] = chunk["TRANSACTION_DATE"].dt.year
        chunk["MONTH"] = chunk["TRANSACTION_DATE"].dt.month

        wapo_df = pd.concat([wapo_df, chunk])

print("This is a sample of the WAPO DF")
wapo_df.groupby(["COUNTY_NAME", "YEAR", "MONTH"]).agg({"QUANTITY": "sum"}).reset_index()
wapo_df.sample(10)

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
# Replace missing FIPS codes
#################################

#################################
# Merge data
#################################
