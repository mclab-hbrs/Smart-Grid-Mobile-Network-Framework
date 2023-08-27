'''Programm representing an IEC 61850 MMS Server, e.g. a Substation.'''
import os
import time
from datetime import datetime
import calendar
import csv

import iec61850 as iec

class gvar():
    # server settings and stats
    tcpPort = 61850
    hostname = "127.0.0.1"

    # Data Model
    iedServer = []
    iedModel = []
    LD_iedModel = []

    counter_MV = 0
    counter_LV = 1

    # Parameter Devices
    IedModelName = os.environ.get('IedModelName')
    DeviceName = os.environ.get('DeviceName')
    # LLN0
    LLN0_vendor = "Manufacturer 1"
    LLN0_d = "XYZ"
    LLN0_swRev = "v1.2"
    LLN0_configRev = "636228633875233607"
    # LPHD1
    LPHD1_vendor = "Manufacturer 2"
    LPHD1_phy_health = 1

    dictUpdateVal =  {}
    
    dataset = []
    dataset_index = 0

def create_new_mv_device():
    #####################################
    # Creation of mandatory devices
    #####################################
    # for CDC options see:
    # https://support.mz-automation.de/doc/libiec61850/c/latest/group__COMMON__DATA__CLASSES.html

    # Logical node (LN): an instance of a logical node class maps to a single MMS NamedVariable. Source "Description of IEC 61850 Communication" p.13
    LD_iedModel = iec.LogicalDevice_create("MV_"+str(gvar.counter_MV), gvar.iedModel)
    # LLN0
    LN_LLN0     = iec.LogicalNode_create("LLN0", LD_iedModel)
    # LLN0 - DOs / CDCs
    DO_LLN0_Beh     = iec.CDC_ENS_create("Beh", iec.toModelNode(LN_LLN0), 0)
    DA_LLN0_Beh_stVal = iec.ModelNode_getChild(iec.toModelNode(DO_LLN0_Beh), "stVal")
    DO_LLN0_Loc     = iec.CDC_SPS_create("Loc", iec.toModelNode(LN_LLN0), 0)
    DO_LLN0_Mod     = iec.CDC_INC_create("Mod", iec.toModelNode(LN_LLN0), 0, 1)
    DA_LLN0_Mod_stVal = iec.ModelNode_getChild(iec.toModelNode(DO_LLN0_Mod), "stVal")

    # Following data initialization, discovered logical nodes are queried for updates. A special attributes called LLN0$DC$NamPlt$configRev is regularly checked.
    # The value of the attribute has to be changed at least on any semantic change of the data model of the logical device that may affect interpretation of the data by the client.
    # The read service requested in all cases an object LLN0$DC$NamPlt$configRev. Source: "Description of IEC 61850 Communication" p.54
    # Das Attribut configRev muss nur im LLN0 verwendet werden. Source: "Modellierungsrichtlinie und Mustermodellierung mit der SCL" p.85
    # Option: iec.CDC_OPTION_AC_LN0_M includes "configRev", iec.CDC_OPTION_DESC includes "d"
    DO_LLN0_NamPlt = iec.CDC_LPL_create("NamPlt", iec.toModelNode(LN_LLN0), (iec.CDC_OPTION_AC_LN0_M+iec.CDC_OPTION_DESC))
    # ak_LPL LPL
    DA_LLNO_NamPlt_vendor = iec.ModelNode_getChild(iec.toModelNode(DO_LLN0_NamPlt), "vendor")
    DA_LLNO_NamPlt_d = iec.ModelNode_getChild(iec.toModelNode(DO_LLN0_NamPlt), "d")
    DA_LLNO_NamPlt_swRev = iec.ModelNode_getChild(iec.toModelNode(DO_LLN0_NamPlt), "swRev")
    DA_LLNO_NamPlt_configRev = iec.ModelNode_getChild(iec.toModelNode(DO_LLN0_NamPlt), "configRev") # indicates if config of substation changed

    # Logical device (LD): an instance of a logical device object is mapped to an MMS domain object. Source "Description of IEC 61850 Communication" p.13
    LN_LPHD1 = iec.LogicalNode_create("LPHD1", LD_iedModel)
    # LPHD1 - DOs / CDCs
    DO_LPHD1_PhyHealth = iec.CDC_INS_create("PhyHealth", iec.toModelNode(LN_LPHD1), 0)
    DA_LPHD1_PhyHealth_stVal = iec.ModelNode_getChild(iec.toModelNode(DO_LPHD1_PhyHealth), "stVal")
    DA_LPHD1_PhyHealth_t = iec.ModelNode_getChild(iec.toModelNode(DO_LPHD1_PhyHealth), "t")
    DO_LPHD1_PhyNam = iec.CDC_DPL_create("PhyNam", iec.toModelNode(LN_LPHD1), 0)  #DPL (Device name plate)
    DA_LPHD1_PhyName_vendor = iec.ModelNode_getChild(iec.toModelNode(DO_LPHD1_PhyNam), "vendor")
    DO_LPHD1_Proxy = iec.CDC_SPS_create("Proxy", iec.toModelNode(LN_LPHD1), 0)

    # Set values for LLN0 and LPHD1
    # LLN0
    iec.DataAttribute_setValue(iec.toDataAttribute(DA_LLNO_NamPlt_vendor), iec.MmsValue_newVisibleString(gvar.LLN0_vendor))
    iec.DataAttribute_setValue(iec.toDataAttribute(DA_LLNO_NamPlt_d), iec.MmsValue_newVisibleString(gvar.LLN0_d))
    iec.DataAttribute_setValue(iec.toDataAttribute(DA_LLNO_NamPlt_swRev), iec.MmsValue_newVisibleString(gvar.LLN0_swRev))
    iec.DataAttribute_setValue(iec.toDataAttribute(DA_LLNO_NamPlt_configRev), iec.MmsValue_newVisibleString(gvar.LLN0_configRev))

    # LPHD1
    iec.DataAttribute_setValue(iec.toDataAttribute(DA_LPHD1_PhyName_vendor), iec.MmsValue_newVisibleString(gvar.LPHD1_vendor))
    iec.DataAttribute_setValue(iec.toDataAttribute(DA_LPHD1_PhyHealth_stVal), iec.MmsValue_newInteger(gvar.LPHD1_phy_health))
    iec.DataAttribute_setValue(iec.toDataAttribute(DA_LPHD1_PhyHealth_t), iec.MmsValue_newUtcTimeByMsTime(get_UTC_timestamp_uint64()))

    ##################
    # Medium Voltage #
    ##################
    
    #############################
    # MMXU E1_MMXU (Typ: 110kV E1)
    LN_MMXU_MV = iec.LogicalNode_create("MMXU_MV", LD_iedModel)
    # MMXU - DOs / CDCs
    DO_MMXU0_Mod = iec.CDC_INC_create("Mod", iec.toModelNode(LN_MMXU_MV), 0, 1)
    DO_MMXU0_NamPlt = iec.CDC_DPL_create("NamPlt", iec.toModelNode(LN_MMXU_MV), 0)
    DO_MMXU0_Health = iec.CDC_INS_create("Health", iec.toModelNode(LN_MMXU_MV), 0)
    DO_MMXU0_Beh = iec.CDC_INS_create("Beh", iec.toModelNode(LN_MMXU_MV), 0)

    # TotW = Total Active Power
    DO_MMXU0_TotW = iec.CDC_MV_create("TotW", iec.toModelNode(LN_MMXU_MV), 0, False)
    gvar.dictUpdateVal["MMXU_MV_TotW_t"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU0_TotW), "t")
    gvar.dictUpdateVal["MMXU_MV_TotW_f"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU0_TotW), "mag.f")

    # TotVAr = Total Reactive Power
    DO_MMXU0_TotVar = iec.CDC_MV_create("TotVAr", iec.toModelNode(LN_MMXU_MV), 0, False)
    gvar.dictUpdateVal["MMXU_MV_TotVar_t"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU0_TotVar), "t")
    gvar.dictUpdateVal["MMXU_MV_TotVar_f"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU0_TotVar), "mag.f")

    # Frequency
    DO_MMXU0_Hz = iec.CDC_MV_create("Hz", iec.toModelNode(LN_MMXU_MV), iec.CDC_OPTION_RANGE, False) # ranged
    gvar.dictUpdateVal["MMXU_MV_Hz_t"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU0_Hz), "t")
    gvar.dictUpdateVal["MMXU_MV_Hz_f"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU0_Hz), "mag.f")

    #Phase to phase related measured values of a three-phase system (DEL)
    #DO_MMXU0_PPV = iec.CDC_DEL_create("PPV", iec.toModelNode(LN_MMXU_MV), 0) # ranged

    #Phase to ground/neutral related measured values of a three-phase system (WYE)
    DO_MMXU0_PhV = iec.CDC_WYE_create("PhV", iec.toModelNode(LN_MMXU_MV), 0) # ranged
    gvar.dictUpdateVal["MMXU_MV_PhV_phsA_t"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU0_PhV), "phsA.t")
    gvar.dictUpdateVal["MMXU_MV_PhV_phsA_f"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU0_PhV), "phsA.cVal.mag.f")
    gvar.dictUpdateVal["MMXU_MV_PhV_phsB_t"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU0_PhV), "phsB.t")
    gvar.dictUpdateVal["MMXU_MV_PhV_phsB_f"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU0_PhV), "phsB.cVal.mag.f")
    gvar.dictUpdateVal["MMXU_MV_PhV_phsC_t"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU0_PhV), "phsC.t")
    gvar.dictUpdateVal["MMXU_MV_PhV_phsC_f"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU0_PhV), "phsC.cVal.mag.f")

    # Phase currents (IL1, IL2, IL3)
    DO_MMXU0_A = iec.CDC_WYE_create("A", iec.toModelNode(LN_MMXU_MV), 0) # ranged
    gvar.dictUpdateVal["MMXU_MV_A_phsA_t"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU0_A), "phsA.t")
    gvar.dictUpdateVal["MMXU_MV_A_phsA_f"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU0_A), "phsA.cVal.mag.f")
    gvar.dictUpdateVal["MMXU_MV_A_phsB_t"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU0_A), "phsB.t")
    gvar.dictUpdateVal["MMXU_MV_A_phsB_f"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU0_A), "phsB.cVal.mag.f")
    gvar.dictUpdateVal["MMXU_MV_A_phsC_t"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU0_A), "phsC.t")
    gvar.dictUpdateVal["MMXU_MV_A_phsC_f"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU0_A), "phsC.cVal.mag.f")

    DS_MMXU_MV = iec.DataSet_create(gvar.DeviceName + "_DS_" + "MMXU_MV", LN_MMXU_MV)
    iec.DataSetEntry_create(DS_MMXU_MV, "MMXU_MV$MX$TotW$mag", -1, None)
    iec.DataSetEntry_create(DS_MMXU_MV, "MMXU_MV$MX$TotVAr$mag", -1, None)
    iec.DataSetEntry_create(DS_MMXU_MV, "MMXU_MV$MX$Hz$mag", -1, None)

    iec.DataSetEntry_create(DS_MMXU_MV, "MMXU_MV$MX$PhV$phsA$cVal", -1, None)
    iec.DataSetEntry_create(DS_MMXU_MV, "MMXU_MV$MX$PhV$phsB$cVal", -1, None)
    iec.DataSetEntry_create(DS_MMXU_MV, "MMXU_MV$MX$PhV$phsC$cVal", -1, None)

    iec.DataSetEntry_create(DS_MMXU_MV, "MMXU_MV$MX$A$phsA$cVal", -1, None)
    iec.DataSetEntry_create(DS_MMXU_MV, "MMXU_MV$MX$A$phsB$cVal", -1, None)
    iec.DataSetEntry_create(DS_MMXU_MV, "MMXU_MV$MX$A$phsC$cVal", -1, None)

    ReportContorlBlock_MV =  iec.ReportControlBlock_create(gvar.DeviceName+str(gvar.counter_MV) + "_RP_" + "MMXU_MV", LN_MMXU_MV, "MMXU_MV_"+str(gvar.counter_MV), False, gvar.DeviceName+str(gvar.counter_MV) + "_DS_" + "MMXU_MV" , 1, iec.TRG_OPT_DATA_CHANGED | iec.TRG_OPT_QUALITY_CHANGED | iec.TRG_OPT_GI | iec.TRG_OPT_DATA_UPDATE, 0, 0, 60000)
    gvar.counter_MV += 1

