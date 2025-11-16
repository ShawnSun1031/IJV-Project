import json

import numpy as np
from pmcx.io import copycfg


def mcx2preview_json(cfg, filestub):
    """
    Format:
        mcx2json(cfg, filestub)

    Save MCXLAB simulation configuration to a JSON file for MCX binary

    Author: Qianqian Fang <q.fang at neu.edu>
    Converted to Python

    Parameters:
    -----------
    cfg : dict
        A dict defining the parameters associated with a simulation.
        Please run 'help mcxlab' or 'help mmclab' to see the details.
        mcxpreview supports the cfg input for both mcxlab and mmclab.
    filestub : str
        The filestub is the name stub for all output files, including:
        filestub.json: the JSON input file
        filestub_vol.bin: the volume file if cfg.vol is defined
        filestub_shapes.json: the domain shape file if cfg.shapes is defined
        filestub_pattern.bin: the domain shape file if cfg.pattern is defined

    Dependency:
        This function depends on the savejson/saveubjson functions from the
        Iso2Mesh toolbox (http://iso2mesh.sf.net) or JSONlab toolbox
        (http://iso2mesh.sf.net/jsonlab)
    """

    # Define the optodes: sources and detectors
    Optode = {}
    Optode["Source"] = {}
    Optode["Source"] = copycfg(cfg, "srcpos", Optode["Source"], "Pos")
    Optode["Source"] = copycfg(cfg, "srcdir", Optode["Source"], "Dir")
    Optode["Source"] = copycfg(cfg, "srciquv", Optode["Source"], "IQUV")
    Optode["Source"] = copycfg(cfg, "srcparam1", Optode["Source"], "Param1")
    Optode["Source"] = copycfg(cfg, "srcparam2", Optode["Source"], "Param2")
    Optode["Source"] = copycfg(cfg, "srctype", Optode["Source"], "Type")
    Optode["Source"] = copycfg(cfg, "srcnum", Optode["Source"], "SrcNum")
    Optode["Source"] = copycfg(cfg, "lambda", Optode["Source"], "WaveLength")

    if "detpos" in cfg and cfg["detpos"] is not None and len(cfg["detpos"]) > 0:
        Optode["Detector"] = []
        detpos = np.array(cfg["detpos"])
        for i in range(detpos.shape[0]):
            detector = {
                "Pos": detpos[i, :3].tolist(),
                "R": detpos[i, 3] if detpos.shape[1] > 3 else 1,
            }
            Optode["Detector"].append(detector)

        if len(Optode["Detector"]) == 1:
            Optode["Detector"] = [Optode["Detector"][0]]

    if "srcpattern" in cfg and cfg["srcpattern"] is not None:
        Optode["Source"]["Pattern"] = np.array(cfg["srcpattern"], dtype=np.float32).tolist()

    # Define the domain and optical properties
    Domain = {}
    Domain = copycfg(cfg, "issrcfrom0", Domain, "OriginType", 0)
    Domain = copycfg(cfg, "unitinmm", Domain, "LengthUnit")
    Domain = copycfg(cfg, "invcdf", Domain, "InverseCDF")
    Domain = copycfg(cfg, "angleinvcdf", Domain, "AngleInverseCDF")

    # Convert prop matrix to Media list
    prop = np.array(cfg["prop"])
    Domain["Media"] = []
    for i in range(prop.shape[0]):
        media = {
            "mua": float(prop[i, 0]),
            "mus": float(prop[i, 1]),
            "g": float(prop[i, 2]),
            "n": float(prop[i, 3]),
        }
        Domain["Media"].append(media)

    if "polprop" in cfg and cfg["polprop"] is not None:
        polprop = np.array(cfg["polprop"])
        Domain["MieScatter"] = []
        for i in range(polprop.shape[0]):
            miescatter = {
                "mua": float(polprop[i, 0]),
                "radius": float(polprop[i, 1]),
                "rho": float(polprop[i, 2]),
                "nsph": float(polprop[i, 3]),
                "nmed": float(polprop[i, 4]),
            }
            Domain["MieScatter"].append(miescatter)

    Shapes = None
    if "shapes" in cfg and isinstance(cfg["shapes"], str):
        Shapes = json.loads(cfg["shapes"])
        Shapes = Shapes["Shapes"]

    if "vol" in cfg and cfg["vol"] is not None and "VolumeFile" not in Domain:
        vol = np.array(cfg["vol"])
        vol_dtype = vol.dtype

        # Determine MediaFormat based on volume data type and dimensions
        if vol_dtype in [np.uint8, np.int8]:
            Domain["MediaFormat"] = "byte"
            if vol.ndim == 4 and vol.shape[0] == 4:
                Domain["MediaFormat"] = "asgn_byte"
            elif vol.ndim == 4 and vol.shape[0] == 8:
                # Reshape and convert to uint64 equivalent
                vol = vol.reshape(-1).view(np.uint64).reshape(vol.shape[1:])
                cfg["vol"] = vol
                Domain["MediaFormat"] = "svmc"
        elif vol_dtype in [np.uint16, np.int16]:
            Domain["MediaFormat"] = "short"
            if vol.ndim == 4 and vol.shape[0] == 2:
                Domain["MediaFormat"] = "muamus_short"
        elif vol_dtype in [np.uint32, np.int32]:
            Domain["MediaFormat"] = "integer"
        elif vol_dtype in [np.float32, np.float64]:
            if vol_dtype == np.float64:
                vol = vol.astype(np.float32)
                cfg["vol"] = vol

            if np.all(np.mod(vol.flatten(), 1) == 0):
                if np.max(vol) < 256:
                    Domain["MediaFormat"] = "byte"
                    cfg["vol"] = vol.astype(np.uint8)
                else:
                    Domain["MediaFormat"] = "integer"
                    cfg["vol"] = vol.astype(np.uint32)
            elif vol.ndim == 4:
                if vol.shape[0] == 1:
                    Domain["MediaFormat"] = "mua_float"
                elif vol.shape[0] == 2:
                    Domain["MediaFormat"] = "muamus_float"
                elif vol.shape[0] == 4:
                    Domain["MediaFormat"] = "asgn_float"
        else:
            raise ValueError("cfg.vol has format that is not supported")

        Domain["Dim"] = list(vol.shape)
        if len(Domain["Dim"]) == 4:
            Domain["Dim"] = Domain["Dim"][1:]

        if Shapes is not None:
            # Check if Shapes contains "Grid"
            shapes_json = json.dumps(Shapes, separators=(",", ":"))
            if '"Grid"' not in shapes_json:
                Domain["VolumeFile"] = filestub + "_vol.bin"
                with open(Domain["VolumeFile"], "wb") as fid:
                    cfg["vol"].tobytes()
                    fid.write(cfg["vol"].tobytes())
        else:
            Domain["VolumeFile"] = ""
            Shapes = cfg["vol"]
            if Shapes.ndim == 4 and Shapes.shape[0] > 1:
                Shapes = np.transpose(Shapes, (1, 2, 3, 0))

    # Define the simulation session flags
    Session = {}
    Session["ID"] = filestub
    Session = copycfg(cfg, "isreflect", Session, "DoMismatch")
    Session = copycfg(cfg, "issave2pt", Session, "DoSaveVolume")
    Session = copycfg(cfg, "issavedet", Session, "DoPartialPath")
    Session = copycfg(cfg, "issaveexit", Session, "DoSaveExit")
    Session = copycfg(cfg, "issaveseed", Session, "DoSaveSeed")
    Session = copycfg(cfg, "isnormalize", Session, "DoNormalize")
    Session = copycfg(cfg, "outputformat", Session, "OutputFormat")
    Session = copycfg(cfg, "outputtype", Session, "OutputType")
    Session = copycfg(cfg, "debuglevel", Session, "Debug")
    Session = copycfg(cfg, "autopilot", Session, "DoAutoThread")
    Session = copycfg(cfg, "maxdetphoton", Session, "MaxDetPhoton")
    Session = copycfg(cfg, "bc", Session, "BCFlags")

    if (
        "savedetflag" in cfg
        and cfg["savedetflag"] is not None
        and isinstance(cfg["savedetflag"], str)
    ):
        cfg["savedetflag"] = cfg["savedetflag"].upper()
    Session = copycfg(cfg, "savedetflag", Session, "SaveDataMask")

    if "seed" in cfg and np.isscalar(cfg["seed"]):
        Session["RNGSeed"] = cfg["seed"]
    Session = copycfg(cfg, "nphoton", Session, "Photons")
    Session = copycfg(cfg, "minenergy", Session, "MinEnergy")
    Session = copycfg(cfg, "rootpath", Session, "RootPath")

    # Define the forward simulation settings
    Forward = {}
    Forward["T0"] = cfg["tstart"]
    Forward["T1"] = cfg["tend"]
    Forward["Dt"] = cfg["tstep"]

    # Assemble the complete input, save to a JSON or UBJSON input file
    mcxsession = {
        "Session": Session,
        "Forward": Forward,
        "Optode": Optode,
        "Domain": Domain,
    }

    if Shapes is not None:
        if isinstance(Shapes, list):
            mcxsession["Shapes"] = np.array(Shapes)  # type: ignore (would be replace to zlib compressed later)
        else:
            mcxsession["Shapes"] = Shapes  # type: ignore (would be replace to zlib compressed later)

    if "AngleInverseCDF" in Domain:
        del Domain["AngleInverseCDF"]  # preview does not need this field

    from jdata import savejd

    savejd(mcxsession, filestub + ".json", compression="zlib")
