import numpy as np
import os
from glob import glob

#%%
def get_dataset(subject: str, train_or_test: str, ijv_type: str, )  -> np.ndarray:
    """get the all the result after WMC from mcx_sim, making training set and testing set.

    Args:
        subject (str): who is this
        train_or_test (str): [train | test]
        ijv_type (str): [ijv_large |ijv_small]
        
        
    Returns:
        np.ndarray: collect all the results from mcx_sim. 
    """

    # get datapaths of the mcx_sim result datapath
    dataset_folder = os.path.join("dataset", subject, train_or_test, ijv_type)
    datapath = sorted(glob(os.path.join(dataset_folder, "*")),
                      key=lambda x: int(x.split("_")[-1][:-4]))
    
    # debugging file exist or not.
    assert os.path.isdir(dataset_folder), "[DEBUG] Missing WMC result !!!"

    # make the array in advance
    num_file = len(datapath)
    each_file_rows = np.load(datapath[0]).shape[0]
    data = np.empty((num_file*each_file_rows, 12)) # Nx: Total Conbinations Ny: mus(5), mua(5), SDS1, SDS2
    
    for idx, path in enumerate(datapath):
        p = path.split("/")[-1]
        print(f"Now processing {p} .....")
        data[(idx)*each_file_rows:(idx+1)*each_file_rows] = np.load(path)

    return data

#%%
if __name__ == "__main__":
    # ====================== Modify your setting here ====================== #
    subject = "Julie"
    # ====================================================================== #
    
    os.makedirs(os.path.join("dataset", subject), exist_ok=True)
    train_or_test_set = ["train", "test"] # ["train" | "test"]
    ijv_type_set = ["ijv_large", "ijv_small"]
    for train_or_test in train_or_test_set:
        for ijv_type in ijv_type_set:
            data = get_dataset(subject=subject,
                            ijv_type=ijv_type,
                            train_or_test=train_or_test)
            np.save(os.path.join('dataset', subject, f'{ijv_type}_{train_or_test}.npy'), data)

