from acitoolkit import Credentials, Session, EPG, Port
import logging
import requests

# Define a function for input validation
def validate_input(tenant_name, app_profile_name, epg_name):
    if not tenant_name or not app_profile_name or not epg_name:
        raise ValueError("Tenant name, App Profile name, and EPG name are required.")
    return True

# Define a function for error handling
def handle_error(error):
    print(error)
    logging.error(error)

# Define logging
logging.basicConfig(filename='aci_script.log', level=logging.ERROR)

# Define the Tenant, App Profile, and EPG
tenant_name = 'myTenant'
app_profile_name = 'myAppProfile'
epg_name = 'myEPG'

# Input validation
try:
    validate_input(tenant_name, app_profile_name, epg_name)
except ValueError as e:
    handle_error(str(e))
    exit()

# Fetching the credentials from Thycotic Secret Server
try:
    thycotic_url = "https://your_thycotic_url/api/v1/secrets/{secret_id}/retrieve"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer your_thycotic_access_token',
    }
    thycotic_response = requests.get(thycotic_url, headers=headers)
    thycotic_response.raise_for_status()
    thycotic_secret = thycotic_response.json()
    apic_ip = thycotic_secret['secret']['fields']['APIC IP']
    username = thycotic_secret['secret']['fields']['username']
    password = thycotic_secret['secret']['fields']['password']
except Exception as e:
    handle_error(str(e))
    exit()

# Define credentials
try:
    creds = Credentials(apic_ip, username, password)
except Exception as e:
    handle_error(str(e))
    exit()

# Create a session
try:
    session = Session(creds)
    session.login()
except Exception as e:
    handle_error(str(e))
    exit()

# Get the EPG object
try:
    epg_obj = session.query(EPG).filter(EPG.name == epg_name, EPG.app_profile_name == app_profile_name, EPG.tenant_name == tenant_name).first()
    if not epg_obj:
        raise ValueError("EPG not found.")
except Exception as e:
    handle_error(str(e))
    exit()

# Define the new port name and VLAN
new_port_name = 'newPort1'
new_vlan = '100'

# Create a new Port object
new_port = Port(epg_obj, new_port_name)

# Set the VLAN for the new Port
new_port.vlan = new_vlan

# Push the changes to the APIC
try:
    resp = session.push_to_apic(tenant_name.get_url(), tenant_name.get_json())
    if not resp.ok:
        raise ValueError("Error modifying port in the ACI fabric: {}".format(resp.text))
except Exception as e:
    handle_error(str(e))
    exit()

# Check if the push was successful
print("Successfully modified port in the ACI fabric.")
session.logout()