def create_new_lv_device():
    #####################################
    # Creation of mandatory devices
    #####################################
    # for CDC options see:
    # https://support.mz-automation.de/doc/libiec61850/c/latest/group__COMMON__DATA__CLASSES.html

    # Logical node (LN): an instance of a logical node class maps to a single MMS NamedVariable. Source "Description of IEC 61850 Communication" p.13
    LD_iedModel = iec.LogicalDevice_create("LV_"+str(gvar.counter_LV), gvar.iedModel)
    # LLN0
    LN_LLN0     = iec.LogicalNode_create("LLN0", LD_iedModel)
    # LLN0 - DOs / CDCs
    DO_LLN0_Beh     = iec.CDC_ENS_create("Beh", iec.toModelNode(LN_LLN0), 0)
    DA_LLN0_Beh_stVal = iec.ModelNode_getChild(iec.toModelNode(DO_LLN0_Beh), "stVal")
    DO_LLN0_Loc     = iec.CDC_SPS_create("Loc", iec.toModelNode(LN_LLN0), 0)
    DO_LLN0_Mod     = iec.CDC_INC_create("Mod", iec.toModelNode(LN_LLN0), 0, 1)
    DA_LLN0_Mod_stVal = iec.ModelNode_getChild(iec.toModelNode(DO_LLN0_Mod), "stVal")

    # Following data initialization, discovered logical nodes are queried for updates. A special attributes called LLN0$DC$NamPlt$configRev is regularly checked.
    # The value of the attribute has to be changed at least on any semantic change of the data model of the logical device that may affect interpretation of the data by the client.
    # The read service requested in all cases an object LLN0$DC$NamPlt$configRev. Source: "Description of IEC 61850 Communication" p.54
    # Das Attribut configRev muss nur im LLN0 verwendet werden. Source: "Modellierungsrichtlinie und Mustermodellierung mit der SCL" p.85
    # Option: iec.CDC_OPTION_AC_LN0_M includes "configRev", iec.CDC_OPTION_DESC includes "d"
    DO_LLN0_NamPlt = iec.CDC_LPL_create("NamPlt", iec.toModelNode(LN_LLN0), (iec.CDC_OPTION_AC_LN0_M+iec.CDC_OPTION_DESC))
    # ak_LPL LPL
    DA_LLNO_NamPlt_vendor = iec.ModelNode_getChild(iec.toModelNode(DO_LLN0_NamPlt), "vendor")
    DA_LLNO_NamPlt_d = iec.ModelNode_getChild(iec.toModelNode(DO_LLN0_NamPlt), "d")
    DA_LLNO_NamPlt_swRev = iec.ModelNode_getChild(iec.toModelNode(DO_LLN0_NamPlt), "swRev")
    DA_LLNO_NamPlt_configRev = iec.ModelNode_getChild(iec.toModelNode(DO_LLN0_NamPlt), "configRev") # indicates if config of substation changed

    # Logical device (LD): an instance of a logical device object is mapped to an MMS domain object. Source "Description of IEC 61850 Communication" p.13
    LN_LPHD1 = iec.LogicalNode_create("LPHD1", LD_iedModel)
    # LPHD1 - DOs / CDCs
    DO_LPHD1_PhyHealth = iec.CDC_INS_create("PhyHealth", iec.toModelNode(LN_LPHD1), 0)
    DA_LPHD1_PhyHealth_stVal = iec.ModelNode_getChild(iec.toModelNode(DO_LPHD1_PhyHealth), "stVal")
    DA_LPHD1_PhyHealth_t = iec.ModelNode_getChild(iec.toModelNode(DO_LPHD1_PhyHealth), "t")
    DO_LPHD1_PhyNam = iec.CDC_DPL_create("PhyNam", iec.toModelNode(LN_LPHD1), 0)  #DPL (Device name plate)
    DA_LPHD1_PhyName_vendor = iec.ModelNode_getChild(iec.toModelNode(DO_LPHD1_PhyNam), "vendor")
    DO_LPHD1_Proxy = iec.CDC_SPS_create("Proxy", iec.toModelNode(LN_LPHD1), 0)

    # Set values for LLN0 and LPHD1
    # LLN0
    iec.DataAttribute_setValue(iec.toDataAttribute(DA_LLNO_NamPlt_vendor), iec.MmsValue_newVisibleString(gvar.LLN0_vendor))
    iec.DataAttribute_setValue(iec.toDataAttribute(DA_LLNO_NamPlt_d), iec.MmsValue_newVisibleString(gvar.LLN0_d))
    iec.DataAttribute_setValue(iec.toDataAttribute(DA_LLNO_NamPlt_swRev), iec.MmsValue_newVisibleString(gvar.LLN0_swRev))
    iec.DataAttribute_setValue(iec.toDataAttribute(DA_LLNO_NamPlt_configRev), iec.MmsValue_newVisibleString(gvar.LLN0_configRev))

    # LPHD1
    iec.DataAttribute_setValue(iec.toDataAttribute(DA_LPHD1_PhyName_vendor), iec.MmsValue_newVisibleString(gvar.LPHD1_vendor))
    iec.DataAttribute_setValue(iec.toDataAttribute(DA_LPHD1_PhyHealth_stVal), iec.MmsValue_newInteger(gvar.LPHD1_phy_health))
    iec.DataAttribute_setValue(iec.toDataAttribute(DA_LPHD1_PhyHealth_t), iec.MmsValue_newUtcTimeByMsTime(get_UTC_timestamp_uint64()))

    ##################
    # Low Voltage    #
    ##################

    #############################
    # MMXU K2_MMXU (Typ: 10kV K2) 
    LN_MMXU_LV = iec.LogicalNode_create("MMXU_LV_"+str(gvar.counter_LV), LD_iedModel)
    # MMXU - DOs / CDCs
    #DO_MMXU_LV_1_Mod = iec.CDC_INC_create("Mod", iec.toModelNode(LN_MMXU_LV_1), 0, 1)
    #DO_MMXU_LV_1_NamPlt = iec.CDC_DPL_create("NamPlt", iec.toModelNode(LN_MMXU_LV_1), 0)
    #DO_MMXU_LV_1_Health = iec.CDC_INS_create("Health", iec.toModelNode(LN_MMXU_LV_1), 0)
    #DO_MMXU_LV_1_Beh = iec.CDC_INS_create("Beh", iec.toModelNode(LN_MMXU_LV_1), 0)

    #Phase to ground/neutral related measured values of a three-phase system (WYE)
    DO_MMXU_LV_PhV = iec.CDC_WYE_create("PhV", iec.toModelNode(LN_MMXU_LV), 0) # ranged
    gvar.dictUpdateVal["MMXU_LV_"+str(gvar.counter_LV)+"_PhV_phsA_t"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU_LV_PhV), "phsA.t")
    gvar.dictUpdateVal["MMXU_LV_"+str(gvar.counter_LV)+"_PhV_phsA_f"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU_LV_PhV), "phsA.cVal.mag.f")
    gvar.dictUpdateVal["MMXU_LV_"+str(gvar.counter_LV)+"_PhV_phsB_t"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU_LV_PhV), "phsB.t")
    gvar.dictUpdateVal["MMXU_LV_"+str(gvar.counter_LV)+"_PhV_phsB_f"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU_LV_PhV), "phsB.cVal.mag.f")
    gvar.dictUpdateVal["MMXU_LV_"+str(gvar.counter_LV)+"_PhV_phsC_t"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU_LV_PhV), "phsC.t")
    gvar.dictUpdateVal["MMXU_LV_"+str(gvar.counter_LV)+"_PhV_phsC_f"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU_LV_PhV), "phsC.cVal.mag.f")

    # Phase currents (IL1, IL2, IL3)
    DO_MMXU_LV_A = iec.CDC_WYE_create("A", iec.toModelNode(LN_MMXU_LV), 0) # ranged
    gvar.dictUpdateVal["MMXU_LV_"+str(gvar.counter_LV)+"_A_phsA_t"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU_LV_A), "phsA.t")
    gvar.dictUpdateVal["MMXU_LV_"+str(gvar.counter_LV)+"_A_phsA_f"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU_LV_A), "phsA.cVal.mag.f")
    gvar.dictUpdateVal["MMXU_LV_"+str(gvar.counter_LV)+"_A_phsB_t"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU_LV_A), "phsB.t")
    gvar.dictUpdateVal["MMXU_LV_"+str(gvar.counter_LV)+"_A_phsB_f"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU_LV_A), "phsB.cVal.mag.f")
    gvar.dictUpdateVal["MMXU_LV_"+str(gvar.counter_LV)+"_A_phsC_t"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU_LV_A), "phsC.t")
    gvar.dictUpdateVal["MMXU_LV_"+str(gvar.counter_LV)+"_A_phsC_f"] = iec.ModelNode_getChild(iec.toModelNode(DO_MMXU_LV_A), "phsC.cVal.mag.f")

    DS_MMXU_LV = iec.DataSet_create(gvar.DeviceName + "_DS_" + "MMXU_LV_"+str(gvar.counter_LV), LN_MMXU_LV)
    iec.DataSetEntry_create(DS_MMXU_LV, "MMXU_LV_"+str(gvar.counter_LV)+"$MX$PhV$phsA$cVal", -1, None)
    iec.DataSetEntry_create(DS_MMXU_LV, "MMXU_LV_"+str(gvar.counter_LV)+"$MX$PhV$phsB$cVal", -1, None)
    iec.DataSetEntry_create(DS_MMXU_LV, "MMXU_LV_"+str(gvar.counter_LV)+"$MX$PhV$phsC$cVal", -1, None)

    iec.DataSetEntry_create(DS_MMXU_LV, "MMXU_LV_"+str(gvar.counter_LV)+"$MX$A$phsA$cVal", -1, None)
    iec.DataSetEntry_create(DS_MMXU_LV, "MMXU_LV_"+str(gvar.counter_LV)+"$MX$A$phsB$cVal", -1, None)
    iec.DataSetEntry_create(DS_MMXU_LV, "MMXU_LV_"+str(gvar.counter_LV)+"$MX$A$phsC$cVal", -1, None)

    ReportContorlBlock_LV =  iec.ReportControlBlock_create(gvar.DeviceName+str(gvar.counter_LV) + "_RP_" + "MMXU_LV_"+str(gvar.counter_LV), LN_MMXU_LV, "MMXU_LV_"+str(gvar.counter_LV)+"_1", False, gvar.DeviceName+str(gvar.counter_LV)+ "_DS_" + "MMXU_LV_"+str(gvar.counter_LV), 1, iec.TRG_OPT_DATA_CHANGED | iec.TRG_OPT_QUALITY_CHANGED | iec.TRG_OPT_GI | iec.TRG_OPT_DATA_UPDATE, 0, 0, 60000)
    gvar.counter_LV += 1
    

