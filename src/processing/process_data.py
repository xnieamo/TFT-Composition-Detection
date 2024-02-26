import os
import pandas as pd
import numpy as np

def main():
    # Set the working directory
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, '../../Data/Intermediate/matchUnits.csv')

    # Load the data csv from data/intermediate 
    df = pd.read_csv(filename)


    reset_indexes = [i for i, val in enumerate(df['characterId']) if val == 0]

    # Group the names, tiers, and item counts based on the reset indexes
    grouped_names = group_by_reset_index(df, reset_indexes, 'characterName')
    grouped_tiers = group_by_reset_index(df, reset_indexes, 'tier')
    grouped_item_count = group_by_reset_index(df, reset_indexes, 'itemCount')

    # Find the placement for each composition and turn it into a dataframe
    placement = [df.loc[reset_indexes[i], 'placement'].tolist()
                            for i in range(len(reset_indexes))]
    placement_df = pd.DataFrame(placement, columns=['placement'])

    # Get puuid for each composition
    puuid = [df.loc[reset_indexes[i], 'puuid']
                            for i in range(len(reset_indexes))]
    puuid_df = pd.DataFrame(puuid, columns=['puuid'])
 
    # Get unique names 
    unique_names = list(set(df['characterName']))

    # Init empty dataframes to store unit presence, tier, and item count.
    unit_presence = pd.DataFrame(columns=unique_names)
    unit_tier = pd.DataFrame(columns=unique_names)
    unit_item_count = pd.DataFrame(columns=unique_names)

    # Print status
    print("Starting to populate dataframes")
    # print(len(grouped_names))

    # Iterate through the groups and populate the dataframes
    for i, names, tiers, items in zip(range(len(grouped_names)), grouped_names, grouped_tiers, grouped_item_count):
        
        # Create zero np arrays for each unique name
        presence = np.zeros(len(unique_names))
        tier = np.zeros(len(unique_names))
        item_count = np.zeros(len(unique_names))

        # Find the index of the unique names in the group
        indexes = [unique_names.index(name) for name in names]

        # Populate the zero vectors with the tier and item count
        tier[indexes] = tiers
        item_count[indexes] = items
        presence[indexes] = 1

        # Append the vectors to the dataframes
        unit_presence.loc[i] = presence
        unit_tier.loc[i] = tier
        unit_item_count.loc[i] = item_count

        # Print the progress
        if i % 100 == 0:
            print(i)

    # Print completion
    print("Dataframes populated")

    # Save all data frames into the same h5 file
    h5_filename = os.path.join(dirname, '../../Data/Processed/compAnalysis.h5')
    with pd.HDFStore(h5_filename,'a', complevel=9, complib='blosc') as store:
        store.put('unit_presence', unit_presence)
        store.put('unit_tier', unit_tier)
        store.put('unit_item_count', unit_item_count)
        store.put('placement', placement_df)
        store.put('puuid', puuid_df)
    

# Function to group data by reset index
def group_by_reset_index(df, reset_indexes, column_name):
    return [df.loc[reset_indexes[i]:reset_indexes[i+1]-1, column_name].tolist() 
                 if i < len(reset_indexes)-1 
                 else df.loc[reset_indexes[i]:, column_name].tolist() 
                 for i in range(len(reset_indexes))]



main()