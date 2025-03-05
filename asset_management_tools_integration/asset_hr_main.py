from .EZ_Office_Inventory.ezOfficeInventoryUtils import *
from .InvGate.invGateApiUtils import *
from .Servicenow.servicenowApiUtils import *
from .Zoho.zohoApiUtil import *
from .Asset_Infinity.assetInfinity import *
from .EZ_Office_Inventory.ezOfficeInventoryUtils import *
from .Asset_Sonar.assetSonarUtils import *
from .Upkeep.upKeepUtils import *
from .SuperOps.SuperOpsUtils import *
from .ConnectTeam.connectTeamUtils import *
from .Workable.workableUtils import *
from .Hector.hectorUtils import *

def call_tool_api(tool, organization_id, body):
    tool_functions = {
        "servicenow": fetch_and_store_servicenow_data,
        "InvGate": fetch_and_store_invGate_data,
        "ezofficeinventory": fetch_and_store_ezofficeinventory_data,
        "zoho": zoho_main,
        "zohoHRM": zoho_main,
        "UpKeep": upkeep_main,
        "SuperOps": superops_main,
        "ConnectTeam": connect_team_main,
        "Workable": workableMain,
        "Hector":hectorMain,
    }
    
    if tool not in tool_functions:
        return {"error": f"Unsupported tool: {tool}"}, 400
    
    response, status = tool_functions[tool](organization_id, tool, body)
    return response, status
