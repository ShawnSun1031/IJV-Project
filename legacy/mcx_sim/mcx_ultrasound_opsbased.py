import numpy as np
from scipy.interpolate import PchipInterpolator
import jdata as jd
from glob import glob
import os
import sys
import json

class MCX:

    # Initialize
    def __init__(self, sessionID):
        # load session ID
        self.sessionID = sessionID

        # load config and related file
        with open(os.path.join(self.sessionID, "config.json")) as f:
            self.config = json.load(f)
        with open(self.config["MCXInputPath"]) as f:
            self.mcxInput = json.load(f)

        # load model parameters
        with open(os.path.join(self.sessionID, "model_parameters.json")) as f:
            self.modelParameters = json.load(f)

        # create related folders in output path
        self.createFolder()

        # check if simulation_result.json is existed
        if not os.path.isfile(os.path.join(self.post_analysis, "{}_simulation_result.json".format(self.config["SessionID"]))):
            self.createSimResultTemplate()

        # check if mcx input file is existed
        if not os.path.isfile(os.path.join(self.json_output, "input_{}.json".format(self.config["SessionID"]))):
            self.makeMCXInput()

    def createFolder(self):
        # set folder path
        # main-path
        self.session = os.path.join(
            self.config["OutputPath"], self.config["SessionID"])
        # sub-path
        self.plot = os.path.join(self.session, "plot")
        self.plot_mc2 = os.path.join(self.session, "plot_mc2")
        self.post_analysis = os.path.join(self.session, "post_analysis")
        self.mcx_output = os.path.join(self.session, "mcx_output")
        self.json_output = os.path.join(self.session, "json_output")

        # create folder
        # main-path for this simulation session
        if not os.path.isdir(self.session):
            os.mkdir(self.session)
        # sub-path for saving plot
        if not os.path.isdir(self.plot):
            os.mkdir(self.plot)
        # sub-path for saving mc2 plot
        if not os.path.isdir(self.plot_mc2):
            os.mkdir(self.plot_mc2)
        # sub-path for saving post analysis (analysis after simulation if needed)
        if not os.path.isdir(self.post_analysis):
            os.mkdir(self.post_analysis)
        # sub-path for saving raw simulation output
        if not os.path.isdir(self.mcx_output):
            os.mkdir(self.mcx_output)
        # sub-path for saving MCX-used configuration
        if not os.path.isdir(self.json_output):
            os.mkdir(self.json_output)

    def createSimResultTemplate(self):
        result = {
            "SessionID:": self.config["SessionID"],
            "AnalyzedSampleNum": 0,
            "GroupingNum": 0,
            "PhotonNum": {"RawSample": "{}".format(self.config["PhotonNum"]), "GroupingSample": 0},
            "GroupingSampleValues": None,
            "GroupingSampleStd": None,
            "GroupingSampleMean": None,
            # the values here are just for initialization
            "GroupingSampleCV": {"sds_0": 1000, "sds_1": 1000},
            "MovingAverageGroupingSampleValues": None,
            "MovingAverageGroupingSampleStd": None,
            "MovingAverageGroupingSampleMean": None,
            # the values here are just for initialization
            "MovingAverageGroupingSampleCV": {"sds_0": 1000, "sds_1": 1000}
        }
        with open(os.path.join(self.post_analysis, "{}_simulation_result.json".format(self.config["SessionID"])), "w") as f:
            json.dump(result, f, indent=4)

    # Main function to run simulation by passing formal configuration to MCX bin.
    def run(self, idx):
        # make command and run
        for customizedCommand in self.config["CustomizedCommands"]:
            command = self.getCommand(idx, customizedCommand)
            # run
            sys.stdout.flush()
            currentDir = os.getcwd()
            os.chdir(self.config["BinaryPath"])
            # print("Current position to run MCX:\n", os.getcwd(), end="\n\n")
            # print("Command sent to MCX:\n{}".format(command), end="\n\n")
            print("∎∎ Start to run # {} ...".format(idx), end=" ")
            os.system(command)
            print("Finished !! ∎∎", end="\n\n")
            os.chdir(currentDir)
        # remove .jnii
        jniiOutputPathSet = glob(os.path.abspath(
            os.path.join(self.mcx_output, "*.jnii")))
        for jniiOutputPath in jniiOutputPathSet:
            os.remove(jniiOutputPath)

    def replay(self, volDim):
        # about paths of detected photon data
        detOutputPathSet = glob(os.path.join(self.mcx_output, "*.mch"))
        detOutputPathSet.sort(key=lambda x: int(
            x.split("_")[-1].replace(".mch", "")))

        self.makeMCXInput(designatedVolDim=volDim)
        customizedCommand = self.config["CustomizedCommands"][1]
        for i in range(len(detOutputPathSet)):
            command = self.getCommand(i, customizedCommand)
            # run
            sys.stdout.flush()
            currentDir = os.getcwd()
            os.chdir("../")
            os.chdir(self.config["BinaryPath"])
            # print("Current position to run MCX:\n", os.getcwd(), end="\n\n")
            # print("Command sent to MCX:\n{}".format(command), end="\n\n")
            print("∎∎ Start to run # {} ...".format(i), end=" ")
            os.system(command)
            print("Finished !! ∎∎", end="\n\n")
            os.chdir(currentDir)
        # remove .jnii
        jniiOutputPathSet = glob(os.path.abspath(
            os.path.join(self.mcx_output, "*.jnii")))
        for jniiOutputPath in jniiOutputPathSet:
            os.remove(jniiOutputPath)

    # Create the user-defined command line flags for mcx
    def getCommand(self, simOrder, customizedCommand):
        # basic setting
        self.jdatname = f'{self.config["SessionID"]}_{simOrder}_detp.jdat'
        sessionName = "{}_{}".format(self.config["SessionID"], simOrder)
        geometryFile = os.path.abspath(os.path.join(
            self.json_output, "input_{}.json".format(self.config["SessionID"])))
        root = os.path.join(os.path.abspath(self.session), "mcx_output")

        # make up command
        if os.name == "posix":
            # linux
            command = "./mcx"
        elif os.name == "nt":
            # windows
            command = "mcx.exe"
        else:
            command = "./mcx"
        command += " --session {} ".format(sessionName)
        command += "--input {} ".format(geometryFile)
        command += "--root {} ".format(root)
        command += "--gpu 1 "  # use first gpu
        # command += "--workload 55,45"
        command += "--autopilot 1 "
        command += "--photon {} ".format(self.config["PhotonNum"])
        command += "--repeat 1 "
        command += "--normalize 1 "
        command += "--bc aaaaar "
        command += "--unitinmm {} ".format(self.config["VoxelSize"])
        command += "--skipradius -2 "
        command += "--array 0 "
        command += "--dumpmask 0 "
        command += "--maxdetphoton {} ".format(3e7)
        command += "--srcfrom0 1 "
        command += "--saveseed 1 "
        command += "--debug P "
        if "mch" in customizedCommand:  # for replay
            customizedCommand = customizedCommand.replace("mch", os.path.abspath(
                os.path.join(self.mcx_output, "{}.mch".format(sessionName))))
        command += customizedCommand
        command += ">> log.txt"
        # print(command)
        return command

    def makeMCXInput(self, designatedVolDim=None):
        """

        Parameters
        ----------
        designatedVolDim : TYPE, optional
            If designatedVolDim is given, its form should be [XSize, YSize, ZSize] in mm.

        Returns
        -------
        None.

        """
        # set Session
        self.mcxInput["Session"]["ID"] = self.config["SessionID"]

        # set Domain Media (optical properties of tissue model)
        self.setDomainMedia()

        # set Domain Dim
        if designatedVolDim:
            self.mcxInput["Domain"]["Dim"] = [int(self.convertUnit(designatedVolDim[0])),
                                              int(self.convertUnit(
                                                  designatedVolDim[1])),
                                              int(self.convertUnit(
                                                  designatedVolDim[2]))
                                              ]
        else:
            vol = np.load(self.config["VolumePath"])
            self.mcxInput["Domain"]["Dim"] = list(vol.shape)

        # set Domain OriginType
        self.mcxInput["Domain"]["OriginType"] = 1

        # set Shapes
        self.mcxInput["Shapes"] = vol

        # set Optodes
        self.setOptodes()

        # save mcxInput to output/json_output
        jd.save(jd.encode(self.mcxInput, {'compression': 'zlib', 'base64': 1}),
                os.path.join(self.json_output, "input_{}.json".format(self.config["SessionID"])))
        self.mcxInput["Optode"]["Source"] = {"Type": "pencil",
                                             "Pos": self.mcxInput["Optode"]["Source"]["Pos"],
                                             "Dir": [0.0, 0.0, 1.0]}
        jd.save(jd.encode(self.mcxInput, {'compression': 'zlib', 'base64': 1}),
                os.path.join(self.json_output, "input_{}_forpreview.json".format(self.config["SessionID"])))

    def setDomainMedia(self):
        # 0: Fiber
        self.mcxInput["Domain"]["Media"][0]["n"] = self.modelParameters["OptParam"]["Fiber"]["n"]
        self.mcxInput["Domain"]["Media"][0]["g"] = self.modelParameters["OptParam"]["Fiber"]["g"]
        self.mcxInput["Domain"]["Media"][0]["mua"] = 0
        self.mcxInput["Domain"]["Media"][0]["mus"] = self.modelParameters["OptParam"]["Fiber"]["mus"]
        # 1: Air
        self.mcxInput["Domain"]["Media"][1]["n"] = self.modelParameters["OptParam"]["Air"]["n"]
        self.mcxInput["Domain"]["Media"][1]["g"] = self.modelParameters["OptParam"]["Air"]["g"]
        self.mcxInput["Domain"]["Media"][1]["mua"] = 0
        self.mcxInput["Domain"]["Media"][1]["mus"] = self.modelParameters["OptParam"]["Air"]["mus"]
        # 2: PLA
        self.mcxInput["Domain"]["Media"][2]["n"] = self.modelParameters["OptParam"]["PLA"]["n"]
        self.mcxInput["Domain"]["Media"][2]["g"] = self.modelParameters["OptParam"]["PLA"]["g"]
        self.mcxInput["Domain"]["Media"][2]["mua"] = 0
        self.mcxInput["Domain"]["Media"][2]["mus"] = self.modelParameters["OptParam"]["PLA"]["mus"]
        # 3:  Prism
        self.mcxInput["Domain"]["Media"][3]["n"] = self.modelParameters["OptParam"]["Prism"]["n"]
        self.mcxInput["Domain"]["Media"][3]["g"] = self.modelParameters["OptParam"]["Prism"]["g"]
        self.mcxInput["Domain"]["Media"][3]["mua"] = 0
        self.mcxInput["Domain"]["Media"][3]["mus"] = self.modelParameters["OptParam"]["Prism"]["mus"]
        # 4: Skin
        self.mcxInput["Domain"]["Media"][4]["n"] = self.modelParameters["OptParam"]["Skin"]["n"]
        self.mcxInput["Domain"]["Media"][4]["g"] = self.modelParameters["OptParam"]["Skin"]["g"]
        if "--save2pt 1" in str(self.config["CustomizedCommands"]):
            self.mcxInput["Domain"]["Media"][4]["mua"] = 4e4
            self.mcxInput["Domain"]["Media"][4]["mus"] = 1e-4
        else:
            self.mcxInput["Domain"]["Media"][4]["mua"] = 0
            self.mcxInput["Domain"]["Media"][4]["mus"] = self.modelParameters["OptParam"]["Skin"]["mus"]
        # 5: Fat
        self.mcxInput["Domain"]["Media"][5]["n"] = self.modelParameters["OptParam"]["Fat"]["n"]
        self.mcxInput["Domain"]["Media"][5]["g"] = self.modelParameters["OptParam"]["Fat"]["g"]
        self.mcxInput["Domain"]["Media"][5]["mua"] = 0
        self.mcxInput["Domain"]["Media"][5]["mus"] = self.modelParameters["OptParam"]["Fat"]["mus"]
        # 6: Muscle
        self.mcxInput["Domain"]["Media"][6]["n"] = self.modelParameters["OptParam"]["Muscle"]["n"]
        self.mcxInput["Domain"]["Media"][6]["g"] = self.modelParameters["OptParam"]["Muscle"]["g"]
        self.mcxInput["Domain"]["Media"][6]["mua"] = 0
        self.mcxInput["Domain"]["Media"][6]["mus"] = self.modelParameters["OptParam"]["Muscle"]["mus"]
        # 7: Muscle or IJV (Perturbed Region)
        if self.config["Type"].find("small") != -1:
            self.mcxInput["Domain"]["Media"][7]["n"] = self.modelParameters["OptParam"]["Muscle"]["n"]
            self.mcxInput["Domain"]["Media"][7]["g"] = self.modelParameters["OptParam"]["Muscle"]["g"]
            self.mcxInput["Domain"]["Media"][7]["mua"] = 0
            self.mcxInput["Domain"]["Media"][7]["mus"] = self.modelParameters["OptParam"]["Muscle"]["mus"]
        elif self.config["Type"].find("large") != -1:
            self.mcxInput["Domain"]["Media"][7]["n"] = self.modelParameters["OptParam"]["IJV"]["n"]
            self.mcxInput["Domain"]["Media"][7]["g"] = self.modelParameters["OptParam"]["IJV"]["g"]
            self.mcxInput["Domain"]["Media"][7]["mua"] = 0
            self.mcxInput["Domain"]["Media"][7]["mus"] = self.modelParameters["OptParam"]["IJV"]["mus"]
        else:
            raise Exception("Something wrong in your config[VolumePath] !")
        # 8: IJV
        self.mcxInput["Domain"]["Media"][8]["n"] = self.modelParameters["OptParam"]["IJV"]["n"]
        self.mcxInput["Domain"]["Media"][8]["g"] = self.modelParameters["OptParam"]["IJV"]["g"]
        self.mcxInput["Domain"]["Media"][8]["mua"] = 0
        self.mcxInput["Domain"]["Media"][8]["mus"] = self.modelParameters["OptParam"]["IJV"]["mus"]
        # 9: CCA
        self.mcxInput["Domain"]["Media"][9]["n"] = self.modelParameters["OptParam"]["CCA"]["n"]
        self.mcxInput["Domain"]["Media"][9]["g"] = self.modelParameters["OptParam"]["CCA"]["g"]
        self.mcxInput["Domain"]["Media"][9]["mua"] = 0
        self.mcxInput["Domain"]["Media"][9]["mus"] = self.modelParameters["OptParam"]["CCA"]["mus"]

    def setOptodes(self):
        # detector (help to extend to left and right)
        modelX = self.mcxInput["Domain"]["Dim"][0]
        modelY = self.mcxInput["Domain"]["Dim"][1]
        detHolderZ = self.convertUnit(
            self.modelParameters["HardwareParam"]["Detector"]["Holder"]["ZSize"])
        prismZ = self.convertUnit(
            self.modelParameters["HardwareParam"]["Detector"]["Prism"]["ZSize"])
        for fiber in self.modelParameters["HardwareParam"]["Detector"]["Fiber"]:
            # right - bottom
            self.mcxInput["Optode"]["Detector"].append({"R": self.convertUnit(fiber["Radius"]),
                                                        "Pos": [modelX/2 + self.convertUnit(fiber["SDS"]),
                                                                modelY/2 - 2 *
                                                                self.convertUnit(
                                                                    fiber["Radius"]),
                                                                detHolderZ - prismZ
                                                                ]
                                                        })
            # left - bottom
            self.mcxInput["Optode"]["Detector"].append({"R": self.convertUnit(fiber["Radius"]),
                                                        "Pos": [modelX/2 - self.convertUnit(fiber["SDS"]),
                                                                modelY/2 - 2 *
                                                                self.convertUnit(
                                                                    fiber["Radius"]),
                                                                detHolderZ - prismZ
                                                                ]
                                                        })
            # right - middle (original)
            self.mcxInput["Optode"]["Detector"].append({"R": self.convertUnit(fiber["Radius"]),
                                                        "Pos": [modelX/2 + self.convertUnit(fiber["SDS"]),
                                                                modelY/2,
                                                                detHolderZ - prismZ
                                                                ]
                                                        })
            # left - middle
            self.mcxInput["Optode"]["Detector"].append({"R": self.convertUnit(fiber["Radius"]),
                                                        "Pos": [modelX/2 - self.convertUnit(fiber["SDS"]),
                                                                modelY/2,
                                                                detHolderZ - prismZ
                                                                ]
                                                        })
            # right - top
            self.mcxInput["Optode"]["Detector"].append({"R": self.convertUnit(fiber["Radius"]),
                                                        "Pos": [modelX/2 + self.convertUnit(fiber["SDS"]),
                                                                modelY/2 + 2 *
                                                                self.convertUnit(
                                                                    fiber["Radius"]),
                                                                detHolderZ - prismZ
                                                                ]
                                                        })
            # left - top
            self.mcxInput["Optode"]["Detector"].append({"R": self.convertUnit(fiber["Radius"]),
                                                        "Pos": [modelX/2 - self.convertUnit(fiber["SDS"]),
                                                                modelY/2 + 2 *
                                                                self.convertUnit(
                                                                    fiber["Radius"]),
                                                                detHolderZ - prismZ
                                                                ]
                                                        })

        # source
        # sampling angles based on the radiation pattern distribution
        currentDir = os.getcwd()
        os.chdir(self.modelParameters["HardwareParam"]
                 ["Source"]["Beam"]["ProfilePath"])
        ledProfileIn3D = np.genfromtxt(
            "LED_profile_in3D_pfForm_0to89.csv", delimiter=",")
        os.chdir(currentDir)
        angle = ledProfileIn3D[:, 0]
        cdf = np.cumsum(ledProfileIn3D[:, 1])
        inversecdf = PchipInterpolator(cdf, angle)
        samplingSeeds = np.linspace(0, 1, num=int(
            self.modelParameters["HardwareParam"]["Source"]["LED"]["SamplingNumOfRadiationPattern"]))
        samplingAngles = inversecdf(samplingSeeds)
        # set source position
        self.mcxInput["Optode"]["Source"]["Pos"] = [modelX/2,
                                                    modelY/2,
                                                    # need to minus a very small value here. (if not, irradiating distribution will disappear)
                                                    self.convertUnit(
                                                        self.modelParameters["HardwareParam"]["Source"]["Holder"]["ZSize"])-1e-4
                                                    ]
        # set source type
        self.mcxInput["Optode"]["Source"]["Type"] = self.modelParameters["HardwareParam"]["Source"]["Beam"]["Type"]
        # set additional parameters about led arrangement (please refer to the hackMD-ijvNotebooks records on 2021/04/09)
        self.mcxInput["Optode"]["Source"]["Param1"] = [int(self.modelParameters["HardwareParam"]["Source"]["LED"]["SamplingNumOfRadiationPattern"]),
                                                       self.convertUnit(
                                                           self.modelParameters["HardwareParam"]["Source"]["LED"]["XSize"]),
                                                       self.convertUnit(
                                                           self.modelParameters["HardwareParam"]["Source"]["LED"]["YSize"]),
                                                       0
                                                       ]
        self.mcxInput["Optode"]["Source"]["Param2"] = [0,
                                                       0,
                                                       self.convertUnit(
                                                           self.modelParameters["HardwareParam"]["Source"]["Holder"]["IrraWinRadius"]),
                                                       self.convertUnit(
                                                           self.modelParameters["HardwareParam"]["Source"]["LED"]["Surf2Win"])
                                                       ]
        # set formal pattern
        self.mcxInput["Optode"]["Source"]["Pattern"] = {}
        self.mcxInput["Optode"]["Source"]["Pattern"]["Nx"] = int(
            self.modelParameters["HardwareParam"]["Source"]["LED"]["SamplingNumOfRadiationPattern"])
        self.mcxInput["Optode"]["Source"]["Pattern"]["Ny"] = 1
        self.mcxInput["Optode"]["Source"]["Pattern"]["Nz"] = 1
        self.mcxInput["Optode"]["Source"]["Pattern"]["Data"] = np.deg2rad(
            samplingAngles).tolist()

    def convertUnit(self, length):
        """
        Do unit conversion.

        Parameters
        ----------
        length : int or float
            The unit of length is [mm].

        Returns
        -------
        numGrid : int or float
            Number of grid, for MCX simulation.

        """
        numGrid = length / self.config["VoxelSize"]
        return numGrid

    def NA_adjust(self, NA):
        detOutput = jd.load(os.path.join(self.mcx_output, self.jdatname))
        info = detOutput["MCXData"]["Info"]
        photonData = detOutput["MCXData"]["PhotonData"]

        layer0_refract_index = info["Media"][2]['n']  # fiber
        layer1_refract_index = info["Media"][3]['n']  # prism
        cz = photonData["v"][:, 2]
        After_refract_theta_z = np.arccos(cz)
        NA_Angle = np.arcsin(NA/layer1_refract_index)
        Before_refract_theta_z = np.arcsin(
            layer0_refract_index*np.sin(After_refract_theta_z)/layer1_refract_index)
        valid = np.where(Before_refract_theta_z <= NA_Angle)[0]
        DetectedPhoton = valid.shape[0]

        info["DetectedPhoton"] = DetectedPhoton
        for k in photonData.keys():
            photonData[k] = photonData[k][valid, :]

        detOutput = {"MCXData": {"Info": info,
                                 "PhotonData": photonData}}
        jd.save(detOutput, os.path.join(self.mcx_output, self.jdatname))


# %% Run
if __name__ == "__main__":

    # parameters
    sessionID = "test"

    # initialize
    simulator = MCX(sessionID)

    # run forward mcx
    simulator.run(1)