def create_ied_model_device():

    #####################################
    # Creation of IED Model Object
    #####################################
    gvar.iedModel = iec.IedModel_create(gvar.IedModelName+"_")

    #####################################
    # Creation of optional Devices
    #####################################

    create_new_lv_device()
    create_new_lv_device()
    create_new_lv_device()
    create_new_mv_device()
    print("IED model complete")


def get_UTC_timestamp_uint64():
    # Get current time and convert to uint64_t
    # Consider correct offset
    offset_summer_time = 7200000
    current_time = datetime.now()
    current_time_uint64_t = calendar.timegm(current_time.utctimetuple())*1000
    return current_time_uint64_t - offset_summer_time

def update_IED_attr():
    ######################
    # set values
    # Iterate through data vars
    for var in gvar.dataset[gvar.dataset_index].keys():
        iec.IedServer_updateFloatAttributeValue(gvar.iedServer, iec.toDataAttribute(gvar.dictUpdateVal.get(var)), float(gvar.dataset[gvar.dataset_index][var]))      

    ######################
    # update all timestamps
    # Iterate through timestamp vars
    var_list_timestamps = [x for x in gvar.dictUpdateVal.keys() if x[-1] == ('t')]
    for var in var_list_timestamps:
        iec.IedServer_updateUTCTimeAttributeValue(gvar.iedServer, iec.toDataAttribute(gvar.dictUpdateVal.get(var)), get_UTC_timestamp_uint64())
    
    if gvar.dataset_index + 1 >= len(gvar.dataset):
        gvar.dataset_index = 0
    else:
        gvar.dataset_index += 1
    return

def server_routine():
    ''' Main function for starting IEC 61850 MMS Server '''
    # build IED Model
    create_ied_model_device()

    # build IED Server with the model
    gvar.iedServer = iec.IedServer_create(gvar.iedModel)

    iec.IedServer_start(gvar.iedServer, gvar.tcpPort)

    # optional parameter
    iec.IedServer_setServerIdentity(gvar.iedServer,"IED Vendor","XY","1.2.3")

    # read dataset
    csv_reader = csv.DictReader(open('sample_data.csv'))
    for row in csv_reader:
        gvar.dataset.append(next(csv_reader)) 

    while True:
        # Clearing the Screen
        os.system('clear')
        
        iec.IedServer_lockDataModel(gvar.iedServer)
        update_IED_attr()
        iec.IedServer_unlockDataModel(gvar.iedServer)

        print(time.strftime("%H:%M:%S")+": Server running")
        print("----------------- total measured values -----------------")
        print("Total Watt: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_MV_TotW_f"))),3))+" W")
        print("Total VAr: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_MV_TotVar_f"))),3))+" V")
        print("Frequency: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_MV_Hz_f"))),3))+" Hz")
        print("----------------- medium voltage output -----------------")
        print("Current Phase 1: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_MV_PhV_phsA_f"))),3))+" kV")
        print("Current Phase 2: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_MV_PhV_phsB_f"))),3))+" kV")
        print("Current Phase 3: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_MV_PhV_phsC_f"))),3))+" kV")
        print("Current Phase 1: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_MV_A_phsA_f"))),3))+" A")
        print("Current Phase 2: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_MV_A_phsB_f"))),3))+" A")
        print("Current Phase 3: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_MV_A_phsC_f"))),3))+" A")
        print("----------------- low voltage output -----------------")
        print("Current Phase 1: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_LV_1_PhV_phsA_f"))),3))+" kV")
        print("Current Phase 2: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_LV_1_PhV_phsB_f"))),3))+" kV")
        print("Current Phase 3: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_LV_1_PhV_phsC_f"))),3))+" kV")
        print("Current Phase 1: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_LV_1_A_phsA_f"))),3))+" A")
        print("Current Phase 2: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_LV_1_A_phsB_f"))),3))+" A")
        print("Current Phase 3: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_LV_1_A_phsC_f"))),3))+" A")
        print("----------------- low voltage output -----------------")
        print("Current Phase 1: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_LV_2_PhV_phsA_f"))),3))+" kV")
        print("Current Phase 2: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_LV_2_PhV_phsB_f"))),3))+" kV")
        print("Current Phase 3: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_LV_2_PhV_phsC_f"))),3))+" kV")
        print("Current Phase 1: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_LV_2_A_phsA_f"))),3))+" A")
        print("Current Phase 2: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_LV_2_A_phsB_f"))),3))+" A")
        print("Current Phase 3: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_LV_2_A_phsC_f"))),3))+" A")
        print("----------------- low voltage output -----------------")
        print("Current Phase 1: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_LV_3_PhV_phsA_f"))),3))+" kV")
        print("Current Phase 2: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_LV_3_PhV_phsB_f"))),3))+" kV")
        print("Current Phase 3: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_LV_3_PhV_phsC_f"))),3))+" kV")
        print("Current Phase 1: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_LV_3_A_phsA_f"))),3))+" A")
        print("Current Phase 2: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_LV_3_A_phsB_f"))),3))+" A")
        print("Current Phase 3: "+str(round(iec.IedServer_getFloatAttributeValue(gvar.iedServer,iec.toDataAttribute(gvar.dictUpdateVal.get("MMXU_LV_3_A_phsC_f"))),3))+" A")
        time.sleep(60) 

server_routine()